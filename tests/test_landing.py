"""Landing page: routing, and that every number it shows comes from the real modules."""
import json
import re
from pathlib import Path

from streamlit.testing.v1 import AppTest

from khetplan.landing_view import SAMPLE_INPUTS, SAMPLE_SENTENCES, _scenarios, landing_payload
from khetplan.models import FarmInputs
from khetplan.optimizer import solve_intercrop
from khetplan.twin import build_twin

ROOT = Path(__file__).resolve().parent.parent


def test_app_opens_on_the_landing_page_then_the_dashboard():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90).run()
    assert not at.exception
    assert len(at.text_area) == 0  # landing page: no dashboard widgets
    at.switch_page("dashboard.py").run()
    assert not at.exception
    assert at.text_area(key="transcript") is not None


def test_payload_is_the_real_plan_twin_and_scenarios(ds):
    data = landing_payload(ds)
    assert data["ok"] and data["dataset_version"] == ds.version
    plan = solve_intercrop(FarmInputs(**SAMPLE_INPUTS), ds).plan
    assert [a["id"] for a in data["plan"]] == plan.crop_ids
    assert abs(sum(a["share"] for a in data["plan"]) - 1) < 1e-9
    base = build_twin(plan, ds)
    assert data["twin"]["cum_sales"] == base["cum_sales"] and data["twin"]["stage"] == base["stage"]
    for kind, what in _scenarios(plan).items():
        tot = build_twin(plan, ds, what)["totals"]
        assert data["scenarios"][kind]["gross"] == round(tot["scenario_gross"])
        assert data["scenarios"][kind]["reference"] == round(tot["reference_gross"])
    replan = data["scenarios"]["water_cut"]["replan"]
    assert replan and abs(sum(a["share"] for a in replan) - 1) < 1e-9


def test_sample_sentences_parse_to_the_sample_farm(ds):
    data = landing_payload(ds)
    assert [p["lang"] for p in data["parsed"]] == [code for code, _ in SAMPLE_SENTENCES]
    for p in data["parsed"]:
        f = p["fields"]
        assert (f["region"], f["area_value"], f["season"], f["water"]) == ("buldhana", 2.0, "kharif", "limited")


def test_risk_numbers_are_the_risk_lab_output(ds):
    r = landing_payload(ds)["risk"]
    assert r["seasons"] == 1000 and r["seed"] == ds.sim["seed"]
    assert 0 <= r["mixed"]["loss"] <= 1 and 0 <= r["share_better"] <= 1


def test_payload_is_small_json(ds):
    assert len(json.dumps(landing_payload(ds))) < 200_000


def test_landing_files_referenced_by_the_page_exist():
    comp = ROOT / "components"
    html = (comp / "index.html").read_text(encoding="utf-8")
    refs = re.findall(r'(?:src|href)="(\./[^"]+)"', html)
    assert refs
    for ref in refs:
        assert (comp / ref).exists(), ref
    for js in ("landing/landing.js", "landing/farm.js"):
        for imp in re.findall(r"from '(\.[^']+)'", (comp / js).read_text(encoding="utf-8")):
            assert ((comp / js).parent / imp).resolve().exists(), imp
    css = (comp / "landing" / "landing.css").read_text(encoding="utf-8")
    for url in re.findall(r"url\('(\.[^']+)'\)", css):
        assert (comp / "landing" / url).resolve().exists(), url
