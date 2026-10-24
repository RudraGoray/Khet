import json

from khetplan.export import metric_rows, plan_json, summary_html
from khetplan.i18n import T, fmt_rs, t
from khetplan.optimizer import monoculture_candidates, solve_intercrop
from khetplan.simulation import run_comparison


def _comp(ds, farm, **kw):
    inp = farm(**kw)
    plan = solve_intercrop(inp, ds).plan
    return plan, run_comparison(plan, monoculture_candidates(inp, ds)[0], ds)


def test_summary_reflects_the_computed_plan_and_simulation(ds, farm):
    plan, comp = _comp(ds, farm, water="limited", risk=60)
    doc = summary_html(plan, ds, "en", comp, embed_font=False)
    for a in plan.allocations:
        assert ds.crops[a.crop_id].name("en") in doc
        assert f"{a.share:.0%}" in doc and f"{a.acres:.2f}" in doc
        assert a.sow_date.strftime("%d %b %Y") in doc
    assert fmt_rs(comp["stats_mixed"]["mean_net"]) in doc
    assert fmt_rs(abs(comp["stats_single"]["p10_net"])) in doc
    assert "not a forecast" in doc and "synthetic" in doc
    assert "@page" in doc and "A4" in doc


def test_summary_without_simulation_says_so(ds, farm):
    plan = solve_intercrop(farm(), ds).plan
    assert t("no_sim_note", "en") in summary_html(plan, ds, "en", None, embed_font=False)


def test_hindi_and_marathi_summaries_embed_font(ds, farm):
    plan, comp = _comp(ds, farm)
    for lang in ("hi", "mr"):
        doc = summary_html(plan, ds, lang, comp)
        assert "@font-face" in doc and ds.crops[plan.crop_ids[0]].name(lang) in doc


def test_gross_and_net_are_labelled_separately(ds, farm):
    _, comp = _comp(ds, farm)
    labels = [r[0] for r in metric_rows(comp["stats_mixed"], comp["stats_single"], "en")]
    assert any("gross" in l.lower() and "before costs" in l for l in labels)
    assert any("net margin" in l.lower() and "direct cost" in l for l in labels)


def test_plan_json_round_trip(ds, farm):
    plan, comp = _comp(ds, farm)
    data = json.loads(plan_json(plan, ds, comp))
    assert data["dataset_version"] == ds.version
    assert sum(a["acres"] for a in data["allocations"]) == plan.inputs.acres
    assert data["comparison"]["seasons"] == 1000


def test_indian_number_format():
    assert fmt_rs(1234567) == "12,34,567"
    assert fmt_rs(999) == "999"


def test_every_text_has_english():
    assert all("en" in v for v in T.values())
