"""Digital-twin timeline: totals add up, stages move forward, and each what-if hits only what it should."""
import pytest

from khetplan.optimizer import solve_intercrop
from khetplan.twin import STAGES, WhatIf, build_twin, crop_stage
from khetplan.validation import water_limit_mm


@pytest.fixture(scope="module")
def plan(ds):
    from khetplan.models import FarmInputs

    inputs = FarmInputs(region="buldhana", area_value=2.0, area_unit="acre", season="kharif", year=2027, water="limited", risk=60)
    res = solve_intercrop(inputs, ds)
    assert res.plan is not None and res.plan.feasible
    return res.plan


def test_no_shock_matches_the_plan(plan, ds):
    tw = build_twin(plan, ds)
    expected = sum(a.acres * ds.crops[a.crop_id].gross_per_acre for a in plan.allocations)
    assert tw["totals"]["reference_gross"] == pytest.approx(expected)
    assert tw["totals"]["scenario_gross"] == pytest.approx(expected)
    assert tw["cum_sales"][-1] == pytest.approx(expected, abs=1)
    assert tw["cum_sales"] == tw["ref_cum_sales"]
    assert sum(tw["sales"]) == pytest.approx(expected, abs=1)


def test_weekly_series_have_one_value_per_week(plan, ds):
    tw = build_twin(plan, ds)
    n = len(tw["weeks"])
    for key in ("water_m3", "irrigation_m3", "labour_days", "sales", "cum_sales", "weather"):
        assert len(tw[key]) == n
    for series in tw["stage"] + tw["growth"] + tw["health"]:
        assert len(series) == n
    assert sum(tw["water_m3"]) == pytest.approx(tw["totals"]["water_m3"], abs=0.5)  # weekly values are rounded
    assert all(i <= w for i, w in zip(tw["irrigation_m3"], tw["water_m3"]))
    # every crop's season water is counted in full
    m3 = sum(ds.crops[a.crop_id].crop_water_mm * a.acres * 4.0469 for a in plan.allocations)
    assert tw["totals"]["water_m3"] == pytest.approx(m3, rel=1e-3)


def test_stages_and_growth_only_move_forward(plan, ds):
    tw = build_twin(plan, ds)
    for stages, growth in zip(tw["stage"], tw["growth"]):
        assert stages == sorted(stages)
        assert growth == sorted(growth)
        assert stages[0] == STAGES.index("not_sown") or stages[0] == STAGES.index("germination")
        assert stages[-1] == STAGES.index("done")


def test_crop_stage_boundaries(ds, plan):
    a = plan.allocations[0]
    crop = ds.crops[a.crop_id]
    from datetime import timedelta

    assert crop_stage(crop, a.sow_date, a.harvest_start, a.harvest_end, a.sow_date - timedelta(days=1))[0] == "not_sown"
    assert crop_stage(crop, a.sow_date, a.harvest_start, a.harvest_end, a.harvest_start)[0] == "harvest"
    assert crop_stage(crop, a.sow_date, a.harvest_start, a.harvest_end, a.harvest_end + timedelta(days=1))[0] == "done"


def test_pest_hits_only_the_target_crop(plan, ds):
    target = plan.allocations[0].crop_id
    tw = build_twin(plan, ds, WhatIf(kind="pest", week=6, severity=0.4, crop=target))
    for cid, v in tw["per_crop"].items():
        if cid == target:
            assert v["yield_factor"] == pytest.approx(0.6)
            assert v["scenario"] == pytest.approx(0.6 * v["reference"], rel=1e-6)
        else:
            assert v["scenario"] == pytest.approx(v["reference"])


def test_price_drop_only_changes_sales_after_it_starts(plan, ds):
    base = build_twin(plan, ds)
    wk = 20
    tw = build_twin(plan, ds, WhatIf(kind="price", week=wk, change=-0.3))
    assert tw["sales"][:wk] == base["sales"][:wk]
    for after, before in zip(tw["sales"][wk + 1:], base["sales"][wk + 1:]):
        assert after == pytest.approx(0.7 * before, abs=0.05)
    assert tw["totals"]["scenario_gross"] < base["totals"]["scenario_gross"]


def test_dry_spell_at_flowering_hurts_more_than_late(plan, ds):
    # find a week when the first crop flowers and one when everything is done
    flower = STAGES.index("flowering")
    base = build_twin(plan, ds)
    wk_flower = base["stage"][0].index(flower)
    early = build_twin(plan, ds, WhatIf(kind="dry_spell", week=wk_flower, weeks=2, severity=0.8))
    late = build_twin(plan, ds, WhatIf(kind="dry_spell", week=len(base["weeks"]) - 3, weeks=2, severity=0.8))
    assert early["totals"]["scenario_gross"] < late["totals"]["scenario_gross"] <= base["totals"]["reference_gross"]
    assert "dry" in early["weather"][wk_flower:wk_flower + 2][0]


def test_dry_spell_hurts_rainfed_more_than_irrigated(ds, farm):
    wi = WhatIf(kind="dry_spell", week=8, weeks=3, severity=0.8)
    losses = {}
    for water in ("rainfed", "assured"):
        p = solve_intercrop(farm(water=water), ds).plan
        tw = build_twin(p, ds, wi)
        losses[water] = 1 - tw["totals"]["scenario_gross"] / tw["totals"]["reference_gross"]
    assert losses["rainfed"] > losses["assured"]


def test_water_cut_cuts_irrigated_crops_and_replan_fits(plan, ds):
    tw = build_twin(plan, ds, WhatIf(kind="water_cut", week=4, water="rainfed"))
    irrigated = [a.crop_id for a in plan.allocations if ds.crops[a.crop_id].irrigation_mm > 0]
    assert irrigated, "this fixture should include an irrigated crop"
    for cid, v in tw["per_crop"].items():
        if cid in irrigated:
            assert v["yield_factor"] < 1
        else:
            assert v["yield_factor"] == 1
    # re-planning for the lower water level gives a valid plan inside the new limit
    from dataclasses import replace

    res = solve_intercrop(replace(plan.inputs, water="rainfed"), ds)
    assert res.plan.feasible and res.plan.water_used_mm <= water_limit_mm(ds, "rainfed")


def test_events_include_the_shock_and_every_sowing(plan, ds):
    tw = build_twin(plan, ds, WhatIf(kind="dry_spell", week=9))
    keys = [(e["key"], e["crop"]) for e in tw["events"]]
    for a in plan.allocations:
        assert ("ev_sow", a.crop_id) in keys and ("ev_harvest", a.crop_id) in keys
    assert any(e["key"] == "ev_dry_spell" and e["week"] == 9 for e in tw["events"])
    assert [e["week"] for e in tw["events"]] == sorted(e["week"] for e in tw["events"])


def test_twin_is_json_ready_and_deterministic(plan, ds):
    import json

    a = json.dumps(build_twin(plan, ds, WhatIf(kind="pest", week=5, crop=plan.crop_ids[-1])), sort_keys=True)
    b = json.dumps(build_twin(plan, ds, WhatIf(kind="pest", week=5, crop=plan.crop_ids[-1])), sort_keys=True)
    assert a == b
