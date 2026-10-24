"""Independent plan checker. It re-derives every hard constraint from the dataset and
does not reuse optimizer code, so a solver bug cannot mark its own plan as feasible."""
from __future__ import annotations

from itertools import combinations

AREA_TOL = 1e-6
RESOURCE_TOL = 1e-6


def water_limit_mm(dataset, water: str) -> float:
    return float(dataset.sim["water_levels_mm"][water])


def validate_plan(plan, dataset) -> list:
    """Return human-readable violation strings. An empty list means the plan is valid."""
    v = []
    inp = plan.inputs
    total_acres = inp.acres
    strips = dataset.sim["strips"]
    max_crops = dataset.sim["max_crops"]
    ids = plan.crop_ids

    if len(set(ids)) != len(ids):
        v.append("A crop appears more than once")
    area = sum(a.acres for a in plan.allocations)
    if abs(area - total_acres) > AREA_TOL:
        v.append(f"Allocated area {area:.4f} acres does not equal plot area {total_acres:.4f} acres")
    if sum(a.strips for a in plan.allocations) != strips or len(plan.strip_order) != strips:
        v.append(f"Strip count does not add up to {strips}")
    for a in plan.allocations:
        if plan.strip_order.count(a.crop_id) != a.strips:
            v.append(f"Bed map shows a different number of strips for {a.crop_id}")
        if a.strips <= 0 or a.acres <= 0:
            v.append(f"{a.crop_id} has a non-positive allocation")

    for cid in ids:
        crop = dataset.crops.get(cid)
        if crop is None:
            v.append(f"{cid} is not an enabled crop in dataset {dataset.version}")
            continue
        if crop.region != inp.region or crop.season != inp.season:
            v.append(f"{cid} is not available for {inp.region} / {inp.season}")
        if cid in inp.excluded_crops:
            v.append(f"{cid} was excluded by the farmer")

    if plan.kind == "intercrop":
        if not 2 <= len(ids) <= max_crops:
            v.append(f"Intercrop plan must have 2 to {max_crops} crops, has {len(ids)}")
        for a in plan.allocations:
            crop = dataset.crops.get(a.crop_id)
            if crop is None:
                continue
            # Shares are counted in whole strips, the same discretisation the farmer sees.
            share = a.strips / strips
            if share + 1e-9 < crop.min_share or share - 1e-9 > crop.max_share:
                v.append(f"{a.crop_id} share {share:.0%} is outside {crop.min_share:.0%}-{crop.max_share:.0%}")
        for x, y in combinations(ids, 2):
            if not dataset.compatible(x, y, inp.season):
                v.append(f"{x} + {y} is not a supported pair in the dataset")
    elif plan.kind == "monoculture":
        if len(ids) != 1:
            v.append("Monoculture baseline must have exactly one crop")
    else:
        v.append(f"Unknown plan kind {plan.kind}")

    limit = water_limit_mm(dataset, inp.water)
    used = sum(dataset.crops[a.crop_id].irrigation_mm * a.acres for a in plan.allocations if a.crop_id in dataset.crops)
    used_mm = used / total_acres if total_acres else 0
    if used_mm > limit + RESOURCE_TOL:
        v.append(f"Irrigation need {used_mm:.1f} mm exceeds available {limit:.0f} mm")

    if inp.budget_rs is not None:
        cost = sum(dataset.crops[a.crop_id].cost_rs_per_acre * a.acres for a in plan.allocations if a.crop_id in dataset.crops)
        if cost > inp.budget_rs + RESOURCE_TOL:
            v.append(f"Direct cost ₹{cost:,.0f} exceeds budget ₹{inp.budget_rs:,.0f}")
    return v
