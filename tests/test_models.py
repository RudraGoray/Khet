from datetime import date

import pytest

from khetplan.models import check_inputs, default_year, to_acres


def test_unit_conversion():
    assert to_acres(40, "guntha") == pytest.approx(1.0)
    assert to_acres(1, "hectare") == pytest.approx(2.4710538)
    with pytest.raises(ValueError):
        to_acres(1, "bigha")
    with pytest.raises(ValueError):
        to_acres(0, "acre")


def test_missing_and_unsupported_inputs(ds, farm):
    assert check_inputs(farm(), ds) == []
    fields = {p[0] for p in check_inputs(farm(region=None, area_value=None, season=None, water=None), ds)}
    assert fields == {"region", "area", "season", "water"}
    assert check_inputs(farm(region="other"), ds)[0][1] == "err_region_unsupported"
    assert check_inputs(farm(season="zaid"), ds)[0][1] == "err_season_unsupported"
    assert check_inputs(farm(area_value=80), ds)[0][1] == "err_area_range"
    assert check_inputs(farm(area_value=2, area_unit="guntha"), ds)[0][1] == "err_area_range"  # 0.05 acre
    assert check_inputs(farm(budget_rs=-1), ds)[0][1] == "err_budget"


def test_default_year_picks_next_open_season():
    assert default_year("kharif", date(2026, 10, 24)) == 2027
    assert default_year("rabi", date(2026, 10, 24)) == 2027
    assert default_year("rabi", date(2026, 9, 1)) == 2026
    assert default_year("kharif", date(2027, 3, 1)) == 2027
