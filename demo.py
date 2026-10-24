"""Run the whole planning journey without the UI and write example outputs.

    python demo.py            # writes samples/generated/
"""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

from khetplan.data import default_dataset
from khetplan.export import plan_json, summary_html, verdict
from khetplan.models import FarmInputs, default_year
from khetplan.optimizer import monoculture_candidates, solve_intercrop
from khetplan.parsing import parse_transcript
from khetplan.simulation import run_comparison

OUT = Path(__file__).resolve().parent / "samples" / "generated"


def main():
    ds = default_dataset()
    samples = json.loads((OUT.parent / "sample_inputs.json").read_text(encoding="utf-8"))["examples"]
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime(2026, 10, 24, 9, 0)  # fixed so regenerated files only change when results change
    for i, sample in enumerate(samples, start=1):
        print(f"\n[{i}] ({sample['lang']}) {sample['text']}")
        parsed = parse_transcript(sample["text"])
        f = parsed.fields
        if parsed.missing or parsed.issues:
            print(f"    needs farmer input: missing={parsed.missing} issues={[k for k, _ in parsed.issues]}")
            continue
        inp = FarmInputs(region=f["region"], area_value=f["area_value"], area_unit=f["area_unit"], season=f["season"],
                         year=f.get("year") or default_year(f["season"], stamp.date()), water=f["water"], risk=f["risk"])
        t0 = time.perf_counter()
        res = solve_intercrop(inp, ds)
        t1 = time.perf_counter()
        if not res.plan:
            print(f"    {res.status}: {res.reasons}")
            continue
        plan = res.plan
        comp = run_comparison(plan, monoculture_candidates(inp, ds)[0], ds)
        t2 = time.perf_counter()
        print(f"    {res.status} in {t1 - t0:.2f}s: " + ", ".join(f"{a.crop_id} {a.share:.0%}" for a in plan.allocations))
        print(f"    1,000 seasons in {t2 - t1:.2f}s. {verdict(comp, ds, 'en')}")
        name = f"example{i}_{sample['lang']}"
        (OUT / f"{name}_summary.html").write_text(summary_html(plan, ds, sample["lang"], comp, stamp), encoding="utf-8")
        (OUT / f"{name}_plan.json").write_text(plan_json(plan, ds, comp), encoding="utf-8")
    print(f"\nWrote outputs to {OUT}")


if __name__ == "__main__":
    main()
