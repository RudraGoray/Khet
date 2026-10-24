"""Printable one-page summary (HTML with inline SVG) and machine-readable plan JSON."""
from __future__ import annotations

import base64
import html
import json
from datetime import date, datetime
from pathlib import Path

from .i18n import crop_list, fmt_acres, fmt_money, fmt_rs, render_item, t
from .visualization import INK, crop_color, text_color

FONT_FILE = Path(__file__).resolve().parent.parent / "assets" / "NotoSansDevanagari.ttf"


def metric_rows(a: dict, b: dict, lang: str) -> list:
    """(label, mixed, single, difference) rows shared by the app table and the summary."""

    rs = fmt_money

    def signed(v):
        return ("−₹" if round(v) < 0 else "+₹") + fmt_rs(abs(v))

    def cv(v):
        return t("undefined", lang) if v is None else f"{v:.2f}"

    rows = [
        ("m_mean_gross", rs(a["mean_gross"]), rs(b["mean_gross"]), signed(a["mean_gross"] - b["mean_gross"])),
        ("m_cost", rs(a["cost"]), rs(b["cost"]), signed(a["cost"] - b["cost"])),
        ("m_mean_net", rs(a["mean_net"]), rs(b["mean_net"]), signed(a["mean_net"] - b["mean_net"])),
        ("m_p10_net", rs(a["p10_net"]), rs(b["p10_net"]), signed(a["p10_net"] - b["p10_net"])),
        ("m_p10_gross", rs(a["p10_gross"]), rs(b["p10_gross"]), signed(a["p10_gross"] - b["p10_gross"])),
        ("m_sd_net", rs(a["sd_net"]), rs(b["sd_net"]), signed(a["sd_net"] - b["sd_net"])),
        ("m_cv_net", cv(a["cv_net"]), cv(b["cv_net"]),
         "" if a["cv_net"] is None or b["cv_net"] is None else f"{a['cv_net'] - b['cv_net']:+.2f}"),
        ("m_prob_loss", f"{a['prob_loss']:.0%}", f"{b['prob_loss']:.0%}", f"{(a['prob_loss'] - b['prob_loss']) * 100:+.1f} pts"),
        ("m_zero_months", f"{a['mean_zero_income_months']:.1f}", f"{b['mean_zero_income_months']:.1f}",
         f"{a['mean_zero_income_months'] - b['mean_zero_income_months']:+.1f}"),
    ]
    return [(t(k, lang), x, y, d) for k, x, y, d in rows]


def verdict(comparison: dict, dataset, lang: str) -> str:
    c, a, b = comparison["cmp"], comparison["stats_mixed"], comparison["stats_single"]
    diff = c["mean_diff_net"]
    return t(
        "verdict", lang,
        share=f"{c['share_a_better']:.0%}",
        crop=crop_list([comparison["baseline"]], dataset, lang),
        diff=fmt_rs(abs(diff)),
        more_less=t("more" if diff >= 0 else "less", lang),
        p10=fmt_money(a["p10_net"]), p10b=fmt_money(b["p10_net"]),
    )


def _strip_svg(plan, dataset, lang) -> str:
    n = len(plan.strip_order)
    w, h, gap = 520, 92, 2
    sw = (w - gap * (n - 1)) / n
    parts = [f'<svg viewBox="0 0 {w} {h + 18}" width="100%" role="img" aria-label="{html.escape(t("tab_map", lang))}">']
    for i, cid in enumerate(plan.strip_order):
        x = i * (sw + gap)
        name = html.escape(dataset.crops[cid].name(lang).split(" (")[0])
        parts.append(f'<rect x="{x:.1f}" y="0" width="{sw:.1f}" height="{h}" rx="2" fill="{crop_color(dataset, cid)}"/>')
        parts.append(
            f'<text x="{x + sw / 2:.1f}" y="{h / 2}" fill="{text_color(dataset, cid)}" font-size="10" '
            f'text-anchor="middle" dominant-baseline="middle" transform="rotate(-90 {x + sw / 2:.1f} {h / 2})">{name}</text>'
        )
        parts.append(f'<text x="{x + sw / 2:.1f}" y="{h + 13}" fill="{INK}" font-size="8" text-anchor="middle">{i + 1}</text>')
    parts.append("</svg>")
    return "".join(parts)


def _calendar_svg(plan, dataset, lang) -> str:
    start = min(a.sow_date for a in plan.allocations).replace(day=1)
    end = max(a.harvest_end for a in plan.allocations)
    span = (end - start).days + 1
    label_w, w, row, pad = 120, 520, 20, 16
    h = row * len(plan.allocations) + 18
    sx = (w - label_w - pad) / span

    def x(d):
        return label_w + (d - start).days * sx

    parts = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{html.escape(t("tab_calendar", lang))}">']
    y_m, m_m = start.year, start.month
    while date(y_m, m_m, 1) <= end:
        d = date(y_m, m_m, 1)
        parts.append(f'<line x1="{x(d):.1f}" y1="0" x2="{x(d):.1f}" y2="{h - 14}" stroke="#ddd" stroke-width="1"/>')
        parts.append(f'<text x="{x(d) + 2:.1f}" y="{h - 3}" font-size="8" fill="{INK}">{d:%b %y}</text>')
        y_m, m_m = (y_m + 1, 1) if m_m == 12 else (y_m, m_m + 1)
    for i, a in enumerate(plan.allocations):
        y = i * row + 3
        color = crop_color(dataset, a.crop_id)
        name = html.escape(dataset.crops[a.crop_id].name(lang))
        parts.append(f'<text x="0" y="{y + 11}" font-size="10" fill="{INK}">{name}</text>')
        parts.append(f'<rect x="{x(a.sow_date):.1f}" y="{y}" width="{(a.harvest_start - a.sow_date).days * sx:.1f}" '
                     f'height="14" rx="3" fill="{color}" fill-opacity="0.35"/>')
        parts.append(f'<rect x="{x(a.harvest_start):.1f}" y="{y}" width="{max(((a.harvest_end - a.harvest_start).days + 1) * sx, 2):.1f}" '
                     f'height="14" rx="3" fill="{color}"/>')
    parts.append("</svg>")
    return "".join(parts)


def summary_html(plan, dataset, lang: str, comparison: dict | None = None, generated: datetime | None = None,
                 embed_font: bool = True, what_if_line: str | None = None) -> str:
    generated = generated or datetime.now()
    inp = plan.inputs
    e = html.escape
    font_css = ""
    if embed_font and lang in ("hi", "mr") and FONT_FILE.exists():
        b64 = base64.b64encode(FONT_FILE.read_bytes()).decode()
        font_css = f"@font-face{{font-family:'KhetNoto';src:url(data:font/ttf;base64,{b64}) format('truetype');}}"

    farm_rows = [
        (t("f_region", lang), t(f"region_{inp.region}", lang)),
        (t("f_area", lang), f"{inp.area_value:g} {t('unit_' + inp.area_unit, lang)} = {fmt_acres(inp.acres, lang)}"),
        (t("f_season", lang), f"{t('season_' + inp.season, lang)} {inp.year}"),
        (t("f_water", lang), t(f"water_{inp.water}", lang)),
        (t("f_risk", lang), f"{inp.risk}/100"),
    ]
    if inp.excluded_crops:
        farm_rows.append((t("f_exclude", lang), crop_list(inp.excluded_crops, dataset, lang)))
    if inp.budget_rs:
        farm_rows.append((t("f_budget", lang), "₹" + fmt_rs(inp.budget_rs)))
    farm = "".join(f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in farm_rows)

    alloc = "".join(
        f"<tr><td><span class='sw' style='background:{crop_color(dataset, a.crop_id)}'></span>{e(dataset.crops[a.crop_id].name(lang))}</td>"
        f"<td>{a.share:.0%}</td><td>{a.acres:.2f}</td><td>{a.sow_date:%d %b %Y}</td>"
        f"<td>{a.harvest_start:%d %b} – {a.harvest_end:%d %b %Y}</td></tr>"
        for a in plan.allocations
    )
    rules = "".join(f"<li>{e(render_item(item, dataset, lang))}</li>" for item in plan.explanation
                    if item["key"] in ("exp_objective", "exp_water", "exp_pairs", "exp_shares", "exp_budget"))

    if comparison:
        mixed_label = t("mixed_plan", lang)
        single_label = t("single_plan", lang, crop=crop_list([comparison["baseline"]], dataset, lang))
        rows = metric_rows(comparison["stats_mixed"], comparison["stats_single"], lang)
        body = "".join(f"<tr><th>{e(r[0])}</th><td>{e(r[1])}</td><td>{e(r[2])}</td></tr>" for r in rows)
        sim = (
            f"<h2>{e(t('sum_sim', lang))}</h2>"
            f"<p class='small'>{e(t('s4_help', lang, n=format(comparison['seasons'], ',')))} {e(t('seed_short', lang))}: {comparison['seed']}.</p>"
            f"<table class='m'><tr><th>{e(t('m_metric', lang))}</th><th>{e(mixed_label)}</th><th>{e(single_label)}</th></tr>{body}</table>"
            f"<p class='verdict'><b>{e(verdict(comparison, dataset, lang))}</b> {e(t('verdict_honest', lang))}</p>"
        )
    else:
        sim = f"<p class='small'>{e(t('no_sim_note', lang))}</p>"

    status = t(f"status_{plan.status}", lang)
    what_if_html = f"<p class='small'><b>{e(t('wi_title', lang))}:</b> {e(what_if_line)}</p>" if what_if_line else ""
    strip_area = f"{inp.acres / len(plan.strip_order):.3f} " + t("unit_acre", lang)
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(t('sum_title', lang))}</title>
<style>
{font_css}
@page {{ size: A4; margin: 9mm; }}
* {{ box-sizing: border-box; }}
body {{ font-family: 'KhetNoto','Noto Sans Devanagari','Nirmala UI','Mangal',system-ui,sans-serif; color:{INK};
       background:#fff; margin:0 auto; max-width:192mm; font-size:9.3pt; line-height:1.3; padding:4mm 0;
       -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
h1 {{ font-size:15pt; margin:0 0 1mm; color:#1d4a2c; }}
h2 {{ font-size:10.5pt; margin:2.6mm 0 1mm; color:#1d4a2c; border-bottom:1px solid #cfd8c8; padding-bottom:1mm; }}
table {{ border-collapse:collapse; width:100%; }}
th, td {{ text-align:left; padding:0.6mm 1.6mm; border-bottom:1px solid #e5e5dc; vertical-align:top; }}
th {{ font-weight:600; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:5mm; }}
.small {{ font-size:7.8pt; color:#4b5548; margin:0.6mm 0; }}
.badge {{ display:inline-block; background:#e5efe2; color:#1d4a2c; border-radius:3mm; padding:0.6mm 2.5mm; font-size:9pt; }}
.sw {{ display:inline-block; width:3mm; height:3mm; border-radius:0.8mm; margin-right:1.5mm; vertical-align:middle; }}
.m td, .m th {{ padding:0.35mm 1.6mm; font-size:8.6pt; }}
ul {{ margin:1mm 0; padding-left:5mm; }} li {{ margin:0.3mm 0; font-size:8.3pt; }}
.warn {{ border:1px solid #d9b56b; background:#fbf4e4; padding:1.4mm 2.4mm; border-radius:2mm; font-size:7.8pt; margin-top:2mm; }}
.verdict {{ margin:1.5mm 0 0; font-size:8.8pt; }}
@media print {{ body {{ padding:0; }} .noprint {{ display:none; }} }}
@media (max-width:600px) {{ .grid {{ grid-template-columns:1fr; }} body {{ padding:4mm; }} }}
</style></head><body>
<h1>{e(t('sum_title', lang))}</h1>
<p class="small">{e(t('sum_generated', lang))}: {generated:%d %b %Y %H:%M} · {e(t('sum_dataset', lang))} v{e(dataset.version)} · <span class="badge">{e(status)}</span></p>
<div class="grid">
<div><h2>{e(t('sum_farm', lang))}</h2><table>{farm}</table></div>
<div><h2>{e(t('tab_map', lang))}</h2>{_strip_svg(plan, dataset, lang)}
<p class="small">{e(t('map_caption', lang, strips=len(plan.strip_order), strip_area=strip_area))}</p></div>
</div>
<h2>{e(t('sum_plan', lang))}</h2>
<table><tr><th>{e(t('col_crop', lang))}</th><th>{e(t('col_share', lang))}</th><th>{e(t('col_area', lang))} ({e(t('unit_acre', lang))})</th><th>{e(t('col_sow', lang))}</th><th>{e(t('col_harvest', lang))}</th></tr>{alloc}</table>
{_calendar_svg(plan, dataset, lang)}
<h2>{e(t('sum_rules', lang))}</h2><ul>{rules}</ul>
{sim}
{what_if_html}
<div class="warn"><b>{e(t('sum_about', lang))}.</b> {e(t('sim_disclaimer', lang))} {e(t('sum_data_note', lang))}</div>
</body></html>"""


def plan_json(plan, dataset, comparison: dict | None = None) -> str:
    def conv(o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        raise TypeError(type(o))

    data = {
        "dataset_version": dataset.version,
        "inputs": plan.inputs.as_dict() | {"acres": plan.inputs.acres},
        "status": plan.status,
        "allocations": [
            {"crop": a.crop_id, "strips": a.strips, "share": a.share, "acres": a.acres,
             "sow": a.sow_date, "harvest_start": a.harvest_start, "harvest_end": a.harvest_end}
            for a in plan.allocations
        ],
        "strip_order": plan.strip_order,
        "irrigation_mm": {"used": plan.water_used_mm, "limit": plan.water_limit_mm},
        "direct_cost_rs": plan.cost_rs,
        "violations": plan.violations,
        "note": "Synthetic demonstration data. Illustrative simulation, not a forecast.",
    }
    if comparison:
        keep = ("mean_gross", "mean_net", "sd_net", "cv_net", "p10_net", "p10_gross", "prob_loss", "mean_zero_income_months", "cost")
        data["comparison"] = {
            "seasons": comparison["seasons"], "seed": comparison["seed"], "baseline_crop": comparison["baseline"],
            "mixed": {k: comparison["stats_mixed"][k] for k in keep},
            "single": {k: comparison["stats_single"][k] for k in keep},
            "share_mixed_better": comparison["cmp"]["share_a_better"],
            "mean_diff_net": comparison["cmp"]["mean_diff_net"],
        }
    return json.dumps(data, default=conv, ensure_ascii=False, indent=2)
