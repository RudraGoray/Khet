import copy

import numpy as np
import pytest

from khetplan.export import verdict
from khetplan.optimizer import monoculture_candidates, solve_intercrop
from khetplan.simulation import Outcome, compare, draw_scenarios, run_comparison, simulate_plan, summarize


@pytest.fixture
def setup(ds, farm):
    inp = farm(risk=80)
    plan = solve_intercrop(inp, ds).plan
    base = monoculture_candidates(inp, ds)[0]
    return plan, base


def test_reproducible_with_same_seed(ds, setup):
    plan, base = setup
    a = run_comparison(plan, base, ds, seed=7)
    b = run_comparison(plan, base, ds, seed=7)
    assert np.array_equal(a["mixed"].net, b["mixed"].net)
    assert a["stats_mixed"]["p10_net"] == b["stats_mixed"]["p10_net"]
    c = run_comparison(plan, base, ds, seed=8)
    assert not np.array_equal(a["mixed"].net, c["mixed"].net)


def test_default_is_1000_seasons(ds, setup):
    assert run_comparison(*setup, ds)["seasons"] == 1000


def test_common_random_numbers(ds, setup):
    """Both plans see the same draws: a crop's per-acre revenue is identical in both."""
    plan, base = setup
    sc = draw_scenarios(ds, "kharif", "buldhana", seed=3)
    crop = base.crop_ids[0]
    plan_copy = copy.deepcopy(base)
    out1 = simulate_plan(base, ds, sc)
    out2 = simulate_plan(plan_copy, ds, sc)
    assert np.array_equal(out1.gross, out2.gross)
    col = sc.gross_per_acre[:, sc.column(crop)]
    assert np.allclose(out1.gross, col * base.inputs.acres)
    # Adding a crop to the dataset order must not change draws for other crops is guaranteed by the
    # fixed sorted draw order; identical plans compared against each other differ by exactly zero.
    cmp = compare(out1, out2)
    assert cmp["mean_diff_net"] == 0 and cmp["share_a_better"] == 0


def test_profit_is_gross_minus_cost_and_months_add_up(ds, setup):
    plan, base = setup
    sc = draw_scenarios(ds, "kharif", "buldhana")
    out = simulate_plan(plan, ds, sc)
    expected_cost = sum(ds.crops[a.crop_id].cost_rs_per_acre * a.acres for a in plan.allocations)
    assert out.cost == pytest.approx(expected_cost)
    assert np.allclose(out.net, out.gross - expected_cost)
    assert np.allclose(out.monthly_gross.sum(axis=1), out.gross)
    assert (out.gross >= 0).all()


def test_metric_definitions_on_known_values():
    gross = np.array([0.0, 100.0, 200.0, 300.0, 400.0])
    monthly = np.zeros((5, 12))
    monthly[:, 5] = gross
    out = Outcome("x", gross, 100.0, gross - 100.0, monthly)
    s = summarize(out)
    assert s["mean_gross"] == 200 and s["mean_net"] == 100
    assert s["p10_net"] == pytest.approx(np.percentile(gross - 100, 10))  # -60 by linear interpolation
    assert s["p10_net"] == pytest.approx(-60)
    assert s["sd_net"] == pytest.approx(np.std(gross))
    assert s["cv_net"] == pytest.approx(np.std(gross) / 100)
    assert s["prob_loss"] == pytest.approx(0.2)
    # 11 empty months each season, plus month 5 empty in the zero-revenue season
    assert s["mean_zero_income_months"] == pytest.approx((11 * 5 + 1) / 5)


def test_cv_undefined_when_mean_is_zero():
    gross = np.array([50.0, 150.0])
    out = Outcome("x", gross, 100.0, gross - 100.0, np.zeros((2, 12)))
    assert summarize(out)["cv_net"] is None


def test_diversification_is_not_forced_to_win(ds, farm):
    """With these synthetic numbers the cautious mixed plan earns LESS on average than the best
    single crop. The comparison must report that, not hide it."""
    inp = farm(risk=80)
    comp = run_comparison(solve_intercrop(inp, ds).plan, monoculture_candidates(inp, ds)[0], ds)
    assert comp["cmp"]["mean_diff_net"] < 0
    assert comp["stats_mixed"]["mean_net"] < comp["stats_single"]["mean_net"]
    assert " less." in verdict(comp, ds, "en")


def test_baseline_must_share_inputs(ds, farm, setup):
    plan, _ = setup
    other = monoculture_candidates(farm(area_value=3), ds)[0]
    with pytest.raises(ValueError):
        run_comparison(plan, other, ds)
