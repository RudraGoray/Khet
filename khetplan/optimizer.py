"""Crop allocation with Google OR-Tools CP-SAT.

The plot is divided into equal strips (default 20, so shares move in 5% steps).
Hard constraints never depend on the risk slider; the slider only changes objective weights.

The objective blends expected net margin with CVaR10 (the average of the worst 10% of
optimisation seasons). Each allowed crop combination is solved as its own small CP-SAT
model and the best is kept; this keeps solves fast and deterministic on one worker.
"""
from __future__ import annotations

import math
from itertools import combinations

from ortools.sat.python import cp_model

from .models import Allocation, Plan, SolveResult, check_inputs
from .schedule import crop_dates, harvest_months
from .simulation import crop_risk_stats, draw_scenarios
from .validation import validate_plan, water_limit_mm

STATUS_NAMES = {
    cp_model.OPTIMAL: "OPTIMAL",
    cp_model.FEASIBLE: "FEASIBLE",
    cp_model.INFEASIBLE: "INFEASIBLE",
    cp_model.UNKNOWN: "TIMEOUT",
    cp_model.MODEL_INVALID: "ERROR",
}


OPT_SCENARIOS = 150  # in-sample seasons used inside the optimizer
CVAR_ALPHA = 0.10  # downside measure: average net margin of the worst 10% of seasons
OBJ_RESOLUTION = 1000  # largest per-strip scenario margin is scaled to about this many integer units
OPT_SEED_OFFSET = 1  # optimizer draws differ from the comparison draws (no in-sample flattery)


def risk_weight(risk: int) -> float:
    """Objective = (1 - w) * expected net margin + w * CVaR10 of net margin."""
    return risk / 100


def interleave(counts: dict, strips: int) -> list:
    """Spread each crop's strips evenly across the plot, e.g. A B A A B A ..."""
    slots = []
    for cid, k in counts.items():
        for i in range(k):
            slots.append(((i + 0.5) * strips / k, cid))
    slots.sort()
    return [cid for _, cid in slots]


def candidate_pool(inputs, dataset) -> tuple:
    """Crops the farmer could grow here, plus explanation entries for those removed."""
    notes = []
    pool = []
    for c in dataset.crops_for(inputs.region, inputs.season):
        if c.id in inputs.excluded_crops:
            notes.append({"key": "exp_farmer_excluded", "crops": [c.id]})
        else:
            pool.append(c)
    unsupported = [e.id for e in dataset.excluded.values() if e.region == inputs.region and e.season == inputs.season]
    if unsupported:
        notes.append({"key": "exp_dataset_excluded", "crops": unsupported})
    return pool, notes


def _build_plan(inputs, dataset, counts: dict, kind: str, status: str, objective: float) -> Plan:
    strips = dataset.sim["strips"]
    total = inputs.acres
    allocations = []
    for cid, k in counts.items():
        crop = dataset.crops[cid]
        sow, start, end = crop_dates(crop, inputs.year)
        allocations.append(Allocation(cid, k, total * k / strips, k / strips, sow, start, end))
    allocations.sort(key=lambda a: -a.strips)
    plan = Plan(
        inputs=inputs,
        allocations=allocations,
        strip_order=interleave({a.crop_id: a.strips for a in allocations}, strips),
        status=status,
        kind=kind,
        objective=objective,
        water_limit_mm=water_limit_mm(dataset, inputs.water),
    )
    plan.water_used_mm = sum(dataset.crops[a.crop_id].irrigation_mm * a.share for a in allocations)
    plan.cost_rs = sum(dataset.crops[a.crop_id].cost_rs_per_acre * a.acres for a in allocations)
    plan.violations = validate_plan(plan, dataset)
    return plan


class _Objective:
    """Scenario margins shared by every sub-model, on one integer scale so objectives compare."""

    def __init__(self, inputs, dataset, pool, stats, scenarios):
        strips = dataset.sim["strips"]
        acres = inputs.acres
        self.k = max(1, round(CVAR_ALPHA * scenarios.seasons))
        self.seasons = scenarios.seasons
        cols = {c.id: (scenarios.gross_per_acre[:, scenarios.column(c.id)] - c.cost_rs_per_acre) * acres / strips for c in pool}
        # Small integer domains keep CP-SAT fast; ~0.1% rounding does not change rankings materially.
        self.unit = max(1.0, max(float(abs(v).max()) for v in cols.values()) / OBJ_RESOLUTION)
        self.per_strip = {cid: [round(v / self.unit) for v in col] for cid, col in cols.items()}
        self.bound = strips * max(max(abs(v) for v in vals) for vals in self.per_strip.values()) + 1
        # Harvest-spread preference in rupees per month that has some harvest income.
        bonus_rs = inputs.risk / 100 * dataset.sim["harvest_spread_bonus"] * acres * max(s[0] for s in stats.values())
        self.month_bonus = round(self.seasons * self.k * 100 * bonus_rs / self.unit)

    def scale(self) -> float:
        """Divide a model objective by this to get rupees."""
        return self.seasons * self.k * 100 / self.unit


def _model(inputs, dataset, crops, objective=None, use_water=True, use_budget=True, use_shares=True):
    """CP-SAT model in which every crop in `crops` is used. Returns (model, strip vars)."""
    strips = dataset.sim["strips"]
    acres = inputs.acres
    m = cp_model.CpModel()
    n = {}
    for c in crops:
        lo = math.ceil(c.min_share * strips - 1e-9) if use_shares else 1
        hi = math.floor(c.max_share * strips + 1e-9) if use_shares else strips
        n[c.id] = m.NewIntVar(lo, hi, f"n_{c.id}")
    m.Add(sum(n.values()) == strips)
    if use_water:
        # Average irrigation depth over the plot: sum(irr_c * n_c) / strips <= limit (exact integers).
        limit = int(dataset.sim["water_levels_mm"][inputs.water])
        m.Add(sum(c.irrigation_mm * n[c.id] for c in crops) <= limit * strips)
    if use_budget and inputs.budget_rs is not None:
        # Paise, rounding cost up and budget down so the solver is never looser than the validator.
        cost = {c.id: math.ceil(c.cost_rs_per_acre * acres / strips * 100) for c in crops}
        m.Add(sum(cost[c.id] * n[c.id] for c in crops) <= math.floor(inputs.budget_rs * 100))
    if objective is None:
        return m, n

    ob, w = objective, inputs.risk  # w is an integer 0..100
    xs = []
    for s in range(ob.seasons):
        x = m.NewIntVar(-ob.bound, ob.bound, f"x_{s}")
        m.Add(x == sum(ob.per_strip[c.id][s] * n[c.id] for c in crops))
        xs.append(x)
    terms = [(100 - w) * ob.k * x for x in xs]  # = (100 - w) * k * S * mean
    if w > 0:
        eta = m.NewIntVar(-ob.bound, ob.bound, "eta")
        shortfalls = []
        for x in xs:
            u = m.NewIntVar(0, 2 * ob.bound, f"u_{len(shortfalls)}")
            m.Add(u >= eta - x)
            shortfalls.append(u)
        # CVaR = eta - sum(u) / k, so w * k * S * CVaR = w * S * (k * eta - sum(u)).
        terms.append(w * ob.seasons * (ob.k * eta - sum(shortfalls)))
    months = set()
    for c in crops:
        months |= harvest_months(c, inputs.year, inputs.season)
    m.Maximize(sum(terms) + ob.month_bonus * len(months))
    return m, n


def _run(model, time_limit, seed):
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.random_seed = seed
    solver.parameters.num_search_workers = 1  # deterministic
    status = solver.Solve(model)
    return solver, STATUS_NAMES.get(status, "ERROR")


def crop_sets(pool, dataset, season, use_pairs=True) -> list:
    """Every combination of 2..max_crops crops in which each pair is supported."""
    sets = []
    for size in range(2, dataset.sim["max_crops"] + 1):
        for combo in combinations(pool, size):
            if not use_pairs or all(dataset.compatible(a.id, b.id, season) for a, b in combinations(combo, 2)):
                sets.append(combo)
    return sets


def _any_feasible(inputs, dataset, sets, time_limit, seed, **rules) -> bool:
    for combo in sets:
        model, _ = _model(inputs, dataset, combo, **rules)
        if _run(model, time_limit, seed)[1] in ("OPTIMAL", "FEASIBLE"):
            return True
    return False


def solve_intercrop(inputs, dataset, time_limit: float = 10.0, seed: int = 0) -> SolveResult:
    """time_limit is the total CP-SAT budget in seconds, shared across crop combinations."""
    problems = check_inputs(inputs, dataset)
    if problems:
        return SolveResult("INVALID_INPUT", reasons=[{"key": p[1], "field": p[0], "detail": p[2]} for p in problems])

    pool, notes = candidate_pool(inputs, dataset)
    if len(pool) < 2:
        return SolveResult("INFEASIBLE", reasons=notes + [{"key": "diag_too_few_crops", "count": len(pool)}])
    sets = crop_sets(pool, dataset, inputs.season)
    if not sets:
        return SolveResult("INFEASIBLE", reasons=notes + [{"key": "diag_infeasible"}, {"key": "diag_lift_pairs"}])

    stats = crop_risk_stats(dataset, inputs.season, inputs.region)
    opt_sc = draw_scenarios(dataset, inputs.season, inputs.region, seasons=OPT_SCENARIOS,
                            seed=dataset.sim["seed"] + OPT_SEED_OFFSET)
    best, statuses = None, []
    try:
        objective = _Objective(inputs, dataset, pool, stats, opt_sc)
        per_set = max(0.05, time_limit / len(sets))
        for combo in sets:
            model, n = _model(inputs, dataset, combo, objective)
            solver, status = _run(model, per_set, seed)
            statuses.append(status)
            if status in ("OPTIMAL", "FEASIBLE"):
                value = solver.ObjectiveValue()
                if best is None or value > best[0] + 1e-9:  # ties keep the earlier, deterministic set
                    best = (value, {cid: solver.Value(v) for cid, v in n.items()})
    except Exception as exc:  # a solver crash must not look like a plan
        return SolveResult("ERROR", reasons=[{"key": "diag_error", "detail": str(exc)}])

    if best is None:
        if "TIMEOUT" in statuses:
            return SolveResult("TIMEOUT", reasons=notes + [{"key": "diag_timeout"}])
        return SolveResult("INFEASIBLE", reasons=notes + diagnose(inputs, dataset, pool, time_limit, seed))

    # OPTIMAL only if every combination was either solved to optimality or proven infeasible.
    status = "OPTIMAL" if all(s in ("OPTIMAL", "INFEASIBLE") for s in statuses) else "FEASIBLE"
    plan = _build_plan(inputs, dataset, best[1], "intercrop", status, best[0] / objective.scale())
    if plan.violations:
        return SolveResult("ERROR", reasons=[{"key": "diag_validation", "detail": "; ".join(plan.violations)}])
    plan.explanation = notes + explain(plan, dataset, pool, stats)
    return SolveResult(status, plan=plan)


def diagnose(inputs, dataset, pool, time_limit, seed) -> list:
    """Find which single rule, if lifted, would allow a plan. Nothing is relaxed automatically."""
    reasons = [{"key": "diag_infeasible"}]
    limit = max(0.05, time_limit / 20)
    checks = [("water", dict(use_water=False)), ("shares", dict(use_shares=False))]
    if inputs.budget_rs is not None:
        checks.insert(1, ("budget", dict(use_budget=False)))
    sets = crop_sets(pool, dataset, inputs.season)
    for name, rules in checks:
        if _any_feasible(inputs, dataset, sets, limit, seed, **rules):
            reasons.append({"key": f"diag_lift_{name}"})
    if _any_feasible(inputs, dataset, crop_sets(pool, dataset, inputs.season, use_pairs=False), limit, seed):
        reasons.append({"key": "diag_lift_pairs"})
    if len(reasons) == 1:
        reasons.append({"key": "diag_multiple"})
    return reasons


def explain(plan, dataset, pool, stats) -> list:
    inp = plan.inputs
    strips = dataset.sim["strips"]
    out = [{"key": "exp_objective", "risk": inp.risk, "weight": risk_weight(inp.risk)}]
    out.append({"key": "exp_area", "acres": inp.acres, "strips": strips, "strip_acres": inp.acres / strips})
    binding_water = plan.water_limit_mm - plan.water_used_mm < (min((c.irrigation_mm for c in pool if c.irrigation_mm > 0), default=0) / strips)
    out.append({"key": "exp_water", "used": plan.water_used_mm, "limit": plan.water_limit_mm, "level": inp.water, "binding": binding_water})
    thirsty = [c.id for c in pool if c.irrigation_mm > plan.water_limit_mm]
    if thirsty:
        out.append({"key": "exp_water_limits", "crops": thirsty})
    if inp.budget_rs is not None:
        out.append({"key": "exp_budget", "cost": plan.cost_rs, "budget": inp.budget_rs})
    out.append({"key": "exp_pairs", "crops": plan.crop_ids})
    for a in plan.allocations:
        c = dataset.crops[a.crop_id]
        at_cap = a.strips == math.floor(c.max_share * strips + 1e-9)
        at_floor = a.strips == math.ceil(c.min_share * strips - 1e-9)
        out.append({
            "key": "exp_crop", "crops": [a.crop_id], "share": a.share,
            "mean": stats[a.crop_id][0], "sd": stats[a.crop_id][1],
            "limit": "max" if at_cap else ("min" if at_floor else ""),
        })
    out.append({"key": "exp_shares", "min": min(c.min_share for c in pool), "max": max(c.max_share for c in pool), "max_crops": dataset.sim["max_crops"]})
    return out


def monoculture_candidates(inputs, dataset) -> list:
    """Valid single-crop plans under the same physical rules (region, season, water, budget,
    farmer exclusions). Sorted best expected net margin first, so the baseline is a strong one."""
    if check_inputs(inputs, dataset):
        return []
    pool, _ = candidate_pool(inputs, dataset)
    stats = crop_risk_stats(dataset, inputs.season, inputs.region)
    plans = []
    for c in pool:
        plan = _build_plan(inputs, dataset, {c.id: dataset.sim["strips"]}, "monoculture", "BASELINE", 0.0)
        if not plan.violations:
            plans.append((stats[c.id][0], plan))
    plans.sort(key=lambda t: -t[0])
    return [p for _, p in plans]
