"""Load and validate the versioned demonstration crop dataset."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

NUMERIC_FIELDS = {
    "duration_days": int,
    "harvest_days": int,
    "irrigation_mm": int,
    "crop_water_mm": int,
    "labor_days_per_acre": float,
    "yield_q_per_acre": float,
    "price_rs_per_q": float,
    "cost_rs_per_acre": float,
    "yield_cv": float,
    "price_cv": float,
    "drought_sensitivity": float,
    "failure_prob": float,
    "min_share": float,
    "max_share": float,
}


class DatasetError(ValueError):
    """Raised when a data file is missing fields or holds invalid values."""


@dataclass(frozen=True)
class Crop:
    id: str
    names: dict  # language code -> display name
    region: str
    season: str
    sow_start: str  # MM-DD
    sow_end: str
    duration_days: int
    harvest_days: int
    irrigation_mm: int
    crop_water_mm: int
    labor_days_per_acre: float
    yield_q_per_acre: float
    price_rs_per_q: float
    cost_rs_per_acre: float
    yield_cv: float
    price_cv: float
    drought_sensitivity: float
    failure_prob: float
    min_share: float
    max_share: float
    value_basis: str

    def name(self, lang: str = "en") -> str:
        return self.names.get(lang) or self.names["en"]

    @property
    def gross_per_acre(self) -> float:
        """Normal-season gross revenue per acre, before any risk."""
        return self.yield_q_per_acre * self.price_rs_per_q

    @property
    def margin_per_acre(self) -> float:
        """Normal-season gross revenue minus direct cash cost, per acre."""
        return self.gross_per_acre - self.cost_rs_per_acre


@dataclass(frozen=True)
class ExcludedCrop:
    id: str
    names: dict
    region: str
    season: str
    reason: str

    def name(self, lang: str = "en") -> str:
        return self.names.get(lang) or self.names["en"]


@dataclass
class Dataset:
    crops: dict  # id -> Crop (enabled only)
    excluded: dict  # id -> ExcludedCrop
    pairs: dict  # season -> set of frozenset pairs
    pair_basis: dict
    sim: dict
    meta: dict
    color_slot: dict = field(default_factory=dict)  # crop id -> palette index

    @property
    def version(self) -> str:
        return self.meta["version"]

    def regions(self) -> dict:
        return self.meta["coverage"]["regions"]

    def seasons(self) -> list:
        return self.meta["coverage"]["seasons"]

    def crops_for(self, region: str, season: str) -> list:
        return [c for c in self.crops.values() if c.region == region and c.season == season]

    def compatible(self, a: str, b: str, season: str) -> bool:
        return frozenset((a, b)) in self.pairs.get(season, set())


def _parse_crop_row(row: dict, line: int) -> Crop:
    values = {}
    for name, cast in NUMERIC_FIELDS.items():
        raw = (row.get(name) or "").strip()
        if raw == "":
            raise DatasetError(f"crops.csv line {line}: '{name}' is empty for enabled crop '{row['id']}'")
        try:
            values[name] = cast(raw)
        except ValueError as exc:
            raise DatasetError(f"crops.csv line {line}: '{name}' is not a number ({raw!r})") from exc
    for name in ("yield_cv", "price_cv", "drought_sensitivity", "failure_prob"):
        if not 0 <= values[name] <= 1:
            raise DatasetError(f"crops.csv line {line}: '{name}' must be between 0 and 1")
    if not 0 < values["min_share"] <= values["max_share"] <= 1:
        raise DatasetError(f"crops.csv line {line}: need 0 < min_share <= max_share <= 1")
    for name in ("duration_days", "harvest_days", "yield_q_per_acre", "price_rs_per_q", "crop_water_mm"):
        if values[name] <= 0:
            raise DatasetError(f"crops.csv line {line}: '{name}' must be positive")
    if values["irrigation_mm"] < 0 or values["cost_rs_per_acre"] < 0 or values["labor_days_per_acre"] < 0:
        raise DatasetError(f"crops.csv line {line}: negative irrigation, cost or labour")
    if values["irrigation_mm"] > values["crop_water_mm"]:
        raise DatasetError(f"crops.csv line {line}: irrigation_mm cannot exceed crop_water_mm")
    for name in ("sow_start", "sow_end"):
        mm, _, dd = row[name].partition("-")
        if not (mm.isdigit() and dd.isdigit() and 1 <= int(mm) <= 12 and 1 <= int(dd) <= 31):
            raise DatasetError(f"crops.csv line {line}: '{name}' must be MM-DD")
    return Crop(
        id=row["id"],
        names={"en": row["name_en"], "hi": row["name_hi"], "mr": row["name_mr"]},
        region=row["region"],
        season=row["season"],
        sow_start=row["sow_start"],
        sow_end=row["sow_end"],
        value_basis=row["value_basis"],
        **values,
    )


def load_dataset(data_dir: Path = DATA_DIR) -> Dataset:
    meta = json.loads((data_dir / "metadata.json").read_text(encoding="utf-8"))
    sim = json.loads((data_dir / "simulation_config.json").read_text(encoding="utf-8"))
    compat = json.loads((data_dir / "compatibility.json").read_text(encoding="utf-8"))

    crops, excluded = {}, {}
    with open(data_dir / "crops.csv", encoding="utf-8", newline="") as fh:
        for line, row in enumerate(csv.DictReader(fh), start=2):
            if row["id"] in crops or row["id"] in excluded:
                raise DatasetError(f"crops.csv line {line}: duplicate id '{row['id']}'")
            if row["region"] not in meta["coverage"]["regions"]:
                raise DatasetError(f"crops.csv line {line}: region '{row['region']}' not in metadata coverage")
            if row["season"] not in meta["coverage"]["seasons"]:
                raise DatasetError(f"crops.csv line {line}: season '{row['season']}' not in metadata coverage")
            names = {"en": row["name_en"], "hi": row["name_hi"], "mr": row["name_mr"]}
            if row["status"] == "excluded":
                if not row["exclusion_reason"]:
                    raise DatasetError(f"crops.csv line {line}: excluded crop needs a reason")
                excluded[row["id"]] = ExcludedCrop(row["id"], names, row["region"], row["season"], row["exclusion_reason"])
            elif row["status"] == "enabled":
                crops[row["id"]] = _parse_crop_row(row, line)
            else:
                raise DatasetError(f"crops.csv line {line}: status must be enabled or excluded")

    pairs = {}
    for season, plist in compat["supported_pairs"].items():
        pairs[season] = set()
        for a, b in plist:
            for cid in (a, b):
                if cid not in crops or crops[cid].season != season:
                    raise DatasetError(f"compatibility.json: '{cid}' is not an enabled {season} crop")
            pairs[season].add(frozenset((a, b)))

    probs = sum(w["probability"] for w in sim["weather_states"])
    if abs(probs - 1) > 1e-9:
        raise DatasetError("simulation_config.json: weather probabilities must sum to 1")

    # Fixed colour slot per crop, assigned within each season so a plan never repeats a colour.
    color_slot = {}
    for season in meta["coverage"]["seasons"]:
        for i, c in enumerate(c for c in crops.values() if c.season == season):
            color_slot[c.id] = i
    return Dataset(crops, excluded, pairs, compat["basis"], sim, meta, color_slot)


@lru_cache(maxsize=1)
def default_dataset() -> Dataset:
    return load_dataset()
