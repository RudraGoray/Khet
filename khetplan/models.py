"""Farm inputs, units and the plan data structures shared across modules."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date

ACRES_PER_UNIT = {
    "acre": 1.0,
    "hectare": 2.4710538,
    "guntha": 1 / 40,  # 40 guntha = 1 acre (Maharashtra usage)
}
MIN_ACRES, MAX_ACRES = 0.1, 50.0
WATER_LEVELS = ("rainfed", "limited", "assured")


def to_acres(value: float, unit: str) -> float:
    if unit not in ACRES_PER_UNIT:
        raise ValueError(f"Unsupported area unit '{unit}'")
    if value is None or value <= 0:
        raise ValueError("Area must be greater than zero")
    return value * ACRES_PER_UNIT[unit]


@dataclass
class FarmInputs:
    region: str | None = None
    area_value: float | None = None
    area_unit: str = "acre"
    season: str | None = None
    year: int | None = None
    water: str | None = None
    risk: int = 50  # 0 = chase returns, 100 = most cautious
    excluded_crops: tuple = ()
    budget_rs: float | None = None  # optional cash budget for direct costs

    @property
    def acres(self) -> float:
        return to_acres(self.area_value, self.area_unit)

    def as_dict(self) -> dict:
        d = asdict(self)
        d["excluded_crops"] = list(self.excluded_crops)
        return d

    def key(self) -> tuple:
        """Hashable fingerprint, used to detect stale results after edits."""
        return tuple(sorted((k, tuple(v) if isinstance(v, list) else v) for k, v in self.as_dict().items()))


def default_year(season: str, today: date | None = None) -> int:
    """Next season whose earliest sowing date (in the dataset) is still ahead, so no sowing date is in the past."""
    today = today or date.today()
    first_sow = {"kharif": (6, 20), "rabi": (9, 25)}.get(season, (12, 31))
    return today.year if (today.month, today.day) <= first_sow else today.year + 1


def check_inputs(inputs: FarmInputs, dataset) -> list:
    """Return a list of (field, message_key, detail) problems. Empty means usable."""
    problems = []
    if not inputs.region:
        problems.append(("region", "err_missing", ""))
    elif inputs.region not in dataset.regions():
        problems.append(("region", "err_region_unsupported", inputs.region))
    if inputs.area_value is None:
        problems.append(("area", "err_missing", ""))
    else:
        try:
            acres = inputs.acres
            if not MIN_ACRES <= acres <= MAX_ACRES:
                problems.append(("area", "err_area_range", f"{acres:.2f}"))
        except ValueError:
            problems.append(("area", "err_area_unit", inputs.area_unit))
    if not inputs.season:
        problems.append(("season", "err_missing", ""))
    elif inputs.season not in dataset.seasons():
        problems.append(("season", "err_season_unsupported", inputs.season))
    if inputs.year is None or not 2024 <= inputs.year <= 2035:
        problems.append(("year", "err_missing", ""))
    if inputs.water not in WATER_LEVELS:
        problems.append(("water", "err_missing", ""))
    if not 0 <= inputs.risk <= 100:
        problems.append(("risk", "err_missing", ""))
    if inputs.budget_rs is not None and inputs.budget_rs <= 0:
        problems.append(("budget", "err_budget", ""))
    return problems


@dataclass
class Allocation:
    crop_id: str
    strips: int
    acres: float
    share: float
    sow_date: date
    harvest_start: date
    harvest_end: date


@dataclass
class Plan:
    inputs: FarmInputs
    allocations: list
    strip_order: list  # crop id for each strip, left to right
    status: str  # OPTIMAL / FEASIBLE
    kind: str  # "intercrop" or "monoculture"
    objective: float = 0.0
    water_used_mm: float = 0.0
    water_limit_mm: float = 0.0
    cost_rs: float = 0.0
    violations: list = field(default_factory=list)
    explanation: list = field(default_factory=list)  # (key, params) pairs for i18n

    @property
    def crop_ids(self) -> list:
        return [a.crop_id for a in self.allocations]

    @property
    def feasible(self) -> bool:
        return not self.violations


@dataclass
class SolveResult:
    status: str  # OPTIMAL, FEASIBLE, INFEASIBLE, TIMEOUT, INVALID_INPUT, ERROR
    plan: Plan | None = None
    reasons: list = field(default_factory=list)  # (key, params) pairs for i18n
