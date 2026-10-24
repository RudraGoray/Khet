# KhetPlan: voice-first farm digital twin (ideathon prototype)

KhetPlan helps a smallholder farmer plan a mixed-crop season and **watch it play out on a 3D digital twin of their field**. The farmer speaks or types their details in Hindi, Marathi or English, checks what was understood, and gets:

1. a **3D model of their plot** drawn to scale (it appears as soon as the plot size is known), which is then planted with the plan's crops in strips and **grows week by week**: sowing, germination, flowering, ripening and harvest, with monsoon rain, dry spells, pests, drip lines and a well or borewell, plus live sales, water and labour figures. Play, pause, step, scrub, change speed and orbit the camera.
2. a **what-if lab**: hit the twin with a dry spell, a pest attack, a price change or a water cut, and replay the season to see what happens to the crops and the money. For a water cut, KhetPlan can **re-plan** for the lower water level and plant the new plan on the twin.
3. a crop allocation that satisfies every hard rule, checked by an independent validator, with a table, calendar and a plain-language "why this plan",
4. a comparison against a valid single-crop plan over 1,000 simulated seasons (the risk lab), and
5. a one-page printable summary built from those exact results.

> **Prototype.** All crop numbers are synthetic demonstration values for **Buldhana district, Maharashtra (kharif and rabi only)**. The simulation is illustrative, not a forecast or a guarantee. Do not use it for real planting decisions.

No LLM, paid API or account is needed. The only network use is optional browser speech recognition (see [Voice](#voice-input)).

---

## Install and run

Python **3.11 or newer** (verified on 3.13.17, Linux). From inside this folder:

**macOS / Linux**
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

**Windows (PowerShell)**
```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
```

Open the address Streamlit prints (normally http://localhost:8501). It opens on the **landing page**; **Launch KhetPlan** takes you to the dashboard, which also has its own address, http://localhost:8501/app. Use `--server.port 8502` if 8501 is busy. Use Chrome or Edge on `localhost` or `https` if you want voice input.

**Tests and a command-line demo**
```bash
.venv/bin/python -m pytest -q tests          # 120 tests
.venv/bin/python demo.py                     # parses the sample transcripts, plans, simulates, writes samples/generated/
```

## Landing page

`/` is an animated scroll story in front of the dashboard. It explains the product in six sections: a 3D hero farm, three steps (tell us, plan, watch), a pinned season showcase, a what-if lab, features, and a closing call to action. Every **Launch KhetPlan** and **Explore My Farm** button opens the real dashboard at `/app`, and the dashboard has a **Home** link back.

- **Nothing on it is made up.** The landing page shows one sample farm (2 acres, Buldhana, kharif 2027, limited water, medium risk), and every number is computed when the page loads by the same modules the app uses (`khetplan/landing_view.py`). The parser reads the three sample sentences (English, Hindi, Marathi), CP-SAT plans the farm, the twin builds the season, the four what-ifs are replayed (and a re-plan for the water cut), and the risk lab runs 1,000 seasons. Labels say it is a sample with synthetic data. There are no testimonials, user counts or invented statistics.
- **3D.** The hero, season showcase, what-if lab and closing section draw one fixed WebGL farm behind the page. Scrolling moves its camera and season (the season showcase is scroll-driven week by week, using the project's stage names). It shares its crop, tree, house and texture code with the dashboard twin through `components/twin/farmkit.js`, so plants look the same in both.
- **Motion.** Staggered hero text, scroll-linked camera fly-in, pinned story and season sections, word-by-word heading reveals, image reveal masks, parallax, hover states and a launch "curtain". It uses no animation library: a small scroll loop plus CSS transitions. With **reduced motion** turned on in the OS, everything appears in place without movement.
- **Responsive.** On phones the nav becomes an accessible menu (keyboard and Escape work), the story steps stack with their own visuals, and the 3D quality drops to keep scrolling smooth.
- **Type.** Fraunces and Inter (SIL OFL), bundled in `components/landing/fonts/` (see `FONTS.txt`), plus Noto Sans Devanagari. Like the twin, the page needs no internet.

How it plugs in: `app.py` is now a small router (`st.navigation`): `/` runs `landing.py`, and `/app` runs `dashboard.py`, which is the former `app.py` unchanged apart from the Home link. The landing page is a Streamlit component pinned to the full window. Its launch buttons send a value back to Python, which calls `st.switch_page`, so the dashboard opens in the same session.

## Using the app

The screen has two halves: the **3D field** on the right (on a phone it comes first once a plan exists) and a control panel on the left.

| Stage | What happens |
|---|---|
| **1. Talk to KhetPlan** | Pick a language. Press **Speak** (Chrome/Edge), type in the box, or tap an example. Press **Read my details**. You can also just fill the form. |
| **2. Check what we understood** | The transcript is shown, and every field is editable: district, plot size and unit (acre, guntha, hectare), season and year, water (rain only, limited, assured), and a risk slider. Fields read from speech are marked ✓, and missing ones are flagged. Optional extras let you exclude crops or set a cash budget. While you edit, the 3D preview shows an empty plot of your size with your water source. Tick **These details are correct**, then press **🌱 Build my farm plan**. |
| **3. Watch the season** | The camera flies in, the strips are planted, and the season starts playing. The top-left card shows the date, week and weather. The top-right card shows sales so far, water and labour this week. The crop panel shows each crop's stage, growth and health, and the mini chart shows weekly water and cumulative sales. Toasts mark sowing, flowering, harvest and shocks. Hover a strip for details. |
| **4. What-if lab** | Choose a shock (dry spell, pest, price change, water cut), set when and how strong it is, and press **Apply to twin**. The twin replays from just before the shock, shows the damage (yellowing, pests, dry soil), and the panel shows the change in season revenue for each crop. For a water cut that the plan does not fit, **Re-plan for this water** solves again and plants the new plan. |
| **Below the field** | **Plan & rules**: table, calendar, strip map, "why this plan" and the independent rule checks. **Risk lab**: 1,000 paired simulated seasons against a single-crop baseline. **Report**: the printable one-page summary (with the active what-if noted) and the plan JSON. |

If you change any detail after planning, the old plan, twin, comparison and summary are hidden until you confirm and build again.

## Project layout

```
app.py                       Entry point: routes / to landing.py and /app to dashboard.py
landing.py                   Landing page (full-window component; launch buttons switch to the dashboard)
dashboard.py                 Streamlit dashboard: voice + details panel, 3D twin, what-if lab, tabs below
demo.py                      Headless end-to-end run over samples/sample_inputs.json
khetplan/
  data.py                    Loads + validates the versioned dataset (raises DatasetError on bad files)
  models.py                  FarmInputs, units, input checks, Plan / Allocation / SolveResult
  parsing.py                 Rule-based transcript → fields (hi / mr / en, number words, Devanagari digits)
  optimizer.py               OR-Tools CP-SAT allocation, infeasibility diagnosis, monoculture baselines
  validation.py              Independent hard-constraint checker (shares no code with the optimizer)
  schedule.py                Sowing / harvest dates and month weights
  simulation.py              NumPy Monte Carlo with common random numbers, metrics, paired comparison
  visualization.py           Plotly strip map, calendar, distribution, monthly and difference charts
  export.py                  One-page A4 HTML summary (inline SVG) and plan JSON
  i18n.py                    English / Hindi / Marathi text and explanation rendering
  speech.py                  Streamlit bridge to the browser speech component
  twin.py                    Digital-twin timeline: weekly stages, growth, health, water, labour, sales, what-if shocks
  twin_view.py               Streamlit bridge to the 3D component (crop looks, plot facts, labels)
  landing_view.py            Landing-page data (sample farm through the real modules) and its component bridge
components/speech/index.html Web Speech API component (no build step)
components/twin/             3D field: index.html (HUD), twin.js (Three.js scene), farmkit.js (shared world and crop drawing), vendor/ (Three.js r170, MIT, bundled offline)
components/index.html        Landing page markup (component root is components/ so it can reuse twin/farmkit.js and twin/vendor/)
components/landing/          landing.css, landing.js (scroll story, launch), farm.js (landing 3D scene), fonts/, img/
data/                        crops.csv, compatibility.json, simulation_config.json, metadata.json, CHANGELOG.md
samples/                     sample_inputs.json (+ generated/ example summaries and plan JSON)
assets/, static/             Noto Sans Devanagari (SIL OFL, see assets/OFL.txt)
tests/                       pytest suite
```

## How the plan is computed

**Plot model.** The plot is split into 20 equal strips, so each crop's share moves in 5% steps. Strips of each crop are spread evenly across the plot, as in strip intercropping. The map is a schematic, not a measured layout.

**Hard constraints.** These never depend on the risk slider:

- The whole area is used exactly (Σ strips = 20).
- Every crop is enabled in the dataset for the chosen district and season, and none were excluded by the farmer.
- Each selected crop gets 15% to 85% of the plot, and a plan has 2 to 3 crops.
- Every pair of selected crops is a supported pair in `data/compatibility.json`.
- The area-weighted irrigation need stays within the water level (rain only 0 mm, limited 75 mm, assured 300 mm).
- If a budget is given, the direct cash cost stays within it. Costs are rounded up and the budget down, so the solver is never looser than the validator.

**Objective.** The slider only changes this. With `w = risk / 100`:

```
maximise (1 − w) · mean(net margin) + w · CVaR10(net margin) + harvest-spread bonus
```

Net margin is computed per season over 150 optimisation seasons. These are drawn with a different seed from the comparison seasons, so the comparison is out-of-sample. CVaR10 is the average net margin of the worst 10% of those seasons. Because it is computed on whole-plot scenarios (shared weather and market draws), it captures how crops offset each other. The harvest-spread bonus is `w × 10% × plot acres × best crop's mean margin per acre` for each month with harvest income.

**Solver.** Each allowed crop combination (2 to 3 crops whose pairs are all supported) is a small CP-SAT model, solved on one worker with a fixed seed. The best result is kept, which makes runs deterministic. On the full input grid in the tests, every solve finished OPTIMAL, and the slowest took about 1.4 s.

Status meanings: **OPTIMAL** means every combination was solved or proven infeasible. **FEASIBLE** means the time ran out with a valid plan. **INFEASIBLE**, **TIMEOUT**, **INVALID_INPUT** and **ERROR** are kept separate. Every plan goes through `validation.validate_plan` before it is shown. A plan that fails is reported as ERROR and never displayed.

**Infeasible plans.** No rule is relaxed automatically. The app re-checks with one rule lifted at a time (water, budget, share limits, pair list) and tells the farmer which change would make a plan possible.

## Simulation and comparison

There are 1,000 seasons by default, with seed 2027. For each season:

- **Weather** is drawn once and shared by all crops: normal (60%), dry spell (25%, severity 0.3) or drought (15%, severity 0.6). Each crop's yield factor is `1 − severity × drought_sensitivity`.
- **Yield noise** is a mean-one lognormal per crop, with the CV taken from the dataset.
- **Price** is a shared market factor (CV 0.08) multiplied by a crop-specific mean-one lognormal.
- **Crop failure** is a Bernoulli event per crop that sets its yield to zero.
- **Gross revenue** = acres × yield × price. It is spread evenly over the harvest window's months, which assumes the crop is sold as it is harvested.
- **Net margin** = gross revenue − direct cash cost. The cost is a fixed per-acre assumption. Family labour, land rent and interest are **not** counted, so this is not full profit.

The comparison uses **common random numbers**. Both plans face exactly the same seasons, and a crop's draws are identical in both plans, so each season's difference is a paired comparison.

| Metric | Definition |
|---|---|
| Average gross revenue | mean of seasonal gross, before costs |
| Average net margin | mean of (gross − direct cost) |
| Bad-year net margin / gross | 10th percentile of seasonal totals (NumPy linear interpolation) |
| Year-to-year swing | population SD of seasonal net margin |
| Variability (CV) | SD / abs(mean) of net margin; shown as n/a if the mean is within ₹1 of zero |
| Chance of losing money | share of seasons with net margin < 0 |
| Months with zero farm income | per season, count of the 12 months (from the season's first month) with no sales, averaged over seasons. Only farm sales are counted. |
| Mixed beats single | share of paired seasons in which mixed net margin > single net margin |

**Baseline.** The single-crop plan fills the whole plot and must obey the same district, season, water, budget and exclusion rules. The default baseline is the one with the highest average net margin, which makes it a strong comparator. If no single crop is valid, the app says no fair comparison is possible.

**Diversification is never forced to win.** With this dataset, cautious mixed plans usually earn *less* on average than the best single crop, but they have a better bad-year margin and fewer zero-income months. The verdict text reports whichever way the numbers fall, and the test `test_diversification_is_not_forced_to_win` locks that in.

## The digital twin

`khetplan/twin.py` turns a checked plan into a week-by-week timeline. It is pure data with no UI, and the 3D view only draws what it is given.

- **Stages** come from each crop's sowing date, duration and harvest window: germination (first 10% of growth), vegetative (to 45%), flowering (to 70%), ripening, harvest, done.
- **Water** spreads each crop's season water need (`crop_water_mm`, new in dataset 1.1.0) over its growth with stage weights (flowering is the thirstiest). Irrigation is the `irrigation_mm` part. 1 mm on 1 acre = 4.05 m³.
- **Labour** spreads `labor_days_per_acre` (new in 1.1.0) with peaks at sowing and harvest.
- **Sales** in a normal year are each crop's area × yield × price, spread evenly over its harvest window, so the season total equals the plan's expected gross revenue exactly.
- **What-if shocks** (all prototype assumptions, labelled as such in the app):
  - *Dry spell*: loss = severity × crop drought sensitivity × worst stage weight during the spell × (1 − irrigation protection). Flowering counts most; limited water protects 30% and assured water 60%.
  - *Pest*: the chosen crop loses `severity` of its yield if it is in the field when the attack starts.
  - *Price change*: sales of the chosen crop (or all crops) after the start week are scaled by the change.
  - *Water cut*: if the plan needs more irrigation than the new level allows, irrigated crops lose yield in proportion to the shortfall. **Re-plan** solves the CP-SAT model again for the new water level and commits the new plan.
- The twin shows one illustrative season. The **risk lab** is where uncertainty is measured (1,000 seasons).

**3D view.** Three.js r170 (MIT licence, `components/twin/vendor/THREE_LICENSE.txt`) is bundled locally, so the twin needs no CDN or internet. The field is to scale (its side is the square root of the plot area). The plot is drawn as 20 equal strips, and plant shapes, heights and colours are illustrative. If the device is slow, the view lowers its resolution and shadow quality automatically.

## Data and honesty

| File | Contents |
|---|---|
| `data/crops.csv` | 13 enabled crops (7 kharif, 6 rabi) with names in 3 languages, sowing window, duration, harvest window, irrigation need, yield, price, cost, variability, drought sensitivity, failure probability, share limits. Also 2 excluded records (sugarcane, kharif onion), each with a reason. |
| `data/compatibility.json` | Supported pairs per season, with the basis for each. |
| `data/simulation_config.json` | Weather states, market CV, seed, strip count, water levels. |
| `data/metadata.json` | Version (1.1.0), coverage, assumption codes, field definitions. 1.1.0 added crop water need and labour days for the twin; see `data/CHANGELOG.md`. |

- **A1** means a value is an authored prototype assumption. **Every number** in the dataset is A1: yields, prices, costs, water needs, labour days, dates, variability, failure rates, weather odds and share limits. None were measured or taken from a market series, and none were reviewed by an agronomist.
- **A2** means the value was reported by the earlier prototype supplied with the brief, which cited a KVK Buldhana district-profile page (https://kvkbuldhana.pdkv.ac.in/?page_id=105). That page **could not be reached from the build environment**, so the kharif pair list is unverified here. The rabi pair list is A1.
- No expert validation, market prices or agronomic evidence is claimed. The app shows a prototype banner, and the printed summary carries the same disclaimer.
- A dataset that fails validation stops the app with a clear message rather than running with bad data. Restart the app after editing CSV or JSON files.

## Voice input

- The **Speak** button uses the browser's Web Speech API with locale `hi-IN`, `mr-IN` or `en-IN`. It works in Chrome and Edge on `localhost` or `https`. These browsers may send audio to the vendor's speech service. KhetPlan's server never receives or stores audio.
- **Fallbacks:** if speech is unsupported, permission is blocked, no microphone is found, the service is unreachable, or the microphone does not start within about 6 seconds, the app shows a translated message and the typed box keeps working. Example buttons fill the box for demos.
- **Parser coverage:** the parser recognises district names (Buldhana; other districts are flagged as unsupported), area with acre, guntha or hectare (bigha is rejected because it varies by place), number words and "साढ़े / साडे" halves, Devanagari digits, kharif/rabi words (summer/zaid flagged), water phrases (rain only, well, borewell, canal, drip, and so on), risk phrases, and a 4-digit year. Conflicting values, such as two plot sizes, are left blank and flagged. It only understands what those rules cover, so the farmer always reviews and confirms every field.

## What was verified

- `pytest`: **120 passed**. Coverage includes:
  - dataset validation and corrupted-file rejection
  - unit conversion and input checks
  - parser samples in all 3 languages, plus ambiguity and unsupported-input cases
  - hard constraints on a 36-case grid (2 seasons × 3 water levels × 3 risk values × 2 plot sizes)
  - infeasible, timeout, solver-crash and failed-validation paths
  - the validator catching each violation type
  - reproducibility, common random numbers, metric formulas on known values, gross − cost = net
  - "mixed can lose" honesty
  - the summary containing the actual plan and metrics
  - the twin: totals match the plan, weekly series line up, stages only move forward, each shock hits only what it should (pest only its crop, price only later sales, dry spell at flowering worse than late, rainfed worse than irrigated), water cut plus a valid re-plan, deterministic output
  - the landing page: the app opens on it and switches to the dashboard; every number it shows equals the planner, twin, scenario and risk-lab output; the sample sentences parse to the sample farm in all three languages; all files the page references exist
  - Streamlit AppTest journeys (entered through the router, as Launch does): voice transcript to twin and risk lab, manual entry, unsupported input, infeasible plan, stale inputs, dry-spell what-if and reset, water cut with re-plan, Hindi UI
- **Real browser:** headless Chromium (Playwright, WebGL through SwiftShader software rendering) at 1440 px in English and 390 px (phone) in Hindi: transcript → build → the 3D field renders, plays through the season, a dry spell is applied and replayed, then the risk lab and report tabs. There were no page or console errors and no horizontal overflow. Headless Chromium has no working microphone, so this exercised the microphone-failure fallback, not real speech.
- **Print:** the summary rendered to PDF in Chromium as **one A4 page** in English, Hindi and Marathi, and Devanagari displays correctly.

- **Landing page in a real browser** (headless Chromium, software WebGL): 1440 × 900 desktop, 820 × 1180 tablet, and 390 × 844 phone. I scrolled through every section, clicked three what-if cards, and pressed Launch, which opened `/app` with the dashboard's voice box. There were no page errors, no horizontal overflow in the page or the frame, and the 3D drew in every section. With reduced motion, headings and reveals were visible at once with no transforms. The phone menu opened, moved focus to the first link, closed on Escape, and its links scrolled to their sections. Scrolling was tested with real input, not just script calls: mouse wheel at desktop size, a raw touch drag at phone size, and Page Down/Space from the keyboard all moved the page. (Streamlit sets `scrolling="no"` on component frames, so the landing scrolls inside its own full-window container.)

**Not verified:** the reference site (farmingguy.framer.ai) could not be opened from the build environment (the proxy returned 403), so its layout was studied only as fetched text and its animations were not seen; the landing page's look is original. Also not verified: real speech recognition accuracy with real voices, frame rate on real phones and GPUs (only software rendering was tested), physical printers, browsers other than Chromium, screen readers (the 3D view has a text crop panel and KPIs, but the canvas itself is not accessible), and the quality of the Hindi and Marathi wording, which was written for this prototype and not reviewed by native speakers or farmers.

## Known limitations

- There is one demonstration district and two seasons, all with synthetic numbers.
- The strip layout is schematic: no row ratios, spacing, or competition and complementarity between crops (no intercrop yield bonus or penalty).
- Sowing is on the first day of each crop's window. There is a single harvest window per crop, with sales during harvest and no storage or price timing.
- Weather, prices and failures are simple assumed distributions, not fitted to history.
- The CVaR objective uses 150 in-sample seasons, so the out-of-sample comparison can differ slightly. That is intended, and it is shown honestly.
- Soil type, crop rotation history, labour limits and fertiliser are not modelled.
- The twin's shock responses are simple authored rules, not crop models. The twin shows one illustrative season, not a forecast.

## Screenshots

`5`–`9` are the landing page (desktop hero, season showcase, what-if, closing section, phone hero). Taken from the headless Chromium checks above (software rendering, so lighting is a little flatter than on a real GPU): `docs/screenshots/`.
