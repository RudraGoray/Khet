"""End-to-end UI journeys with Streamlit's AppTest (runs the script; not a real browser, so the 3D view itself is not drawn).

The app starts on the landing page (app.py routes / to landing.py); each journey switches to the dashboard the
way "Launch KhetPlan" does.
"""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _button(at, text):
    return next(b for b in at.button if text in b.label)


def _start():
    at = AppTest.from_file(APP, default_timeout=90).run()
    assert not at.exception
    at.switch_page("dashboard.py").run()
    assert not at.exception
    return at


def _build(at, transcript):
    at.text_area(key="transcript").set_value(transcript).run()
    at.button(key="read_btn").click().run()
    at.checkbox(key="f_confirm").check().run()
    at.button(key="build_btn").click().run()
    assert not at.exception
    return at


def test_voice_transcript_to_twin_risk_and_report(ds):
    at = _start()
    at.text_area(key="transcript").set_value("I have 2 acres in Buldhana, kharif, borewell, low risk").run()
    _button(at, "Read my details").click().run()
    assert at.session_state["f_area"] == 2 and at.session_state["f_water"] == "assured"
    assert _button(at, "Build my farm plan").disabled  # not confirmed yet
    at.checkbox(key="f_confirm").check().run()
    _button(at, "Build my farm plan").click().run()
    assert at.session_state["result"].status == "OPTIMAL"
    # plan view: plan card, what-if lab, three tabs
    assert any("Your plan" in m.value for m in at.markdown)
    assert [t.label for t in at.tabs][:3] == ["📋 Plan & rules", "🎲 Risk lab", "🖨 Report"] or len(at.tabs) >= 3
    _button(at, "Run 1,000").click().run()
    assert at.session_state["comparison"]["seasons"] == 1000
    assert not at.exception


def test_manual_entry_without_voice():
    at = _start()
    assert len(at.error) >= 4  # region, area, season, water all missing
    at.selectbox(key="f_region").set_value("buldhana")
    at.number_input(key="f_area").set_value(30.0)
    at.selectbox(key="f_unit").set_value("guntha")
    at.selectbox(key="f_season").set_value("rabi")
    at.run()
    at.radio(key="f_water").set_value("rainfed")
    at.checkbox(key="f_confirm").check().run()
    assert len(at.error) == 0
    _button(at, "Build my farm plan").click().run()
    assert at.session_state["result"].plan.inputs.acres == 0.75


def test_unsupported_transcript_blocks_planning():
    at = _start()
    at.text_area(key="transcript").set_value("5 bigha in Pune for summer").run()
    _button(at, "Read my details").click().run()
    assert len(at.warning) == 3
    assert _button(at, "Build my farm plan").disabled


def test_infeasible_plan_is_explained():
    at = _start()
    at.text_area(key="transcript").set_value("Buldhana 2 acres kharif rainfed").run()
    _button(at, "Read my details").click().run()
    at.number_input(key="f_budget").set_value(1000).run()
    at.checkbox(key="f_confirm").check().run()
    _button(at, "Build my farm plan").click().run()
    assert at.session_state["result"].status == "INFEASIBLE"
    assert any("budget" in m.value for m in at.markdown)


def test_editing_inputs_marks_plan_stale():
    at = _build(_start(), "Buldhana 2 acres kharif rainfed")
    _button(at, "Edit farm details").click().run()
    at.number_input(key="f_area").set_value(3.0).run()
    assert any("changed since the last plan" in i.value for i in at.info)
    assert not any("What-if" in m.value for m in at.markdown)  # stale plan: no what-if on an old plan


def test_what_if_dry_spell_changes_outcome_not_plan():
    at = _build(_start(), "Buldhana 2 acres kharif rainfed")
    crops = at.session_state["result"].plan.crop_ids
    at.selectbox(key="wi_kind").set_value("dry_spell").run()
    at.slider(key="wi_sev").set_value(80).run()
    _button(at, "Apply to twin").click().run()
    assert at.session_state["what"].kind == "dry_spell" and at.session_state["what"].severity == 0.8
    assert at.session_state["result"].plan.crop_ids == crops
    assert any("kp-impact down" in m.value for m in at.markdown)
    _button(at, "Reset").click().run()
    assert at.session_state["what"].kind == "none"


def test_water_cut_offers_and_commits_a_replan(ds):
    at = _build(_start(), "Buldhana 2 acres kharif limited water from a well")
    old = at.session_state["result"].plan
    assert old.water_used_mm > 0, "fixture should use some irrigation"
    at.selectbox(key="wi_kind").set_value("water_cut").run()
    at.selectbox(key="wi_water").set_value("rainfed").run()
    _button(at, "Apply to twin").click().run()
    _button(at, "Re-plan").click().run()
    new = at.session_state["result"].plan
    assert new.inputs.water == "rainfed" and new.water_used_mm == 0
    assert at.session_state["f_water"] == "rainfed" and at.session_state["what"].kind == "none"
    assert any("New plan committed" in s.value for s in at.success)


def test_hindi_interface():
    at = _start()
    at.radio(key="lang").set_value("hi").run()
    assert any("अपना खेत बोलिए" in m.value for m in at.markdown)
    at = _build(at, "बुलढाणा में 2 एकड़, खरीफ, बारिश पर")
    assert at.session_state["result"].status == "OPTIMAL"
    assert any("आपकी योजना" in m.value or "योजना" in m.value for m in at.markdown)
