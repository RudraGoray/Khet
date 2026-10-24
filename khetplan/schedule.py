"""Sowing and harvest calendar derived from the dataset (all dates are A1 assumptions)."""
from __future__ import annotations

from datetime import date, timedelta

SEASON_START_MONTH = {"kharif": 6, "rabi": 9}  # first month of the 12-month income horizon


def sow_date(crop, year: int) -> date:
    month, day = (int(x) for x in crop.sow_start.split("-"))
    return date(year, month, day)


def crop_dates(crop, year: int) -> tuple:
    """(sow, harvest_start, harvest_end) for a crop sown at its window start."""
    sow = sow_date(crop, year)
    start = sow + timedelta(days=crop.duration_days)
    end = start + timedelta(days=crop.harvest_days - 1)
    return sow, start, end


def horizon_months(season: str, year: int) -> list:
    """Twelve (year, month) tuples starting at the season's first month."""
    y, m = year, SEASON_START_MONTH[season]
    months = []
    for _ in range(12):
        months.append((y, m))
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return months


def harvest_month_weights(crop, year: int, season: str):
    """Fraction of the crop's harvest (and sales) that falls in each horizon month.

    Revenue is assumed to arrive evenly across the harvest window (A1: no storage, sold as harvested).
    """
    import numpy as np

    months = horizon_months(season, year)
    index = {ym: i for i, ym in enumerate(months)}
    weights = np.zeros(len(months))
    _, start, end = crop_dates(crop, year)
    day = start
    while day <= end:
        i = index.get((day.year, day.month))
        if i is not None:
            weights[i] += 1
        day += timedelta(days=1)
    total = weights.sum()
    if total == 0:
        raise ValueError(f"Harvest of {crop.id} falls outside the 12-month horizon")
    return weights / total


def harvest_months(crop, year: int, season: str) -> set:
    w = harvest_month_weights(crop, year, season)
    return {i for i, x in enumerate(w) if x > 0}
