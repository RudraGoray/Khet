"""Farm digital twin: a week-by-week replay of one season for a validated plan.

The twin turns the plan into crop stages, water and labour demand, harvest sales and
events for every week, and can replay the same season under one "what-if" shock.
Stage boundaries, crop-water curves, labour profiles and shock responses are simple,
transparent prototype assumptions (A1), not a crop-growth model.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, timedelta

from .validation import water_limit_mm

STAGES = ("not_sown", "germination", "vegetative", "flowering", "maturing", "harvest", "done")
# Stage ends as a fraction of days from sowing to harvest start (A1).
STAGE_ENDS = (("germination", 0.10), ("vegetative", 0.45), ("flowering", 0.70), ("maturing", 1.0))
# Relative daily crop-water use by stage (A1, shaped like a crop coefficient curve).
WATER_WEIGHT = {"germination": 0.5, "vegetative": 0.9, "flowering": 1.2, "maturing": 0.75, "harvest": 0.3}
# Relative daily labour by stage (A1): sowing and harvest are the busy times.
LABOUR_WEIGHT = {"germination": 2.0, "vegetative": 0.8, "flowering": 0.4, "maturing": 0.3, "harvest": 2.5}
# How much a dry spell hurts at each stage (A1). Flowering is the most sensitive.
DROUGHT_STAGE = {"germination": 0.7, "vegetative": 0.6, "flowering": 1.0, "maturing": 0.5, "harvest": 0.1}
# Share of dry-spell damage avoided with protective irrigation (A1).
IRRIGATION_PROTECTION = {"rainfed": 0.0, "limited": 0.3, "assured": 0.6}
# Visual-only weather backdrop: kharif monsoon months (A1).
MONSOON_MONTHS = {6, 7, 8, 9}
M3_PER_MM_ACRE = 4.0469  # 1 mm of water over 1 acre


@dataclass(frozen=True)
class WhatIf:
    """One shock applied to the twin. kind: none, dry_spell, pest, price, water_cut."""

    kind: str = "none"
    week: int = 6
    weeks: int = 3  # dry spell length
    severity: float = 0.5  # dry-spell intensity or pest loss (0..1)
    crop: str | None = None  # pest or price target; None for price means all crops
    change: float = -0.25  # price change as a fraction
    water: str | None = None  # new water level for water_cut

    def as_dict(self) -> dict:
        return asdict(self)


def crop_stage(crop, sow: date, harvest_start: date, harvest_end: date, day: date) -> tuple:
    """(stage, growth 0..1) on a given day. Growth reaches 1 at harvest start."""
    if day < sow:
        return "not_sown", 0.0
    if day > harvest_end:
        return "done", 1.0
    if day >= harvest_start:
        return "harvest", 1.0
    frac = (day - sow).days / max(1, (harvest_start - sow).days)
    for stage, end in STAGE_ENDS:
        if frac < end:
            return stage, frac
    return "maturing", frac


def _daily_profile(crop, a, weights: dict) -> dict:
    """Normalised daily weights over the crop's life (sow to harvest end)."""
    out, day = {}, a.sow_date
    while day <= a.harvest_end:
        out[day] = weights[crop_stage(crop, a.sow_date, a.harvest_start, a.harvest_end, day)[0]]
        day += timedelta(days=1)
    total = sum(out.values())
    return {d: w / total for d, w in out.items()}


def _season_window(plan) -> tuple:
    first = min(a.sow_date for a in plan.allocations)
    last = max(a.harvest_end for a in plan.allocations)
    start = first - timedelta(days=first.weekday() + 7)  # Monday one week before sowing
    weeks = (last - start).days // 7 + 2
    return start, weeks


def _yield_factors(plan, dataset, what: WhatIf, start: date) -> dict:
    """Yield multiplier per crop and the day it takes effect, under the what-if."""
    factors = {a.crop_id: (1.0, None) for a in plan.allocations}
    if what.kind == "none":
        return factors
    shock_day = start + timedelta(weeks=what.week)
    for a in plan.allocations:
        crop = dataset.crops[a.crop_id]
        loss = 0.0
        if what.kind == "dry_spell":
            worst = 0.0
            for d in range(what.weeks * 7):
                stage, _ = crop_stage(crop, a.sow_date, a.harvest_start, a.harvest_end, shock_day + timedelta(days=d))
                worst = max(worst, DROUGHT_STAGE.get(stage, 0.0))
            protect = IRRIGATION_PROTECTION[plan.inputs.water]
            loss = what.severity * crop.drought_sensitivity * worst * (1 - protect)
        elif what.kind == "pest" and what.crop == a.crop_id:
            if a.sow_date <= shock_day < a.harvest_start:
                loss = what.severity
        elif what.kind == "water_cut" and what.water is not None and crop.irrigation_mm > 0:
            used = plan.water_used_mm
            limit = water_limit_mm(dataset, what.water)
            if used > limit and a.sow_date <= shock_day <= a.harvest_end:
                shortfall = 1 - limit / used
                loss = shortfall * crop.irrigation_mm / crop.crop_water_mm
        if loss > 0:
            factors[a.crop_id] = (max(0.0, 1 - loss), shock_day)
    return factors


def build_twin(plan, dataset, what: WhatIf | None = None, lang: str = "en") -> dict:
    """Everything the twin view needs, week by week. Pure data, no UI."""
    what = what or WhatIf()
    start, n_weeks = _season_window(plan)
    week_starts = [start + timedelta(weeks=i) for i in range(n_weeks)]
    factors = _yield_factors(plan, dataset, what, start)
    price_day = start + timedelta(weeks=what.week)

    crops_out, stages, health, growth = [], [], [], []
    water = [0.0] * n_weeks
    irrigation = [0.0] * n_weeks
    labour = [0.0] * n_weeks
    sales = [0.0] * n_weeks
    ref_sales = [0.0] * n_weeks
    per_crop = {}

    for ci, a in enumerate(plan.allocations):
        crop = dataset.crops[a.crop_id]
        expected = a.acres * crop.gross_per_acre
        yf, yf_day = factors[a.crop_id]
        water_p = _daily_profile(crop, a, WATER_WEIGHT)
        labour_p = _daily_profile(crop, a, LABOUR_WEIGHT)
        water_total = crop.crop_water_mm * a.acres * M3_PER_MM_ACRE
        irr_total = crop.irrigation_mm * a.acres * M3_PER_MM_ACRE
        labour_total = crop.labor_days_per_acre * a.acres
        harvest_days = (a.harvest_end - a.harvest_start).days + 1
        got = 0.0
        for d, w in water_p.items():
            i = (d - start).days // 7
            water[i] += w * water_total
            irrigation[i] += w * irr_total
            labour[i] += labour_p[d] * labour_total
        day = a.harvest_start
        while day <= a.harvest_end:
            i = (day - start).days // 7
            ref = expected / harvest_days
            price_f = 1.0
            if what.kind == "price" and (what.crop in (None, a.crop_id)) and day >= price_day:
                price_f = 1 + what.change
            amount = ref * yf * price_f
            ref_sales[i] += ref
            sales[i] += amount
            got += amount
            day += timedelta(days=1)
        crop_stages, crop_health, crop_growth = [], [], []
        for ws in week_starts:
            mid = ws + timedelta(days=3)
            stage, g = crop_stage(crop, a.sow_date, a.harvest_start, a.harvest_end, mid)
            crop_stages.append(STAGES.index(stage))
            crop_growth.append(round(g, 4))
            hurt = yf_day is not None and mid >= yf_day and stage not in ("not_sown",)
            crop_health.append(round(yf if hurt else 1.0, 4))
        stages.append(crop_stages)
        health.append(crop_health)
        growth.append(crop_growth)
        per_crop[a.crop_id] = {"reference": expected, "scenario": got, "yield_factor": yf}
        crops_out.append({
            "id": a.crop_id, "share": a.share, "acres": a.acres, "strips": a.strips,
            "sow": a.sow_date.isoformat(), "harvest_start": a.harvest_start.isoformat(),
            "harvest_end": a.harvest_end.isoformat(), "index": ci,
        })

    events = []
    for a in plan.allocations:
        for key, d in (("ev_sow", a.sow_date), ("ev_flower", a.sow_date + timedelta(days=round(0.45 * (a.harvest_start - a.sow_date).days))),
                       ("ev_harvest", a.harvest_start), ("ev_done", a.harvest_end)):
            events.append({"week": (d - start).days // 7, "key": key, "crop": a.crop_id, "date": d.isoformat()})
    if what.kind != "none":
        events.append({"week": what.week, "key": f"ev_{what.kind}", "crop": what.crop, "date": price_day.isoformat()})
    events.sort(key=lambda e: (e["week"], e["date"]))

    weather = []
    for i, ws in enumerate(week_starts):
        mid = ws + timedelta(days=3)
        if what.kind == "dry_spell" and what.week <= i < what.week + what.weeks:
            weather.append("dry")
        elif plan.inputs.season == "kharif" and mid.month in MONSOON_MONTHS:
            weather.append("rain")
        else:
            weather.append("clear")

    cum, ref_cum, run, ref_run = [], [], 0.0, 0.0
    for s, r in zip(sales, ref_sales):
        run += s
        ref_run += r
        cum.append(round(run, 2))
        ref_cum.append(round(ref_run, 2))
    cost = sum(dataset.crops[a.crop_id].cost_rs_per_acre * a.acres for a in plan.allocations)
    return {
        "start": start.isoformat(),
        "weeks": [ws.isoformat() for ws in week_starts],
        "strip_order": plan.strip_order,
        "crops": crops_out,
        "stage": stages,
        "growth": growth,
        "health": health,
        "water_m3": [round(x, 2) for x in water],
        "irrigation_m3": [round(x, 2) for x in irrigation],
        "labour_days": [round(x, 3) for x in labour],
        "sales": [round(x, 2) for x in sales],
        "cum_sales": cum,
        "ref_cum_sales": ref_cum,
        "weather": weather,
        "events": events,
        "what_if": what.as_dict(),
        "totals": {
            "reference_gross": sum(v["reference"] for v in per_crop.values()),
            "scenario_gross": sum(v["scenario"] for v in per_crop.values()),
            "cost": cost,
            "water_m3": sum(water),
            "irrigation_m3": sum(irrigation),
            "labour_days": sum(labour),
            "peak_labour_week": max(range(n_weeks), key=lambda i: labour[i]),
        },
        "per_crop": per_crop,
    }
