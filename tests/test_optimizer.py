import math
from itertools import combinations

import pytest

from khetplan import optimizer
from khetplan.optimizer import crop_sets, interleave, monoculture_candidates, solve_intercrop
from khetplan.validation import validate_plan

GRID = [
    (season, water, risk, acres)
    for season in ("kharif", "rabi")
    for water in ("rainfed", "limited", "assured")
    for risk in (0, 50, 100)
    for acres in (0.5, 7.0)
]


def assert_hard_constraints(plan, ds):
    inp = plan.inputs
    strips = ds.sim["strips"]
    assert sum(a.acres for a in plan.allocations) == pytest.approx(inp.acres, abs=1e-9)
    assert sum(a.strips for a in plan.allocations) == strips
    assert 2 <= len(plan.allocations) <= ds.sim["max_crops"]
    for a in plan.allocations:
        c = ds.crops[a.crop_id]
        assert (c.region, c.season) == (inp.region, inp.season)
        assert math.ceil(c.min_share * strips - 1e-9) <= a.strips <= math.floor(c.max_share * strips + 1e-9)
        assert a.crop_id not in inp.excluded_crops
    for x, y in combinations(plan.crop_ids, 2):
        assert ds.compatible(x, y, inp.season)
    water = sum(ds.crops[a.crop_id].irrigation_mm * a.acres for a in plan.allocations) / inp.acres
    assert water <= ds.sim["water_levels_mm"][inp.water] + 1e-9
    if inp.budget_rs is not None:
        assert plan.cost_rs <= inp.budget_rs + 1e-6


@pytest.mark.parametrize("season,water,risk,acres", GRID)
def test_every_plan_satisfies_hard_constraints_at_every_risk(ds, farm, season, water, risk, acres):
    res = solve_intercrop(farm(season=season, water=water, risk=risk, area_value=acres), ds)
    assert res.status == "OPTIMAL"
    assert_hard_constraints(res.plan, ds)
    assert validate_plan(res.plan, ds) == []


def test_rainfed_excludes_irrigated_crops(ds, farm):
    for risk in (0, 100):
        plan = solve_intercrop(farm(water="rainfed", risk=risk), ds).plan
        assert "cotton" not in plan.crop_ids and plan.water_used_mm == 0


def test_water_limit_binds_with_limited_irrigation(ds, farm):
    plan = solve_intercrop(farm(season="rabi", water="limited", risk=100), ds).plan
    assert plan.water_used_mm <= 75
    assert "wheat" in plan.crop_ids or "mustard" in plan.crop_ids


def test_risk_slider_changes_choice_but_not_rules(ds, farm):
    low = solve_intercrop(farm(risk=0), ds).plan
    high = solve_intercrop(farm(risk=100), ds).plan
    assert {a.crop_id: a.strips for a in low.allocations} != {a.crop_id: a.strips for a in high.allocations}
    for p in (low, high):
        assert_hard_constraints(p, ds)


def test_deterministic(ds, farm):
    a = solve_intercrop(farm(risk=40), ds).plan
    b = solve_intercrop(farm(risk=40), ds).plan
    assert [(x.crop_id, x.strips) for x in a.allocations] == [(x.crop_id, x.strips) for x in b.allocations]
    assert a.strip_order == b.strip_order


def test_budget_is_respected(ds, farm):
    res = solve_intercrop(farm(water="assured", budget_rs=30000, area_value=2), ds)
    assert res.plan.cost_rs <= 30000
    assert_hard_constraints(res.plan, ds)


def test_infeasible_budget_is_reported_with_diagnosis(ds, farm):
    res = solve_intercrop(farm(budget_rs=5000), ds)
    assert res.status == "INFEASIBLE" and res.plan is None
    keys = [r["key"] for r in res.reasons]
    assert "diag_infeasible" in keys and "diag_lift_budget" in keys


def test_infeasible_water_is_reported(ds, farm):
    # Rainfed rabi without chickpea and safflower leaves only pairs that need irrigation.
    res = solve_intercrop(farm(season="rabi", water="rainfed", excluded_crops=("chickpea", "safflower")), ds)
    assert res.status == "INFEASIBLE"
    assert "diag_lift_water" in [r["key"] for r in res.reasons]


def test_too_few_crops(ds, farm):
    keep = "pigeonpea"
    excluded = tuple(c.id for c in ds.crops_for("buldhana", "kharif") if c.id != keep)
    res = solve_intercrop(farm(excluded_crops=excluded), ds)
    assert res.status == "INFEASIBLE"
    assert any(r["key"] == "diag_too_few_crops" for r in res.reasons)


def test_invalid_input_is_not_solved(ds, farm):
    res = solve_intercrop(farm(region="other", water=None), ds)
    assert res.status == "INVALID_INPUT" and res.plan is None
    assert {r["field"] for r in res.reasons} == {"region", "water"}


def test_timeout_is_distinct(ds, farm, monkeypatch):
    monkeypatch.setattr(optimizer, "_run", lambda model, tl, seed: (None, "TIMEOUT"))
    res = solve_intercrop(farm(), ds)
    assert res.status == "TIMEOUT" and res.plan is None


def test_solver_crash_is_an_error_not_a_plan(ds, farm, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("solver exploded")
    monkeypatch.setattr(optimizer, "_run", boom)
    res = solve_intercrop(farm(), ds)
    assert res.status == "ERROR" and res.plan is None


def test_plan_failing_independent_validation_is_never_shown(ds, farm, monkeypatch):
    monkeypatch.setattr(optimizer, "validate_plan", lambda plan, ds: ["forced failure"])
    res = solve_intercrop(farm(), ds)
    assert res.status == "ERROR" and res.plan is None
    assert "forced failure" in res.reasons[0]["detail"]


def test_crop_sets_respect_pairs(ds):
    pool = ds.crops_for("buldhana", "kharif")
    for combo in crop_sets(pool, ds, "kharif"):
        for a, b in combinations(combo, 2):
            assert ds.compatible(a.id, b.id, "kharif")


def test_interleave_keeps_counts():
    order = interleave({"a": 11, "b": 6, "c": 3}, 20)
    assert len(order) == 20 and order.count("a") == 11 and order.count("c") == 3


def test_monoculture_baselines_are_valid_and_obey_water(ds, farm):
    rainfed = monoculture_candidates(farm(water="rainfed"), ds)
    assert rainfed and all(validate_plan(p, ds) == [] for p in rainfed)
    assert "cotton" not in [p.crop_ids[0] for p in rainfed]
    assert "cotton" in [p.crop_ids[0] for p in monoculture_candidates(farm(water="assured"), ds)]
    assert monoculture_candidates(farm(budget_rs=1000), ds) == []
