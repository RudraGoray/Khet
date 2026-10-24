"""Streamlit bridge to the 3D digital-twin component (components/twin, Three.js bundled locally)."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import streamlit.components.v1 as components

from .i18n import T, t
from .visualization import MONTHS, crop_color

_COMPONENT = components.declare_component(
    "khetplan_twin", path=str(Path(__file__).resolve().parent.parent / "components" / "twin")
)

# Visual-only look of each crop in 3D: plant form, relative height, flower and ripe colours.
CROP_LOOK = {
    "soybean": ("bush", 0.75, "#9b6bd6", "#c8a64b"),
    "pigeonpea": ("bush", 1.7, "#f2c230", "#9c7a3c"),
    "greengram": ("bush", 0.55, "#f2d43a", "#7f7a3a"),
    "blackgram": ("bush", 0.55, "#e8c94a", "#4d4a33"),
    "cotton": ("bush", 1.25, "#f6edc8", "#a0874f"),
    "sorghum": ("grass", 2.1, "#d9c27a", "#a0522d"),
    "sesame": ("stalk", 1.3, "#f3d6e6", "#b58b4a"),
    "chickpea": ("bush", 0.55, "#d36ba5", "#b9a05a"),
    "wheat": ("grass", 0.95, "#e9df9a", "#d9ad3c"),
    "safflower": ("stalk", 1.05, "#f08a24", "#c28a3a"),
    "rabi_sorghum": ("grass", 1.7, "#d9c27a", "#c08a4a"),
    "linseed": ("stalk", 0.75, "#6a8fe0", "#b5964e"),
    "mustard": ("stalk", 1.45, "#f2d21c", "#a88c3c"),
}

LABEL_KEYS = [
    "sales", "water_week", "labour_week", "plot", "water", "season", "person_days", "acre", "week_of", "mini_title",
    "legend_water", "legend_sales", "legend_ref", "health", "harvested", "sow_on", "strip", "all_crops",
    "intro_plan", "intro_plan_sub", "intro_preview", "intro_preview_sub", "wx_rain", "wx_dry", "wx_clear",
    "ev_sow", "ev_flower", "ev_harvest", "ev_done", "ev_dry_spell", "ev_pest", "ev_price", "ev_water_cut",
] + [f"stage_{i}" for i in range(7)]


def crop_meta(dataset, lang: str, crop_ids) -> dict:
    out = {}
    for cid in crop_ids:
        c = dataset.crops[cid]
        kind, height, flower, mature = CROP_LOOK.get(cid, ("bush", 1.0, "#f2d43a", "#b8a040"))
        out[cid] = {
            "name": c.name(lang), "short": c.name(lang).split(" (")[0], "color": crop_color(dataset, cid),
            "kind": kind, "height": height, "flower": flower, "mature": mature, "irrigated": c.irrigation_mm > 0,
        }
    return out


def farm_meta(inputs, lang: str) -> dict:
    """Plot facts for the 3D field. Works on partly filled inputs (preview while editing)."""
    try:
        acres = inputs.acres
    except (ValueError, TypeError):
        acres = None
    side = math.sqrt(acres * 4046.86) if acres else None
    unit = t("unit_acre", lang)
    return {
        "acres": acres or 0,
        "water": inputs.water or "rainfed",
        "season": inputs.season or "kharif",
        "acres_label": f"{acres:.2f} <small>{unit}</small>" if acres else "—",
        "water_label": t(f"water_short_{inputs.water}", lang) if inputs.water else "—",
        "season_label": (t(f"season_short_{inputs.season}", lang) + (f" {inputs.year}" if inputs.year else "")) if inputs.season in ("kharif", "rabi") else "—",
        "title": t("twin_preview_title", lang) if acres else t("twin_empty_title", lang),
        "subtitle": t("twin_preview_sub", lang),
        "width_label": f"≈ {side:.0f} m" if side else "",
        "depth_label": f"≈ {side:.0f} m" if side else "",
    }


def render_twin(*, dataset, lang: str, inputs, twin: dict | None, plan_key: str | None, autoplay: bool,
                height: int = 640, key: str = "twin"):
    mode = "plan" if twin else "preview"
    crops = crop_meta(dataset, lang, [c["id"] for c in twin["crops"]]) if twin else {}
    labels = {k: t(k, lang) for k in LABEL_KEYS if k in T}
    payload = {
        "mode": mode,
        "plan_key": plan_key or "preview",
        "farm": farm_meta(inputs, lang),
        "twin": twin,
        "crops": crops,
        "labels": labels,
        "months": MONTHS[lang],
    }
    # The view only rebuilds when this changes, so autoplay and height are left out of it.
    payload["version"] = hashlib.sha1(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
    return _COMPONENT(**payload, height=height, autoplay=autoplay, key=key, default=None)
