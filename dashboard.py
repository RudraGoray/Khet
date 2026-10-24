"""KhetPlan dashboard: voice-first intercrop planner with a 3D farm digital twin.

Served at /app by app.py (the landing page is /). Run:  streamlit run app.py
"""
from __future__ import annotations

import html
import json
from dataclasses import replace
from pathlib import Path

import pandas as pd
import streamlit as st

from khetplan import visualization as viz
from khetplan.data import DatasetError, default_dataset
from khetplan.export import metric_rows, plan_json, summary_html, verdict
from khetplan.i18n import LANGS, SPEECH_LOCALE, T, crop_list, fmt_acres, fmt_money, fmt_rs, render_item, t
from khetplan.models import ACRES_PER_UNIT, WATER_LEVELS, FarmInputs, check_inputs, default_year
from khetplan.optimizer import monoculture_candidates, solve_intercrop
from khetplan.parsing import parse_transcript
from khetplan.simulation import run_comparison
from khetplan.twin import WhatIf, build_twin
from khetplan.validation import water_limit_mm

ROOT = Path(__file__).resolve().parent
SAMPLES = json.loads((ROOT / "samples" / "sample_inputs.json").read_text(encoding="utf-8"))["examples"]
FORM_KEYS = ["f_region", "f_area", "f_unit", "f_season", "f_year", "f_water", "f_risk", "f_exclude", "f_budget", "f_confirm",
             "wi_kind", "wi_week", "wi_weeks", "wi_sev", "wi_crop", "wi_change", "wi_water"]

st.set_page_config(page_title="KhetPlan · Farm digital twin", page_icon="🌱", layout="wide", initial_sidebar_state="collapsed")
S = st.session_state

st.markdown(
    """<style>
@font-face { font-family: 'KhetNoto'; src: url('app/static/NotoSansDevanagari.ttf') format('truetype'); font-display: swap; }
:root { --kp-ink:#13231a; --kp-muted:#5b6a60; --kp-green:#1d4a2c; --kp-line:#e3e6df; }
html, body, .stApp, .stMarkdown, button, input, textarea, select, label, [data-testid="stWidgetLabel"] p {
  font-family: 'Inter', 'KhetNoto', 'Noto Sans Devanagari', 'Nirmala UI', system-ui, -apple-system, 'Segoe UI', sans-serif !important; }
.stApp { background: radial-gradient(1200px 500px at 85% -10%, #e4efe0 0%, rgba(228,239,224,0) 60%), #f5f6f1; }
header[data-testid="stHeader"] { background: transparent; height: 0; }
[data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer { display: none !important; }
.block-container { padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1480px; }
h1, h2, h3 { color: var(--kp-ink); letter-spacing: -0.02em; }
.kp-top { display:flex; align-items:center; gap:14px; }
.kp-logo { width:44px; height:44px; border-radius:13px; background: linear-gradient(135deg,#2c7a45,#1d4a2c); display:grid; place-items:center;
  color:#fff; font-size:24px; box-shadow:0 8px 18px rgba(29,74,44,.28); }
.kp-brand { font-size:24px; font-weight:800; letter-spacing:-.02em; color:var(--kp-ink); line-height:1.05; }
.kp-brand small { display:block; font-size:12px; font-weight:700; letter-spacing:.16em; color:#3c8d4f; }
.kp-hero h1 { font-size: 2.35rem !important; line-height:1.1; margin: .8rem 0 .4rem !important; font-weight: 800; }
.kp-hero p { color: var(--kp-muted); font-size: 1.05rem; max-width: 820px; margin-bottom: .6rem; }
.kp-chip { display:inline-flex; align-items:center; gap:6px; padding:4px 10px; border-radius:999px; background:#fff; border:1px solid var(--kp-line);
  font-size:12.5px; font-weight:600; color:var(--kp-muted); margin-right:6px; }
.kp-warn { background:#fff7e6; border-color:#f0d9a8; color:#7a5a12; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div > div > .kp-panel-anchor) { background:#fff; border-radius:18px; border:1px solid var(--kp-line);
  box-shadow: 0 10px 30px rgba(19,35,26,.06); }
.kp-panel-title { font-weight:800; font-size:1.05rem; color:var(--kp-ink); margin:.1rem 0 .4rem; letter-spacing:-.01em; }
.kp-sub { color:var(--kp-muted); font-size:.92rem; margin-bottom:.4rem; }
.kp-ok { color:#1d6b35; font-size:.82rem; font-weight:600; } .kp-miss { color:#a0521a; font-size:.82rem; font-weight:700; }
.kp-quote { border-left:3px solid #2c7a45; padding:.35rem .8rem; background:#f4f8f2; border-radius:.4rem; font-size:.98rem; margin:.2rem 0 .6rem; }
.stButton > button, .stDownloadButton > button { min-height: 2.9rem; border-radius: 12px; font-weight: 700; border:1px solid var(--kp-line); }
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] { background: linear-gradient(135deg,#2c7a45,#1d4a2c); border:0;
  box-shadow: 0 8px 18px rgba(29,74,44,.25); color:#fff; }
.stButton > button[kind="primary"]:disabled { background:#dfe5dd; color:#6f7b72; box-shadow:none; }
div[data-testid="stMetric"] { background:#f7f9f5; border:1px solid var(--kp-line); border-radius:14px; padding:.6rem .8rem; }
div[data-testid="stMetricLabel"] p { font-size:.78rem !important; color:var(--kp-muted); }
div[data-testid="stMetricValue"] { font-size:1.35rem; font-weight:800; }
.kp-crop { display:flex; align-items:center; gap:10px; padding:8px 0; border-bottom:1px solid var(--kp-line); }
.kp-crop:last-child { border-bottom:0; }
.kp-crop .sw { width:14px; height:14px; border-radius:5px; flex:none; }
.kp-crop .nm { font-weight:700; }
.kp-crop .sh { margin-left:auto; color:var(--kp-muted); font-weight:600; font-size:.9rem; }
.kp-status { display:inline-flex; gap:8px; align-items:center; padding:6px 12px; border-radius:999px; font-weight:700; font-size:.88rem; }
.kp-status.good { background:#e2efe0; color:#1d4a2c; } .kp-status.bad { background:#f8e1da; color:#8a2b12; }
.kp-impact { font-size:1.6rem; font-weight:800; letter-spacing:-.02em; }
.kp-impact.down { color:#b0412a; } .kp-impact small { font-size:.85rem; color:var(--kp-muted); font-weight:600; }
.kp-ib { margin: .35rem 0 .7rem; }
.kp-ib-h { display:flex; justify-content:space-between; font-size:.88rem; margin-bottom:4px; }
.kp-ib-h span { color: var(--kp-muted); font-variant-numeric: tabular-nums; }
.kp-ib-t { position:relative; height:12px; background:#f0f2ee; border-radius:6px; overflow:hidden; }
.kp-ib-t i { position:absolute; left:0; top:0; bottom:0; border-radius:6px; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] { background:#fff; border:1px solid var(--kp-line); border-radius:12px; padding:8px 16px; font-weight:700; }
.stTabs [aria-selected="true"] { background:#1d4a2c; color:#fff; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display:none; }
@media (max-width: 760px) { .kp-hero h1 { font-size: 1.7rem !important; } .block-container { padding-left: .8rem; padding-right: .8rem; } }
</style>""",
    unsafe_allow_html=True,
)


@st.cache_resource
def dataset():
    return default_dataset()


try:
    DS = dataset()
except (DatasetError, OSError, ValueError) as exc:
    st.error(f"The crop dataset failed validation, so KhetPlan cannot run: {exc}")
    st.stop()

for k in FORM_KEYS:  # keep values when the widget is not on screen this run
    if k in S:
        S[k] = S[k]
S.setdefault("lang", "en")
S.setdefault("transcript", "")
S.setdefault("speech_seq", None)
S.setdefault("what", WhatIf())


def L(key, **kw):
    return t(key, S.lang, **kw)


def label_fn(prefix: str):
    lang = S.lang
    return lambda v: t("choose", lang) if v is None else t(f"{prefix}{v}", lang)


def current_inputs() -> FarmInputs:
    budget = S.get("f_budget") or None
    return FarmInputs(
        region=S.get("f_region"), area_value=S.get("f_area"), area_unit=S.get("f_unit") or "acre",
        season=S.get("f_season"), year=S.get("f_year"), water=S.get("f_water"), risk=int(S.get("f_risk", 50)),
        excluded_crops=tuple(S.get("f_exclude") or ()), budget_rs=float(budget) if budget else None,
    )


def current_plan():
    res = S.get("result")
    if res is None or S.get("plan_key") != current_inputs().key():
        return None
    return res.plan if res.plan and res.plan.feasible else None


def apply_parse():
    r = parse_transcript(S.transcript)
    S.parsed = r
    f = r.fields
    for src, dst in [("region", "f_region"), ("area_value", "f_area"), ("area_unit", "f_unit"), ("season", "f_season"),
                     ("water", "f_water"), ("risk", "f_risk"), ("year", "f_year")]:
        if src in f:
            S[dst] = f[src]
    if "region" not in f and any(i[0] == "parse_region_unsupported" for i in r.issues):
        S.f_region = "other"
    if "season" not in f and any(i[0] == "parse_season_unsupported" for i in r.issues):
        S.f_season = "zaid"
    if S.get("f_season") in ("kharif", "rabi") and "year" not in f:
        S.f_year = default_year(S.f_season)
    S.f_confirm = False


def use_example(text):
    S.transcript = text


def build_plan():
    inputs = current_inputs()
    S.result = solve_intercrop(inputs, DS)
    S.plan_key = inputs.key()
    S.pop("comparison", None)
    S.what = WhatIf()
    S.wi_kind = "none"
    S.autoplay = True
    S.editing = False


def apply_what_if():
    kind = S.get("wi_kind", "none")
    S.what = WhatIf(
        kind=kind, week=int(S.get("wi_week", 6)), weeks=int(S.get("wi_weeks", 3)),
        severity=float(S.get("wi_sev", 50)) / 100, crop=S.get("wi_crop") if kind in ("pest", "price") else None,
        change=float(S.get("wi_change", -25)) / 100, water=S.get("wi_water") if kind == "water_cut" else None,
    )
    S.pop("replan_msg", None)


def reset_what_if():
    S.what = WhatIf()
    S.wi_kind = "none"
    S.pop("replan_msg", None)


def replan_for_water():
    plan = current_plan()
    new_water = S.what.water
    old = crop_list(plan.crop_ids, DS, S.lang)
    res = solve_intercrop(replace(plan.inputs, water=new_water), DS)
    if res.plan is not None and res.plan.feasible:
        S.result = res
        S.f_water = new_water
        S.plan_key = res.plan.inputs.key()
        S.pop("comparison", None)
        S.what = WhatIf()
        S.wi_kind = "none"
        S.autoplay = True
        S.replan_msg = ("success", L("replan_ok", water=L(f"water_{new_water}"), old=old))
    else:
        S.replan_msg = ("error", L("replan_fail", water=L(f"water_{new_water}")))


# ---------------- header ----------------
h1, h2 = st.columns([3, 2], vertical_alignment="center")
with h1:
    st.markdown(f"<div class='kp-top'><div class='kp-logo'>🌱</div><div class='kp-brand'>{L('app_title')}<small>{L('hero_kicker')}</small></div></div>",
                unsafe_allow_html=True)
with h2:
    c_lang, c_home = st.columns([4, 1], vertical_alignment="center")
    c_lang.radio(L("language"), list(LANGS), format_func=LANGS.get, key="lang", horizontal=True, label_visibility="collapsed")
    c_home.page_link("landing.py", label="Home", icon=":material/arrow_back:")

plan = current_plan()
if plan is None:
    st.markdown(f"<div class='kp-hero'><h1>{L('hero_title')}</h1><p>{L('hero_sub')}</p></div>", unsafe_allow_html=True)
st.markdown(
    f"<span class='kp-chip kp-warn'>⚠️ {L('demo_banner')}</span>"
    f"<span class='kp-chip'>📦 {L('sum_dataset')} v{DS.version} · {L('region_buldhana')} · {L('season_short_kharif')} / {L('season_short_rabi')}</span>",
    unsafe_allow_html=True,
)
st.write("")


# ---------------- left panel: setup ----------------
def heard_note(field, value_key):
    r = S.get("parsed")
    if r and field in r.heard:
        st.markdown(f"<span class='kp-ok'>{html.escape(L('heard_as', phrase=r.heard[field]))}</span>", unsafe_allow_html=True)
    elif S.get(value_key) in (None, "", []):
        st.markdown(f"<span class='kp-miss'>{L('not_heard')}</span>", unsafe_allow_html=True)


def voice_panel():
    with st.container(border=True):
        st.markdown("<span class='kp-panel-anchor'></span>", unsafe_allow_html=True)
        st.markdown(f"<div class='kp-panel-title'>{L('panel_voice')}</div><div class='kp-sub'>{L('listening_tip')}</div>", unsafe_allow_html=True)
        try:
            from khetplan.speech import speech_input

            value = speech_input(
                SPEECH_LOCALE[S.lang],
                {"start": L("mic_title"), "stop": L("mic_stop"), "ready": "", "listening": L("mic_listening"),
                 "done": L("mic_got"), "error": L("mic_problem"), "nothing": L("mic_nothing"), "starting": L("mic_starting")},
                key=f"speech_{S.lang}",
            )
        except Exception as exc:  # component failed to load: typing still works
            value = {"kind": "error", "error": str(exc), "seq": -1}
        if value and value.get("seq") != S.speech_seq:
            S.speech_seq = value.get("seq")
            if value.get("kind") == "transcript":
                S.transcript = value["text"]
                S.pop("mic_error", None)
                apply_parse()
            else:
                S.mic_error = value.get("error", "unknown")
        if S.get("mic_error"):
            code = S.mic_error
            st.warning(L("mic_error", detail=L(f"mic_err_{code}") if f"mic_err_{code}" in T else code))
        st.text_area(L("transcript"), key="transcript", placeholder=L("transcript_ph"), height=90)
        examples = [e for e in SAMPLES if e["lang"] == S.lang] or [e for e in SAMPLES if e["lang"] == "en"]
        st.caption(L("examples"))
        cols = st.columns(2)
        for i, ex in enumerate(examples[:4]):
            cols[i % 2].button(ex["label"], key=f"ex_{S.lang}_{i}", on_click=use_example, args=(ex["text"],), width="stretch")
        st.button(L("read_details"), key="read_btn", type="primary", on_click=apply_parse, width="stretch", disabled=not S.transcript.strip())
        st.caption(L("mic_note"))


def details_panel():
    with st.container(border=True):
        st.markdown("<span class='kp-panel-anchor'></span>", unsafe_allow_html=True)
        st.markdown(f"<div class='kp-panel-title'>{L('panel_details')}</div>", unsafe_allow_html=True)
        r = S.get("parsed")
        if r and S.transcript.strip():
            st.markdown(f"<div class='kp-quote'>“{html.escape(S.transcript)}”</div>", unsafe_allow_html=True)
            for key, detail in r.issues:
                st.warning(L(key, detail=detail))
        st.selectbox(L("f_region"), [None, "buldhana", "other"], key="f_region", format_func=label_fn("region_"))
        heard_note("region", "f_region")
        c1, c2 = st.columns([3, 2])
        c1.number_input(L("f_area"), min_value=0.0, max_value=10000.0, step=0.5, value=None, key="f_area", format="%g")
        c2.selectbox(L("f_unit"), list(ACRES_PER_UNIT), key="f_unit", format_func=label_fn("unit_"))
        heard_note("area_value", "f_area")
        c1, c2 = st.columns([3, 2])
        c1.selectbox(L("f_season"), [None, "kharif", "rabi", "zaid"], key="f_season", format_func=label_fn("season_"))
        if S.get("f_season") in ("kharif", "rabi") and S.get("f_year") is None:
            S.f_year = default_year(S.f_season)
        c2.selectbox(L("f_year"), [None] + list(range(2025, 2031)), key="f_year", format_func=lambda v, c=L("choose"): c if v is None else str(v))
        heard_note("season", "f_season")
        st.radio(L("f_water"), list(WATER_LEVELS), key="f_water", index=None, format_func=label_fn("water_"))
        heard_note("water", "f_water")
        S.setdefault("f_risk", 50)
        st.slider(L("f_risk"), 0, 100, step=5, key="f_risk")
        word = L("risk_low") if S.f_risk < 34 else L("risk_mid") if S.f_risk < 67 else L("risk_high")
        st.caption(f"← {L('risk_left')}  ·  **{word}**  ·  {L('risk_right')} →")
        with st.expander(L("advanced")):
            season_crops = [c.id for c in DS.crops.values() if c.season == S.get("f_season")]
            S.f_exclude = [c for c in (S.get("f_exclude") or []) if c in season_crops]
            st.multiselect(L("f_exclude"), season_crops, key="f_exclude", format_func=lambda c, lang=S.lang: DS.crops[c].name(lang))
            S.setdefault("f_budget", 0)
            st.number_input(L("f_budget"), min_value=0, step=1000, key="f_budget")
        inputs = current_inputs()
        problems = check_inputs(inputs, DS)
        for field, key, detail in problems:
            st.error(render_item({"key": key, "field": field, "detail": detail}, DS, S.lang))
        if S.get("plan_key") and S.plan_key != inputs.key():
            st.info(L("stale"))
        st.checkbox(L("confirm_box"), key="f_confirm")
        clicked = st.button(L("build_farm"), key="build_btn", type="primary", width="stretch", disabled=bool(problems) or not S.get("f_confirm"))
        if clicked:
            with st.spinner(L("solving")):
                build_plan()
            st.rerun()
        if not problems and not S.get("f_confirm"):
            st.caption(L("need_confirm"))


# ---------------- left panel: plan + what-if ----------------
def plan_panel(plan, twin):
    res = S.result
    with st.container(border=True):
        st.markdown("<span class='kp-panel-anchor'></span>", unsafe_allow_html=True)
        st.markdown(f"<div class='kp-panel-title'>{L('plan_card')}</div><span class='kp-status good'>{L('status_' + res.status)}</span>",
                    unsafe_allow_html=True)
        rows = "".join(
            f"<div class='kp-crop'><span class='sw' style='background:{viz.crop_color(DS, a.crop_id)}'></span>"
            f"<span class='nm'>{DS.crops[a.crop_id].name(S.lang)}</span><span class='sh'>{a.share:.0%} · {fmt_acres(a.acres, S.lang)}</span></div>"
            for a in plan.allocations
        )
        st.markdown(rows, unsafe_allow_html=True)
        tot = twin["totals"]
        c1, c2 = st.columns(2)
        c1.metric(L("kpi_gross"), "₹" + fmt_rs(tot["reference_gross"]))
        c2.metric(L("kpi_net"), fmt_money(tot["reference_gross"] - tot["cost"]))
        c1, c2 = st.columns(2)
        c1.metric(L("kpi_water"), f"{plan.water_used_mm:.0f} / {plan.water_limit_mm:.0f} mm")
        peak = tot["peak_labour_week"]
        c2.metric(L("kpi_peak"), L("week_of", i=peak + 1, n=len(twin["weeks"])).split(" ")[0] + f" {peak + 1}")
        st.button("✏️ " + L("edit_farm"), key="edit_btn", width="stretch", on_click=lambda: S.update(editing=True))


def impact_html(per_crop: dict) -> str:
    """Planned vs what-if gross per crop as simple bars (grey = planned, colour = under the shock)."""
    top = max(v["reference"] for v in per_crop.values()) or 1
    rows = []
    for cid, v in per_crop.items():
        color = viz.crop_color(DS, cid)
        rows.append(
            f"<div class='kp-ib'><div class='kp-ib-h'><b>{html.escape(DS.crops[cid].name(S.lang))}</b>"
            f"<span>₹{fmt_rs(v['scenario'])} / ₹{fmt_rs(v['reference'])}</span></div>"
            f"<div class='kp-ib-t'><i style='width:{v['reference'] / top:.1%};background:#d5dbd3'></i>"
            f"<i style='width:{v['scenario'] / top:.1%};background:{color}'></i></div></div>"
        )
    return "".join(rows)


def what_if_panel(plan, twin):
    with st.container(border=True):
        st.markdown("<span class='kp-panel-anchor'></span>", unsafe_allow_html=True)
        st.markdown(f"<div class='kp-panel-title'>{L('wi_title')}</div><div class='kp-sub'>{L('wi_help')}</div>", unsafe_allow_html=True)
        kinds = ["none", "dry_spell", "pest", "price", "water_cut"]
        S.setdefault("wi_kind", "none")
        st.selectbox(L("wi_kind"), kinds, key="wi_kind", format_func=label_fn("wi_"))
        kind = S.wi_kind
        n_weeks = len(twin["weeks"])
        if kind != "none":
            S.setdefault("wi_week", min(8, n_weeks - 2))
            S.wi_week = min(S.wi_week, n_weeks - 1)
            st.slider(L("wi_week"), 0, n_weeks - 1, key="wi_week")
        if kind == "dry_spell":
            c1, c2 = st.columns(2)
            S.setdefault("wi_weeks", 3)
            S.setdefault("wi_sev", 60)
            c1.slider(L("wi_weeks"), 1, 8, key="wi_weeks")
            c2.slider(L("wi_severity") + " (%)", 10, 100, step=10, key="wi_sev")
        elif kind == "pest":
            if S.get("wi_crop") not in plan.crop_ids:
                S.wi_crop = plan.crop_ids[0]
            S.setdefault("wi_sev", 40)
            c1, c2 = st.columns(2)
            c1.selectbox(L("wi_crop"), plan.crop_ids, key="wi_crop", format_func=lambda c, lang=S.lang: DS.crops[c].name(lang))
            c2.slider(L("wi_severity") + " (%)", 10, 100, step=10, key="wi_sev")
        elif kind == "price":
            opts = [None] + plan.crop_ids
            if S.get("wi_crop") not in opts:
                S.wi_crop = None
            S.setdefault("wi_change", -25)
            c1, c2 = st.columns(2)
            c1.selectbox(L("wi_crop"), opts, key="wi_crop",
                         format_func=lambda c, lang=S.lang: t("all_crops", lang) if c is None else DS.crops[c].name(lang))
            c2.slider(L("wi_change"), -60, 60, step=5, key="wi_change")
        elif kind == "water_cut":
            levels = [w for w in WATER_LEVELS if water_limit_mm(DS, w) < plan.water_limit_mm]
            if not levels:
                st.info(L("replan_fits"))
            else:
                if S.get("wi_water") not in levels:
                    S.wi_water = levels[0]
                st.selectbox(L("wi_water"), levels, key="wi_water", format_func=label_fn("water_"))
        b1, b2 = st.columns(2)
        b1.button(L("wi_apply"), type="primary", on_click=apply_what_if, width="stretch",
                  disabled=kind == "none" or (kind == "water_cut" and not S.get("wi_water")))
        b2.button(L("wi_reset"), on_click=reset_what_if, width="stretch")

        what = S.what
        tot = twin["totals"]
        if what.kind != "none":
            delta = tot["scenario_gross"] - tot["reference_gross"]
            st.markdown(
                f"<div class='kp-sub'>{L('wi_active', name=L('wi_' + what.kind))}</div>"
                f"<div class='kp-sub'>{L('wi_impact')}</div>"
                f"<div class='kp-impact {'down' if delta < -0.5 else ''}'>₹{fmt_rs(tot['scenario_gross'])} "
                f"<small>{fmt_money(delta)} · {L('wi_vs', ref='₹' + fmt_rs(tot['reference_gross']))}</small></div>",
                unsafe_allow_html=True,
            )
            st.markdown(impact_html(twin["per_crop"]), unsafe_allow_html=True)
            if what.kind == "water_cut" and what.water:
                limit = water_limit_mm(DS, what.water)
                if plan.water_used_mm > limit:
                    st.caption(L("replan_hint", used=f"{plan.water_used_mm:.0f}", water=L(f"water_{what.water}"), limit=f"{limit:.0f}"))
                    st.button(L("replan"), on_click=replan_for_water, width="stretch")
                else:
                    st.caption(L("replan_fits"))
            st.caption("ⓘ " + L("wi_note"))
        msg = S.get("replan_msg")
        if msg:
            (st.success if msg[0] == "success" else st.error)(msg[1])


# ---------------- layout ----------------
editing = plan is None or S.get("editing")
if not editing:  # on phones, show the field first once a plan exists
    st.markdown("<style>@media (max-width: 640px) { div[data-testid='stHorizontalBlock']:has(iframe[title*='khetplan_twin']) "
                "{ flex-direction: column-reverse; } }</style>", unsafe_allow_html=True)
left, right = st.columns([0.33, 0.67], gap="large")
twin = build_twin(plan, DS, S.what, S.lang) if plan is not None else None

with left:
    if editing:
        voice_panel()
        details_panel()
        if plan is not None and st.button(L("back"), width="stretch"):
            S.editing = False
            st.rerun()
    else:
        plan_panel(plan, twin)
        what_if_panel(plan, twin)
    res = S.get("result")
    if res is not None and S.get("plan_key") == current_inputs().key() and (res.plan is None or not res.plan.feasible):
        with st.container(border=True):
            st.markdown(f"<span class='kp-status bad'>{L('status_' + res.status)}</span>", unsafe_allow_html=True)
            for item in res.reasons:
                st.write("• " + render_item(item, DS, S.lang))

with right:
    from khetplan.twin_view import render_twin

    autoplay = bool(S.pop("autoplay", False))
    render_twin(dataset=DS, lang=S.lang, inputs=current_inputs(), twin=twin,
                plan_key=str(hash(S.get("plan_key"))) if plan is not None else None, autoplay=autoplay, height=640)
    st.caption(L("twin_caption"))


# ---------------- below: details tabs ----------------
def plan_tab(plan):
    inp = plan.inputs
    c1, c2 = st.columns([1.1, 1])
    with c1:
        rows = []
        for a in plan.allocations:
            c = DS.crops[a.crop_id]
            rows.append({
                L("col_crop"): c.name(S.lang), L("col_share"): f"{a.share:.0%}", L("col_area"): fmt_acres(a.acres, S.lang),
                L("col_sow"): a.sow_date.strftime("%d %b %Y"), L("col_harvest"): f"{a.harvest_start:%d %b} – {a.harvest_end:%d %b %Y}",
                L("col_irrigation"): f"{c.irrigation_mm} mm", L("col_cost"): "₹" + fmt_rs(c.cost_rs_per_acre * a.acres),
                L("col_gross_normal"): "₹" + fmt_rs(c.gross_per_acre * a.acres),
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.plotly_chart(viz.calendar(plan, DS, S.lang), width="stretch", config={"displayModeBar": False})
        st.plotly_chart(viz.bed_map(plan, DS, S.lang), width="stretch", config={"displayModeBar": False})
        st.caption(L("map_caption", strips=len(plan.strip_order), strip_area=f"{inp.acres / len(plan.strip_order):.3f} {L('unit_acre')}"))
    with c2:
        st.markdown(f"**{L('tab_why')}**")
        for item in plan.explanation:
            st.write("• " + render_item(item, DS, S.lang))
        st.markdown(f"**{L('checks_title')}**")
        checks = ["check_area", "check_season", "check_shares", "check_pairs", "check_water", "check_excluded"]
        if inp.budget_rs:
            checks.append("check_budget")
        for c in checks:
            st.write("✅ " + L(c, acres=fmt_acres(inp.acres, S.lang)))


def risk_tab(plan):
    st.write(L("s4_help", n=f"{DS.sim['seasons']:,}"))
    candidates = monoculture_candidates(plan.inputs, DS)
    if not candidates:
        st.warning(L("no_baseline"))
        return
    ids = [p.crop_ids[0] for p in candidates]
    c1, c2, c3 = st.columns([2, 1, 1], vertical_alignment="bottom")
    base = c1.selectbox(L("baseline"), ids, format_func=lambda c, lang=S.lang: DS.crops[c].name(lang), help=L("baseline_help"))
    seed = c2.number_input(L("seed"), min_value=0, max_value=10**9, value=int(DS.sim["seed"]), step=1)
    if c3.button(L("run_sim"), type="primary", width="stretch"):
        with st.spinner(L("simulating")):
            S.comparison = run_comparison(plan, candidates[ids.index(base)], DS, seed=int(seed))
            S.comparison_key = (S.plan_key, base, int(seed))
    comp = S.get("comparison")
    if not comp or S.get("comparison_key", (None,))[0] != S.plan_key:
        return
    labels = (L("mixed_plan"), L("single_plan", crop=DS.crops[comp["baseline"]].name(S.lang)))
    st.info(f"**{verdict(comp, DS, S.lang)}** {L('verdict_honest')}")
    m1, m2, m3, m4 = st.columns(4)
    a, b = comp["stats_mixed"], comp["stats_single"]
    m1.metric(L("m_mean_net"), fmt_money(a["mean_net"]), fmt_money(a["mean_net"] - b["mean_net"]))
    m2.metric(L("m_p10_net"), fmt_money(a["p10_net"]), fmt_money(a["p10_net"] - b["p10_net"]))
    m3.metric(L("m_prob_loss"), f"{a['prob_loss']:.0%}", f"{(a['prob_loss'] - b['prob_loss']) * 100:+.1f} pts", delta_color="inverse")
    m4.metric(L("m_zero_months"), f"{a['mean_zero_income_months']:.1f}",
              f"{a['mean_zero_income_months'] - b['mean_zero_income_months']:+.1f}", delta_color="inverse")
    c1, c2 = st.columns(2)
    cfg = {"displayModeBar": False}
    with c1:
        st.markdown(f"**{L('chart_monthly')}** · P10–P90")
        st.plotly_chart(viz.monthly_band(a, b, labels, plan.inputs.season, plan.inputs.year, S.lang), width="stretch", config=cfg)
    with c2:
        st.markdown(f"**{L('chart_dist')}**")
        st.plotly_chart(viz.distribution(comp["mixed"], comp["single"], labels, S.lang), width="stretch", config=cfg)
    c1, c2 = st.columns(2)
    with c1:
        st.dataframe(pd.DataFrame(metric_rows(a, b, S.lang), columns=[L("m_metric"), labels[0], labels[1], L("m_diff")]),
                     hide_index=True, width="stretch")
    with c2:
        st.markdown(f"**{L('chart_diff')}**")
        st.plotly_chart(viz.difference(comp["cmp"]["diff"], S.lang), width="stretch", config=cfg)
    st.caption("ⓘ " + L("sim_disclaimer"))


def report_tab(plan, twin):
    comp = S.get("comparison") if S.get("comparison_key", (None,))[0] == S.plan_key else None
    if comp is None:
        st.info(L("no_sim_note"))
    st.write(L("s5_help"))
    line = None
    if S.what.kind != "none":
        tot = twin["totals"]
        line = f"{L('wi_' + S.what.kind)} · {L('wi_impact')}: ₹{fmt_rs(tot['scenario_gross'])} ({L('wi_vs', ref='₹' + fmt_rs(tot['reference_gross']))})"
    doc = summary_html(plan, DS, S.lang, comp, what_if_line=line)
    c1, c2 = st.columns(2)
    c1.download_button(L("download_html"), doc, file_name=f"khetplan-summary-{S.lang}.html", mime="text/html", type="primary", width="stretch")
    c2.download_button(L("download_json"), plan_json(plan, DS, comp), file_name="khetplan-plan.json", mime="application/json", width="stretch")
    printable = doc.replace(
        "<body>",
        "<body><div class='noprint' style='text-align:right;margin-bottom:8px'><button onclick='window.print()' style='font-size:15px;"
        f"padding:9px 18px;border-radius:12px;border:0;background:#1d4a2c;color:#fff;cursor:pointer'>{L('print_now')}</button></div>",
        1,
    )
    st.iframe(printable, height=1180)  # our own generated HTML; user text in it is escaped


if plan is not None:
    st.write("")
    tab1, tab2, tab3 = st.tabs([L("tab_twin_plan"), L("tab_risk"), L("tab_report")])
    with tab1:
        plan_tab(plan)
    with tab2:
        risk_tab(plan)
    with tab3:
        report_tab(plan, twin)
