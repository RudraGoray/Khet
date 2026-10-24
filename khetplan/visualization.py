"""Plotly figures. Every figure is drawn from a validated Plan or simulation Outcome."""
from __future__ import annotations

from datetime import datetime, time

import numpy as np
import plotly.graph_objects as go

from .i18n import fmt_rs, t
from .schedule import horizon_months

# Categorical palette (validated reference order); a crop keeps its slot on every chart.
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
LIGHT_FILLS = {2, 3, 4}  # slots below 3:1 contrast with white text: label them in dark ink
INK, INK_MUTED, GRID = "#1f2a22", "#5b6559", "#e4e2d8"
MIXED_COLOR, SINGLE_COLOR = PALETTE[0], PALETTE[1]
FONT = "Noto Sans Devanagari, Noto Sans, system-ui, sans-serif"

MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "hi": ["जन", "फ़र", "मार्च", "अप्रै", "मई", "जून", "जुला", "अग", "सित", "अक्टू", "नव", "दिस"],
    "mr": ["जाने", "फेब्रु", "मार्च", "एप्रि", "मे", "जून", "जुलै", "ऑग", "सप्टें", "ऑक्टो", "नोव्हें", "डिसें"],
}


def crop_color(dataset, crop_id: str) -> str:
    return PALETTE[dataset.color_slot.get(crop_id, 0) % len(PALETTE)]


def text_color(dataset, crop_id: str) -> str:
    return INK if dataset.color_slot.get(crop_id, 0) % len(PALETTE) in LIGHT_FILLS else "#ffffff"


def _layout(fig, height=320, **kw):
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=36, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=14, color=INK),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=13)),
        hoverlabel=dict(font=dict(family=FONT, size=14)),
        **kw,
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, color=INK_MUTED)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, color=INK_MUTED)
    return fig


def bed_map(plan, dataset, lang: str) -> go.Figure:
    """Schematic field as equal vertical strips, labelled with crop names."""
    strip_acres = plan.inputs.acres / len(plan.strip_order)
    fig = go.Figure()
    for a in plan.allocations:
        crop = dataset.crops[a.crop_id]
        xs = [i + 1 for i, cid in enumerate(plan.strip_order) if cid == a.crop_id]
        fig.add_bar(
            x=xs, y=[1] * len(xs), width=0.92, name=f"{crop.name(lang)} · {a.share:.0%}",
            marker=dict(color=crop_color(dataset, a.crop_id), line=dict(width=0)),
            text=[crop.name(lang).split(" (")[0]] * len(xs), textposition="inside", insidetextanchor="middle",
            textangle=-90, textfont=dict(color=text_color(dataset, a.crop_id), size=13),
            hovertemplate=f"{crop.name(lang)}<br>#%{{x}} · {strip_acres:.3f} {t('unit_acre', lang)}<extra></extra>",
        )
    _layout(fig, height=300, barmode="overlay", bargap=0)
    fig.update_xaxes(title=t("col_strips", lang), dtick=1, range=[0.5, len(plan.strip_order) + 0.5], showgrid=False)
    fig.update_yaxes(visible=False, range=[0, 1])
    fig.update_layout(uniformtext=dict(minsize=9, mode="hide"))
    return fig


def calendar(plan, dataset, lang: str) -> go.Figure:
    """Growing period (pale) and harvest window (solid) for each crop."""
    fig = go.Figure()
    names = [dataset.crops[a.crop_id].name(lang) for a in plan.allocations]
    ms_day = 24 * 3600 * 1000
    for a, name in zip(plan.allocations, names):
        color = crop_color(dataset, a.crop_id)
        grow_days = (a.harvest_start - a.sow_date).days
        harvest_days = (a.harvest_end - a.harvest_start).days + 1
        fig.add_bar(
            y=[name], x=[grow_days * ms_day], base=[datetime.combine(a.sow_date, time())], orientation="h",
            marker=dict(color=color, opacity=0.35), name=t("growing", lang), legendgroup="grow",
            showlegend=a is plan.allocations[0],
            hovertemplate=f"{name}<br>{t('col_sow', lang)}: {a.sow_date:%d %b %Y}<extra></extra>",
        )
        fig.add_bar(
            y=[name], x=[harvest_days * ms_day], base=[datetime.combine(a.harvest_start, time())], orientation="h",
            marker=dict(color=color), name=t("harvesting", lang), legendgroup="harvest",
            showlegend=a is plan.allocations[0],
            hovertemplate=f"{name}<br>{t('col_harvest', lang)}: {a.harvest_start:%d %b} – {a.harvest_end:%d %b %Y}<extra></extra>",
        )
    _layout(fig, height=110 + 48 * len(names), barmode="overlay")
    fig.update_xaxes(type="date", tickformat="%b %Y")
    fig.update_yaxes(autorange="reversed")
    return fig


def distribution(mixed, single, labels: tuple, lang: str) -> go.Figure:
    fig = go.Figure()
    lo = min(mixed.net.min(), single.net.min())
    hi = max(mixed.net.max(), single.net.max())
    size = max((hi - lo) / 40, 1)
    for out, label, color in ((mixed, labels[0], MIXED_COLOR), (single, labels[1], SINGLE_COLOR)):
        fig.add_histogram(
            x=out.net, name=label, marker=dict(color=color, line=dict(width=1, color="#fbfaf5")), opacity=0.6,
            xbins=dict(start=lo, end=hi + size, size=size),
            hovertemplate=f"{label}<br>₹%{{x}}<br>%{{y}}<extra></extra>",
        )
        p10 = float(np.percentile(out.net, 10))
        fig.add_vline(x=p10, line=dict(color=color, width=2, dash="dash"))
    fig.add_annotation(x=0, xref="paper", y=1, yref="paper", yanchor="bottom", showarrow=False,
                       text=f"- - {t('p10_line', lang)}", font=dict(size=12, color=INK_MUTED), xanchor="left", yshift=-18)
    _layout(fig, barmode="overlay")
    fig.update_xaxes(title=t("axis_net", lang), tickprefix="₹")
    fig.update_yaxes(title=t("axis_seasons", lang))
    return fig


def monthly(mixed_stats, single_stats, labels: tuple, season: str, year: int, lang: str) -> go.Figure:
    months = horizon_months(season, year)
    names = [f"{MONTHS[lang][m - 1]} {str(y)[2:]}" for y, m in months]
    fig = go.Figure()
    for stats, label, color in ((mixed_stats, labels[0], MIXED_COLOR), (single_stats, labels[1], SINGLE_COLOR)):
        fig.add_bar(
            x=names, y=stats["monthly_mean_gross"], name=label, marker=dict(color=color),
            customdata=[fmt_rs(v) for v in stats["monthly_mean_gross"]],
            hovertemplate=f"{label}<br>%{{x}}: ₹%{{customdata}}<extra></extra>",
        )
    _layout(fig, barmode="group", bargap=0.25, bargroupgap=0.06)
    fig.update_yaxes(title=t("axis_gross_month", lang), tickprefix="₹")
    return fig


def difference(diff: np.ndarray, lang: str) -> go.Figure:
    fig = go.Figure()
    fig.add_histogram(x=diff, nbinsx=40, marker=dict(color="#7d8b7a", line=dict(width=1, color="#fbfaf5")),
                      hovertemplate="₹%{x}<br>%{y}<extra></extra>", showlegend=False)
    fig.add_vline(x=0, line=dict(color=INK, width=2))
    _layout(fig, height=280)
    fig.update_xaxes(title=t("axis_diff", lang), tickprefix="₹")
    fig.update_yaxes(title=t("axis_seasons", lang))
    return fig


def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{alpha})"


def monthly_band(mixed_stats, single_stats, labels: tuple, season: str, year: int, lang: str) -> go.Figure:
    """Monthly gross revenue: mean line with a 10th–90th percentile band for each plan."""
    months = horizon_months(season, year)
    names = [f"{MONTHS[lang][m - 1]} {str(y)[2:]}" for y, m in months]
    fig = go.Figure()
    for stats, label, color in ((single_stats, labels[1], SINGLE_COLOR), (mixed_stats, labels[0], MIXED_COLOR)):
        fig.add_scatter(x=names, y=stats["monthly_p90_gross"], mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip")
        fig.add_scatter(x=names, y=stats["monthly_p10_gross"], mode="lines", line=dict(width=0), fill="tonexty",
                        fillcolor=_rgba(color, 0.16), showlegend=False, hoverinfo="skip")
        fig.add_scatter(
            x=names, y=stats["monthly_mean_gross"], mode="lines+markers", name=label,
            line=dict(color=color, width=2), marker=dict(size=8, color=color, line=dict(width=2, color="#ffffff")),
            customdata=[[fmt_rs(a), fmt_rs(b), fmt_rs(c)] for a, b, c in zip(stats["monthly_mean_gross"], stats["monthly_p10_gross"], stats["monthly_p90_gross"])],
            hovertemplate=f"{label}<br>%{{x}}: ₹%{{customdata[0]}}<br>P10–P90: ₹%{{customdata[1]}} – ₹%{{customdata[2]}}<extra></extra>",
        )
    _layout(fig, height=340, hovermode="x unified")
    fig.update_yaxes(title=t("axis_gross_month", lang), tickprefix="₹", rangemode="tozero")
    return fig

