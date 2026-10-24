"""Monte Carlo season simulation with common random numbers for fair plan comparison.

Every random parameter comes from data/simulation_config.json and crops.csv and is a
prototype assumption (A1). Results are illustrative, not forecasts.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .schedule import harvest_month_weights

ZERO_TOL = 1e-6


def _mean_one_lognormal(rng, cv: float, size) -> np.ndarray:
    """Lognormal multiplier with mean 1 and the given coefficient of variation."""
    if cv <= 0:
        return np.ones(size)
    sigma = np.sqrt(np.log1p(cv**2))
    return np.exp(-0.5 * sigma**2 + sigma * rng.standard_normal(size))


@dataclass
class Scenarios:
    """Shared random draws for one season type. Column j belongs to crop_ids[j]."""

    crop_ids: list
    weather_state: np.ndarray  # (S,) index into config weather_states
    gross_per_acre: np.ndarray  # (S, C) INR per acre, after weather, noise and failure
    failed: np.ndarray  # (S, C) bool
    seed: int

    @property
    def seasons(self) -> int:
        return len(self.weather_state)

    def column(self, crop_id: str) -> int:
        return self.crop_ids.index(crop_id)


def draw_scenarios(dataset, season: str, region: str, seasons: int | None = None, seed: int | None = None) -> Scenarios:
    cfg = dataset.sim
    seasons = seasons or cfg["seasons"]
    seed = cfg["seed"] if seed is None else seed
    crops = sorted(dataset.crops_for(region, season), key=lambda c: c.id)
    rng = np.random.default_rng(seed)
    n = len(crops)

    states = cfg["weather_states"]
    weather = rng.choice(len(states), size=seasons, p=[s["probability"] for s in states])
    severity = np.array([s["severity"] for s in states])[weather]
    market = _mean_one_lognormal(rng, cfg["market_price_cv"], seasons)

    gross = np.zeros((seasons, n))
    failed = np.zeros((seasons, n), dtype=bool)
    for j, c in enumerate(crops):
        # Draw order is fixed per crop (sorted ids), so any plan sees identical draws for a crop.
        y_noise = _mean_one_lognormal(rng, c.yield_cv, seasons)
        p_noise = _mean_one_lognormal(rng, c.price_cv, seasons)
        fail = rng.random(seasons) < c.failure_prob
        weather_factor = np.clip(1 - severity * c.drought_sensitivity, 0, 1)
        yield_q = c.yield_q_per_acre * y_noise * weather_factor * (~fail)
        price = c.price_rs_per_q * p_noise * market
        gross[:, j] = yield_q * price
        failed[:, j] = fail
    return Scenarios([c.id for c in crops], weather, gross, failed, seed)


@dataclass
class Outcome:
    label: str
    gross: np.ndarray  # (S,) seasonal gross revenue, INR
    cost: float  # deterministic direct cash cost, INR
    net: np.ndarray  # (S,) gross minus direct cost, INR
    monthly_gross: np.ndarray  # (S, 12) gross revenue by horizon month


def simulate_plan(plan, dataset, scenarios: Scenarios) -> Outcome:
    season, year = plan.inputs.season, plan.inputs.year
    s = scenarios.seasons
    gross = np.zeros(s)
    monthly = np.zeros((s, 12))
    cost = 0.0
    for a in plan.allocations:
        crop = dataset.crops[a.crop_id]
        g = scenarios.gross_per_acre[:, scenarios.column(a.crop_id)] * a.acres
        gross += g
        monthly += np.outer(g, harvest_month_weights(crop, year, season))
        cost += crop.cost_rs_per_acre * a.acres
    return Outcome(plan.kind, gross, cost, gross - cost, monthly)


def summarize(outcome: Outcome) -> dict:
    net, gross = outcome.net, outcome.gross
    mean_net = float(net.mean())
    sd_net = float(net.std(ddof=0))
    zero_months = (outcome.monthly_gross < ZERO_TOL).sum(axis=1)
    return {
        "mean_gross": float(gross.mean()),
        "mean_net": mean_net,
        "sd_net": sd_net,
        # CV is undefined when mean net is near zero; report None instead of a huge number.
        "cv_net": None if abs(mean_net) < 1.0 else sd_net / abs(mean_net),
        "p10_net": float(np.percentile(net, 10)),
        "p10_gross": float(np.percentile(gross, 10)),
        "p90_net": float(np.percentile(net, 90)),
        "prob_loss": float((net < 0).mean()),
        "mean_zero_income_months": float(zero_months.mean()),
        "cost": outcome.cost,
        "monthly_mean_gross": outcome.monthly_gross.mean(axis=0),
        "monthly_p10_gross": np.percentile(outcome.monthly_gross, 10, axis=0),
        "monthly_p90_gross": np.percentile(outcome.monthly_gross, 90, axis=0),
    }


def compare(a: Outcome, b: Outcome) -> dict:
    """Paired comparison: the same simulated season is used for both plans."""
    diff = a.net - b.net
    return {
        "mean_diff_net": float(diff.mean()),
        "p10_diff_net": float(np.percentile(diff, 10)),
        "share_a_better": float((diff > 0).mean()),
        "diff": diff,
    }


def crop_risk_stats(dataset, season: str, region: str) -> dict:
    """Per-acre net margin mean and SD for each crop, from the configured simulation draws.

    The optimizer uses these as a linear risk proxy; they come from the same model the
    comparison uses, so the plan and the comparison stay consistent.
    """
    sc = draw_scenarios(dataset, season, region)
    stats = {}
    for cid in sc.crop_ids:
        net = sc.gross_per_acre[:, sc.column(cid)] - dataset.crops[cid].cost_rs_per_acre
        stats[cid] = (float(net.mean()), float(net.std(ddof=0)))
    return stats


def run_comparison(plan, baseline, dataset, seasons: int | None = None, seed: int | None = None) -> dict:
    """Simulate the mixed plan and a monoculture baseline on identical seasons."""
    inp = plan.inputs
    if baseline.inputs.key() != inp.key():
        raise ValueError("Plan and baseline were built from different farm inputs")
    sc = draw_scenarios(dataset, inp.season, inp.region, seasons=seasons, seed=seed)
    mixed, single = simulate_plan(plan, dataset, sc), simulate_plan(baseline, dataset, sc)
    return {
        "seasons": sc.seasons,
        "seed": sc.seed,
        "baseline": baseline.crop_ids[0],
        "mixed": mixed,
        "single": single,
        "stats_mixed": summarize(mixed),
        "stats_single": summarize(single),
        "cmp": compare(mixed, single),
    }
