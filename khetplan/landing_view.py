"""Data and Streamlit bridge for the landing page (components/index.html).

Everything the landing page shows about the sample farm is computed here by the real
modules: the parser reads the sample sentences, CP-SAT plans the farm, the twin builds
the season, each what-if is replayed, and the risk lab runs 1,000 seasons. Nothing is
typed in by hand.
"""
from __future__ import annotations

from pathlib import Path

import streamlit.components.v1 as components

from .i18n import t
from .models import FarmInputs
from .optimizer import monoculture_candidates, solve_intercrop
from .parsing import parse_transcript
from .simulation import run_comparison
from .twin import STAGES, WhatIf, build_twin
from .twin_view import crop_meta
from .visualization import MONTHS

# path is the whole components folder so the page can reuse twin/farmkit.js and twin/vendor/
_COMPONENT = components.declare_component(
    "khetplan_landing", path=str(Path(__file__).resolve().parent.parent / "components")
)

SAMPLE_INPUTS = dict(region="buldhana", area_value=2.0, area_unit="acre", season="kharif", year=2027, water="limited", risk=50)
SAMPLE_SENTENCES = [
    ("en", "I have 2 acres in Buldhana for kharif, limited water from a well, medium risk"),
    ("hi", "मेरे पास बुलढाणा में 2 एकड़ ज़मीन है, खरीफ, कुएँ से थोड़ा पानी, मध्यम जोखिम"),
    ("mr", "माझ्याकडे बुलढाणा जिल्ह्यात २ एकर शेत आहे, खरीप, विहिरीचे थोडे पाणी, मध्यम जोखीम"),
]


def _scenarios(plan) -> dict:
    biggest = max(plan.allocations, key=lambda a: a.share).crop_id
    return {
        "dry_spell": WhatIf(kind="dry_spell", week=8, weeks=3, severity=0.6),
        "pest": WhatIf(kind="pest", week=6, severity=0.4, crop=biggest),
        "water_cut": WhatIf(kind="water_cut", week=4, water="rainfed"),
        "price": WhatIf(kind="price", week=20, change=-0.25),
    }


def landing_payload(dataset, lang: str = "en") -> dict:
    """Real results for the sample farm, in the shape the landing page uses."""
    inputs = FarmInputs(**SAMPLE_INPUTS)
    res = solve_intercrop(inputs, dataset)
    if res.plan is None or not res.plan.feasible:  # dataset edited so the sample no longer fits
        return {"ok": False}
    plan = res.plan
    base = build_twin(plan, dataset, lang=lang)
    ids = [a.crop_id for a in plan.allocations]

    parsed = []
    for code, text in SAMPLE_SENTENCES:
        f = parse_transcript(text).fields
        parsed.append({"lang": code, "text": text, "fields": {k: f.get(k) for k in ("region", "area_value", "area_unit", "season", "water", "risk")}})

    scenarios = {}
    for kind, what in _scenarios(plan).items():
        tw = build_twin(plan, dataset, what, lang)
        tot = tw["totals"]
        item = {
            "label": t(f"wi_{kind}", lang), "week": what.week, "crop": what.crop,
            "gross": round(tot["scenario_gross"]), "reference": round(tot["reference_gross"]),
            "factors": {cid: round(v["yield_factor"], 4) for cid, v in tw["per_crop"].items()},
            "per_crop": {cid: [round(v["scenario"]), round(v["reference"])] for cid, v in tw["per_crop"].items()},
            "health": tw["health"],
        }
        if kind == "water_cut":
            re = solve_intercrop(FarmInputs(**{**SAMPLE_INPUTS, "water": "rainfed"}), dataset)
            if re.plan is not None and re.plan.feasible:
                item["replan"] = [{"id": a.crop_id, "share": a.share} for a in re.plan.allocations]
        scenarios[kind] = item

    risk = None
    candidates = monoculture_candidates(inputs, dataset)
    if candidates:
        comp = run_comparison(plan, candidates[0], dataset)
        a, b = comp["stats_mixed"], comp["stats_single"]
        risk = {
            "baseline": comp["baseline"], "seasons": comp["seasons"], "seed": comp["seed"],
            "mixed": {"mean": round(a["mean_net"]), "p10": round(a["p10_net"]), "loss": a["prob_loss"]},
            "single": {"mean": round(b["mean_net"]), "p10": round(b["p10_net"]), "loss": b["prob_loss"]},
            "share_better": comp["cmp"]["share_a_better"],
        }
        ids_all = ids + [comp["baseline"]]
    else:
        ids_all = ids

    return {
        "ok": True,
        "dataset_version": dataset.version,
        "sample": {**SAMPLE_INPUTS, "acres": inputs.acres},
        "parsed": parsed,
        "plan": [{"id": a.crop_id, "share": a.share, "acres": a.acres, "sow": a.sow_date.isoformat(),
                  "harvest_start": a.harvest_start.isoformat(), "harvest_end": a.harvest_end.isoformat()} for a in plan.allocations],
        "water_used_mm": plan.water_used_mm, "water_limit_mm": plan.water_limit_mm,
        "twin": {k: base[k] for k in ("weeks", "strip_order", "crops", "stage", "growth", "health", "weather",
                                       "water_m3", "cum_sales", "events", "totals")},
        "crops": crop_meta(dataset, lang, ids_all),
        "stages": {s: t(f"stage_{i}", lang) for i, s in enumerate(STAGES)},
        "months": MONTHS[lang],
        "scenarios": scenarios,
        "risk": risk,
    }


def render_landing(payload: dict, key: str = "landing"):
    """Shows the landing page; returns {"action": "launch", "nonce": ...} when a launch button is pressed."""
    return _COMPONENT(data=payload, key=key, default=None, height=900)
