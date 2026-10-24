import copy

from khetplan.optimizer import solve_intercrop
from khetplan.validation import validate_plan


def _plan(ds, farm, **kw):
    return solve_intercrop(farm(**kw), ds).plan


def test_valid_plan_has_no_violations(ds, farm):
    assert validate_plan(_plan(ds, farm), ds) == []


def test_detects_area_mismatch(ds, farm):
    p = copy.deepcopy(_plan(ds, farm))
    p.allocations[0].acres += 0.01
    assert any("Allocated area" in v for v in validate_plan(p, ds))


def test_detects_unsupported_pair(ds, farm):
    p = copy.deepcopy(_plan(ds, farm))
    assert not ds.compatible("soybean", "sesame", "kharif")
    rename = dict(zip(p.crop_ids[:2], ["soybean", "sesame"]))
    for a in p.allocations[:2]:
        a.crop_id = rename[a.crop_id]
    p.strip_order = [rename.get(c, c) for c in p.strip_order]
    assert any("soybean + sesame" in v or "sesame + soybean" in v for v in validate_plan(p, ds))


def test_detects_water_violation(ds, farm):
    p = copy.deepcopy(_plan(ds, farm, water="assured", risk=0))
    p.inputs.water = "rainfed"
    assert any("Irrigation need" in v for v in validate_plan(p, ds))


def test_detects_excluded_and_wrong_season(ds, farm):
    p = copy.deepcopy(_plan(ds, farm))
    p.inputs.excluded_crops = (p.crop_ids[0],)
    assert any("excluded" in v for v in validate_plan(p, ds))
    p.inputs.excluded_crops = ()
    p.inputs.season = "rabi"
    assert any("not available" in v for v in validate_plan(p, ds))


def test_detects_share_outside_limits_and_map_mismatch(ds, farm):
    p = copy.deepcopy(_plan(ds, farm))
    a, b = p.allocations[0], p.allocations[1]
    move = b.strips - 1  # leave b with 1 strip (5%), below the 15% minimum
    a.strips += move
    b.strips -= move
    a.acres, b.acres = a.strips / 20 * p.inputs.acres, b.strips / 20 * p.inputs.acres
    v = validate_plan(p, ds)
    assert any("outside" in x for x in v)
    assert any("Bed map" in x for x in v)


def test_detects_budget_violation(ds, farm):
    p = copy.deepcopy(_plan(ds, farm))
    p.inputs.budget_rs = 10
    assert any("exceeds budget" in v for v in validate_plan(p, ds))
