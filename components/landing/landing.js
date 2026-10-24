// KhetPlan landing page: scroll story, live 3D farm, and the launch hand-off to the Streamlit app.
import { createFarm } from './farm.js';

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const ease = (x) => 1 - Math.pow(1 - clamp(x), 3);
const lerp = (a, b, f) => a + (b - a) * f;
const mix = (A, B, f) => A.map((v, i) => lerp(v, B[i], f));
const scroller = document.getElementById('scroller');
const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const isPhone = () => window.innerWidth <= 760;
const inr = (v) => {
  const neg = v < 0; let s = Math.round(Math.abs(v)).toString();
  if (s.length > 3) { let head = s.slice(0, -3); const tail = s.slice(-3); const p = []; while (head.length > 2) { p.unshift(head.slice(-2)); head = head.slice(0, -2); } if (head) p.unshift(head); s = p.join(',') + ',' + tail; }
  return (neg ? '−₹' : '₹') + s;
};
const pct = (x) => `${Math.round(x * 100)}%`;

// ---------- Streamlit bridge ----------
const embedded = window.parent !== window;
const post = (type, d = {}) => embedded && window.parent.postMessage(Object.assign({ isStreamlitMessage: true, type }, d), '*');
let data = null, booted = false;
window.addEventListener('message', (e) => {
  if (!e.data || e.data.type !== 'streamlit:render') return;
  if (!booted) { booted = true; boot(e.data.args.data || { ok: false }); }
});
post('streamlit:componentReady', { apiVersion: 1 });
// keyboard scrolling (space, arrows, page keys) needs focus inside the scroll container
scroller.focus({ preventScroll: true });
post('streamlit:setFrameHeight', { height: window.innerHeight });
// opened directly (not inside Streamlit): run without the sample plan
setTimeout(() => { if (!booted) { booted = true; boot({ ok: false }); } }, embedded ? 2500 : 0);

// ---------- launch: curtain, then ask Streamlit to switch to the dashboard ----------
function launch(ev) {
  const a = ev.currentTarget;
  if (!embedded) return; // plain link to /app
  ev.preventDefault();
  const r = a.getBoundingClientRect();
  const cur = $('#curtain');
  cur.style.setProperty('--cx', `${r.left + r.width / 2}px`);
  cur.style.setProperty('--cy', `${r.top + r.height / 2}px`);
  cur.classList.add('on');
  closeMenu();
  setTimeout(() => post('streamlit:setComponentValue', { value: { action: 'launch', nonce: `${Date.now()}` }, dataType: 'json' }), reduce ? 0 : 650);
}
$$('[data-launch]').forEach((a) => a.addEventListener('click', launch));

// ---------- menu ----------
const burger = $('#burger'), menu = $('#menu');
function closeMenu() { if (!menu.hidden) { menu.hidden = true; burger.setAttribute('aria-expanded', 'false'); burger.setAttribute('aria-label', 'Open menu'); scroller.style.overflowY = ''; } }
burger.addEventListener('click', () => {
  const open = menu.hidden;
  menu.hidden = !open;
  burger.setAttribute('aria-expanded', String(open));
  burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  scroller.style.overflowY = open ? 'hidden' : '';
  if (open) $('a', menu).focus();
});
$$('a', menu).forEach((a) => a.addEventListener('click', closeMenu));
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMenu(); });

// load animations: once finished, drop the class so scroll-driven inline styles take over
$$('.load').forEach((el) => el.addEventListener('animationend', () => { el.classList.remove('load'); el.style.removeProperty('--d'); }, { once: true }));

// ---------- text reveals: split headings into words ----------
$$('.reveal-lines').forEach((h) => {
  let i = 0;
  const walk = (node) => [...node.childNodes].forEach((n) => {
    if (n.nodeType === 3) {
      const frag = document.createDocumentFragment();
      n.textContent.split(/(\s+)/).forEach((w) => {
        if (!w) return;
        if (/^\s+$/.test(w)) { frag.append(w); return; }
        const o = document.createElement('span'); o.className = 'rl';
        const s = document.createElement('span'); s.textContent = w; s.style.setProperty('--i', i++);
        o.append(s); frag.append(o);
      });
      n.replaceWith(frag);
    } else if (n.nodeType === 1) walk(n);
  });
  walk(h);
});
const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: 0.18, rootMargin: '0px 0px -6% 0px' });
$$('.reveal-up, .reveal-mask, .reveal-lines').forEach((el) => io.observe(el));

// ---------- section geometry ----------
const sec = {};
['home', 'how', 'season', 'whatif', 'features', 'start'].forEach((id) => { sec[id] = document.getElementById(id); });
const progress = (el) => { const r = el.getBoundingClientRect(); const span = r.height - window.innerHeight; return span > 0 ? clamp(-r.top / span) : clamp(1 - r.bottom / (r.height + window.innerHeight)); };
const visible = (el) => { const r = el.getBoundingClientRect(); return Math.max(0, Math.min(r.bottom, window.innerHeight) - Math.max(r.top, 0)); };

// ---------- the 3D farm ----------
let farm = null;
const canvas = $('#farm');

function boot(d) {
  data = d;
  try { farm = createFarm(canvas, data, { small: isPhone() }); } catch (err) { canvas.style.display = 'none'; farm = null; }
  if (farm) { farm.resize(); window.addEventListener('resize', () => { farm.resize(); placeVisuals(); }); }
  fill();
  placeVisuals();
  tick(true);
  if (farm) farm.jump();
  requestAnimationFrame(loop);
}

// ---------- content from the real sample plan ----------
const FIELD_LABEL = { region: 'District', area_value: 'Plot', season: 'Season', water: 'Water', risk: 'Risk' };
const VAL = { buldhana: 'Buldhana', kharif: 'Kharif', rabi: 'Rabi', limited: 'Limited (well)', rainfed: 'Rain only', assured: 'Assured' };
let heroWeek = 10, finalWeek = 24, marks = [];

function fill() {
  if (!data.ok) {
    $('#seasonNote').textContent = 'The sample plan could not be computed from the dataset; open the app to plan your own farm.';
    $('#wiResult').innerHTML = '<p class="wi-empty">Scenario results are available inside the app.</p>';
    $('#riskTile').querySelector('.risk').innerHTML = '<p class="risk-say">Run 1,000 simulated seasons for your own plan inside the app.</p>';
    return;
  }
  const tw = data.twin, n = tw.weeks.length, s = data.sample;
  const name = (id) => data.crops[id].short;
  $('#dsv').textContent = `v${data.dataset_version}`;
  $('#hm-acres').textContent = `${s.acres} acres`;
  $('#hm-crops').textContent = `${data.plan.length} crops`;
  $('#hm-weeks').textContent = `${n} weeks`;
  $('#seasonNote').textContent = `Sample plan computed by KhetPlan: ${s.acres} acres in Buldhana, kharif ${s.year}, limited water. Synthetic demonstration data.`;
  const pestCrop = data.scenarios.pest && data.scenarios.pest.crop;
  if (pestCrop) $('#wiPestSub').textContent = `On ${name(pestCrop).toLowerCase()} from week ${data.scenarios.pest.week}`;

  // hero and final weeks come from the timeline itself
  const first = tw.stage[0];
  const fl = first.indexOf(3);
  heroWeek = fl >= 0 ? Math.min(n - 1, fl + 2) : Math.floor(n / 3);
  let best = -1;
  for (let w = 0; w < n; w++) { const sc = tw.stage.reduce((a, st) => a + (st[w] === 4 || st[w] === 5 ? 1 : 0), 0); if (sc > best) { best = sc; finalWeek = w; } }

  // story visual 2: strips, legend, calendar
  $('#vpStrips').innerHTML = tw.strip_order.map((id, i) => `<i style="--i:${i};background:${data.crops[id].color}"></i>`).join('');
  $('#vpLegend').innerHTML = data.plan.map((a) => `<span><i style="background:${data.crops[a.id].color}"></i>${name(a.id)} · ${pct(a.share)}</span>`).join('');
  const t0 = new Date(tw.weeks[0] + 'T00:00:00').getTime(), t1 = t0 + n * 7 * 86400000;
  const at = (iso) => clamp((new Date(iso + 'T00:00:00').getTime() - t0) / (t1 - t0)) * 100;
  const monthsSeen = [];
  for (let w = 0; w < n; w += 4) { const m = new Date(t0 + w * 7 * 86400000).getMonth(); if (!monthsSeen.includes(data.months[m])) monthsSeen.push(data.months[m]); }
  $('#vpCal').innerHTML = data.plan.map((a) => {
    const c = data.crops[a.id].color;
    return `<div class="row"><span>${name(a.id)}</span><div class="bar"><i style="left:${at(a.sow)}%;width:${at(a.harvest_start) - at(a.sow)}%;background:${c}"></i><b style="left:${at(a.harvest_start)}%;width:${Math.max(1.5, at(a.harvest_end) - at(a.harvest_start))}%;background:${c}"></b></div></div>`;
  }).join('') + `<div class="months">${monthsSeen.map((m) => `<span>${m}</span>`).join('')}</div>`;

  // story visual 3: chart rows
  $('#vsCrops').innerHTML = tw.crops.map((c) => `<div class="row"><span>${name(c.id)}</span><div class="g"><i style="background:${data.crops[c.id].color};width:0"></i></div><span class="st"></span></div>`).join('');

  // voice visual
  $('#vvLang').innerHTML = data.parsed.map((p) => `<span data-l="${p.lang}">${{ en: 'English', hi: 'हिन्दी', mr: 'मराठी' }[p.lang]}</span>`).join('');

  // season HUD crops + timeline marks (project stage names)
  $('#scCrops').innerHTML = tw.crops.map((c) => `<li><span class="sw" style="background:${data.crops[c.id].color}"></span><span class="nm">${name(c.id)}</span><span class="st"></span><span class="g"><i style="background:${data.crops[c.id].color};width:0"></i></span></li>`).join('');
  // milestones of the main (largest) crop, in the project's own stage names
  const main = data.plan.reduce((a, b) => (b.share > a.share ? b : a));
  const mi = tw.crops.findIndex((c) => c.id === main.id), ms = tw.stage[mi];
  const sowW = tw.events.find((e) => e.key === 'ev_sow' && e.crop === main.id).week;
  marks = [['Sowing', sowW], [data.stages.germination, ms.indexOf(1)], [data.stages.vegetative, ms.indexOf(2)], [data.stages.flowering, ms.indexOf(3)], [data.stages.harvest, ms.indexOf(5)]]
    .filter((m) => m[1] >= 0);
  marks.forEach((m, i) => { if (i && m[1] <= marks[i - 1][1]) m[1] = marks[i - 1][1] + 0.5; });
  const midWeek = (w) => { const d = new Date(tw.weeks[Math.floor(w)] + 'T00:00:00'); d.setDate(d.getDate() + 3); return d.toISOString().slice(0, 10); };
  $('#tlMarks').innerHTML = marks.map(([l, w], i) => `<li style="left:${tlPos(i)}%">${l}<small>${fmtDate(i === 0 ? main.sow : midWeek(w))}</small></li>`).join('');
  $('#tlMain').textContent = `Milestones of the main crop, ${name(main.id).toLowerCase()} (${pct(main.share)} of the plot)`;

  // what-if tile: the four shocks on the sample plan
  $('#wiImpact').innerHTML = Object.entries(data.scenarios).map(([k, v]) => {
    const r = (v.gross - v.reference) / v.reference;
    return `<div class="imp"><span>${CARD_NAME[k]}</span><i><b style="width:${Math.min(100, Math.abs(r) * 400)}%"></b></i><em>${r < 0 ? '−' : '+'}${Math.abs(r * 100).toFixed(1)}%</em></div>`;
  }).join('') + '<p class="imp-note">Change in season gross revenue on the sample plan, from the twin.</p>';

  // risk tile: the risk lab's numbers for this sample
  const r = data.risk;
  if (r) {
    const base = name(r.baseline);
    const row = (label, a, b, money = true) => `<div class="risk-row"><span>${label}</span><b class="${money && a < 0 ? 'neg' : ''}">${money ? inr(a) : pct(a)}</b><b class="${money && b < 0 ? 'neg' : ''}">${money ? inr(b) : pct(b)}</b></div>`;
    $('#riskBox').innerHTML = `<div class="risk-row"><span class="h">Sample plan</span><span class="h">Mixed</span><span class="h">${base} only</span></div>`
      + row('Average net margin', r.mixed.mean, r.single.mean) + row('Bad year (10th percentile)', r.mixed.p10, r.single.p10) + row('Chance of a loss', r.mixed.loss, r.single.loss, false)
      + `<p class="risk-say">Here the mixed plan earned ${r.mixed.mean < r.single.mean ? 'less' : 'more'} on average but ${r.mixed.p10 > r.single.p10 ? 'held up better' : 'did worse'} in bad seasons. KhetPlan shows both sides instead of forcing a winner.</p>`;
    $('#riskNote').textContent = `${r.seasons.toLocaleString('en-IN')} paired simulated seasons, seed ${r.seed}. Illustrative, synthetic data, not a forecast.`;
  }
}
const CARD_NAME = { dry_spell: 'Dry spell', pest: 'Pest attack', water_cut: 'Water shortage', price: 'Price −25%' };
const tlPos = (i) => (marks.length > 1 ? (i / (marks.length - 1)) * 100 : 0);
function tlFill(t) {
  if (t <= marks[0][1]) return 0;
  for (let i = 0; i < marks.length - 1; i++) if (t < marks[i + 1][1]) return tlPos(i) + (tlPos(i + 1) - tlPos(i)) * ((t - marks[i][1]) / (marks[i + 1][1] - marks[i][1]));
  return 100;
}
const fmtDate = (iso) => { const d = new Date(iso + 'T00:00:00'); return `${d.getDate()} ${data.months[d.getMonth()]}`; };

// story visuals live in a sticky stage on desktop and inside each step on phones
function placeVisuals() {
  const phone = isPhone();
  $$('.vis').forEach((v) => {
    const step = $(`.step[data-step="${v.dataset.vis}"]`);
    if (phone) {
      let box = $('.vis-inline', step);
      if (!box) { box = document.createElement('div'); box.className = 'vis-inline stage'; step.append(box); }
      if (v.parentElement !== box) box.append(v);
      v.classList.add('on');
    } else if (v.parentElement !== $('#storyStage')) {
      $('#storyStage').append(v);
    }
  });
  if (!$('.wi-window') && phone) { const win = document.createElement('div'); win.className = 'wi-window'; win.setAttribute('aria-hidden', 'true'); sec.whatif.append(win); }
}

// ---------- voice typing loop ----------
let vv = { i: 0, ch: 0, hold: 0, fields: 0 };
function voiceTick(dt) {
  if (!data || !data.ok) return;
  const p = data.parsed[vv.i];
  if (vv.ch < p.text.length) { vv.ch = Math.min(p.text.length, vv.ch + dt * 34); }
  else { vv.hold += dt; }
  $('#vvText').textContent = p.text.slice(0, Math.floor(vv.ch));
  $$('#vvLang span').forEach((s) => s.classList.toggle('on', s.dataset.l === p.lang));
  if (vv.ch >= p.text.length && !vv.fields) {
    const f = p.fields;
    const items = Object.entries(FIELD_LABEL).filter(([k]) => f[k] != null).map(([k, l]) => {
      const v = k === 'area_value' ? `${f.area_value} ${f.area_unit}${f.area_value === 1 ? '' : 's'}` : k === 'risk' ? `${f.risk}/100` : (VAL[f[k]] || f[k]);
      return `<span><b>${l}</b>${v}</span>`;
    });
    $('#vvFields').innerHTML = items.join('');
    $$('#vvFields span').forEach((s, i) => setTimeout(() => s.classList.add('on'), 120 * i));
    vv.fields = 1;
  }
  if (vv.hold > 2.6) { vv = { i: (vv.i + 1) % data.parsed.length, ch: 0, hold: 0, fields: 0 }; $('#vvFields').innerHTML = ''; }
  // wave bars react while "speaking"
  const wave = $('#wave');
  if (!wave.children.length) wave.innerHTML = '<b></b>'.repeat(28);
  const talking = vv.ch < p.text.length;
  [...wave.children].forEach((b, i) => { b.style.height = `${talking ? 20 + Math.abs(Math.sin(performance.now() / 140 + i * 0.7)) * 75 * (0.5 + 0.5 * Math.sin(i * 1.3)) : 12}%`; });
}

// ---------- story visual 3: chart sweep ----------
let chartW = 0;
function chartTick(dt) {
  if (!data || !data.ok) return;
  const tw = data.twin, n = tw.weeks.length;
  chartW = (chartW + dt * 4) % (n + 6);
  const w = Math.min(n - 1, chartW);
  const svg = $('#vsChart');
  const maxS = Math.max(...tw.cum_sales) || 1, maxW = Math.max(...tw.water_m3) || 1;
  const X = (i) => (i / (n - 1)) * 400, Ys = (v) => 190 - (v / maxS) * 170;
  if (!svg.dataset.drawn) {
    const bars = tw.water_m3.map((v, i) => `<rect x="${X(i) - 4}" y="${200 - (v / maxW) * 80}" width="7" height="${(v / maxW) * 80}" rx="2" fill="#8fc0e8" opacity=".55"/>`).join('');
    const line = tw.cum_sales.map((v, i) => `${i ? 'L' : 'M'}${X(i).toFixed(1)},${Ys(v).toFixed(1)}`).join(' ');
    svg.innerHTML = `${bars}<path d="${line} L400,200 L0,200 Z" fill="rgba(199,166,122,.18)"/><path d="${line}" fill="none" stroke="#C7A67A" stroke-width="3" stroke-linejoin="round"/>`
      + `<line id="vsMark" x1="0" x2="0" y1="0" y2="200" stroke="#F7F6EF" stroke-width="1.5" stroke-dasharray="4 4"/><circle id="vsDot" r="6" fill="#F7F6EF"/>`;
    svg.dataset.drawn = 1;
  }
  const wi = Math.floor(w);
  $('#vsMark').setAttribute('x1', X(w)); $('#vsMark').setAttribute('x2', X(w));
  $('#vsDot').setAttribute('cx', X(w)); $('#vsDot').setAttribute('cy', Ys(tw.cum_sales[wi]));
  $('#vsWeek').textContent = `Week ${wi + 1} of ${n} · ${inr(tw.cum_sales[wi])}`;
  $$('#vsCrops .row').forEach((r, ci) => {
    $('.g i', r).style.width = `${tw.growth[ci][wi] * 100}%`;
    $('.st', r).textContent = data.stages[STAGE_KEYS[tw.stage[ci][wi]]];
  });
}
const STAGE_KEYS = ['not_sown', 'germination', 'vegetative', 'flowering', 'maturing', 'harvest', 'done'];

// ---------- season HUD ----------
let lastHudWeek = -1;
function seasonHud(t) {
  const tw = data.twin, n = tw.weeks.length, wi = Math.min(n - 1, Math.floor(t));
  $('#tlFill').style.width = `${tlFill(t)}%`;
  $$('#tlMarks li').forEach((li, i) => li.classList.toggle('on', t >= marks[i][1] - 0.01));
  if (wi === lastHudWeek) return;
  lastHudWeek = wi;
  const d = new Date(tw.weeks[wi] + 'T00:00:00');
  d.setDate(d.getDate() + 3);
  $('#scDate').textContent = `${d.getDate()} ${data.months[d.getMonth()]} ${d.getFullYear()}`;
  $('#scWeek').textContent = `Week ${wi + 1} of ${n}`;
  const stages = tw.stage.map((s) => s[wi]);
  const sowing = tw.events.some((e) => e.key === 'ev_sow' && e.week === wi);
  const live = stages.filter((s) => s < 6);
  $('#scStage').textContent = sowing ? 'Sowing' : live.length ? data.stages[STAGE_KEYS[Math.max(...live)]] : data.stages.done;
  $$('#scCrops li').forEach((li, ci) => {
    $('.st', li).textContent = data.stages[STAGE_KEYS[stages[ci]]];
    $('.g i', li).style.width = `${tw.growth[ci][wi] * 100}%`;
  });
  $('#scSales').textContent = `${inr(tw.cum_sales[wi])} / ${inr(tw.totals.reference_gross)}`;
}

// ---------- what-if cards ----------
let scenario = null;
const SC_WEEK = { dry_spell: 10, pest: 12, water_cut: 14, price: 26 };
function pick(kind) {
  scenario = scenario === kind ? null : kind;
  $$('.wi-card').forEach((c) => c.setAttribute('aria-selected', String(c.dataset.kind === scenario)));
  if (farm) farm.setScenario(scenario);
  const box = $('#wiResult');
  if (!data.ok) return;
  if (!scenario) { box.innerHTML = '<p class="wi-empty">Choose a scenario to replay the season.</p>'; return; }
  const s = data.scenarios[scenario];
  const delta = s.gross - s.reference, rel = delta / s.reference;
  const top = Math.max(...Object.values(s.per_crop).map((v) => v[1])) || 1;
  const rows = Object.entries(s.per_crop).map(([id, [got, ref]]) => `<div class="wi-row"><span>${data.crops[id].short}</span><div class="t"><i style="width:${(ref / top) * 100}%;background:#dfe5dc"></i><i style="width:${(got / top) * 100}%;background:${data.crops[id].color}"></i></div><span class="v">${inr(got)} / ${inr(ref)}</span></div>`).join('');
  const replan = s.replan ? `<p class="wi-replan">Re-plan for rain only: ${s.replan.map((a) => `${data.crops[a.id] ? data.crops[a.id].short : a.id} ${pct(a.share)}`).join(' + ')}</p>` : '';
  const note = scenario === 'price' ? '<p class="fine">The field looks the same; only the money changes.</p>' : '';
  box.innerHTML = `<div class="wi-big"><b>${inr(s.gross)}</b><span class="delta ${Math.abs(rel) < 0.005 ? 'flat' : ''}">${delta < 0 ? '−' : '+'}${Math.abs(rel * 100).toFixed(1)}%</span><small>season gross vs ${inr(s.reference)} planned</small></div><div class="wi-rows">${rows}</div>${replan}${note}`;
}
$$('.wi-card').forEach((c) => {
  c.addEventListener('click', () => pick(c.dataset.kind));
  c.addEventListener('mouseenter', () => { if (!scenario && farm) farm.setScenario(c.dataset.kind); });
  c.addEventListener('mouseleave', () => { if (!scenario && farm) farm.setScenario(null); });
});

// ---------- pointer: gentle look-around in the hero ----------
window.addEventListener('pointermove', (e) => { if (farm && !reduce) farm.setPointer((e.clientX / window.innerWidth - 0.5) * 2, (e.clientY / window.innerHeight - 0.5) * -2); }, { passive: true });

// ---------- per-frame orchestration ----------
let lastT = performance.now(), dirty = true;
scroller.addEventListener('scroll', () => { dirty = true; }, { passive: true });
window.addEventListener('resize', () => { dirty = true; });

function tick(force) {
  const vh = window.innerHeight;
  // nav state + active link
  const heroP = progress(sec.home);
  $('#nav').classList.toggle('solid', heroP > 0.55 || sec.home.getBoundingClientRect().bottom < vh * 0.4);
  const cur = ['start', 'features', 'how', 'home'].find((id) => sec[id].getBoundingClientRect().top < vh * 0.45) || 'home';
  $$('.links a').forEach((a) => a.classList.toggle('on', a.dataset.nav === (cur === 'start' ? 'features' : cur === 'how' ? 'how' : cur)));

  // hero copy drifts up and fades as the camera flies in
  const hc = $('.hero-copy');
  if (!reduce) { hc.style.transform = `translateY(${-heroP * 90}px)`; hc.style.opacity = String(1 - ease(heroP * 1.4)); }
  $('.hint').style.opacity = heroP > 0.05 ? '0' : '';
  if (!reduce) { const hm = $('.hero-meta'); hm.style.opacity = String(1 - ease(heroP * 2)); hm.style.transform = `translateY(${-heroP * 60}px)`; }

  // story: which step is in the middle of the screen
  if (!isPhone()) {
    let on = 0;
    $$('.step').forEach((s, i) => { const r = s.getBoundingClientRect(); if (r.top < vh * 0.55) on = i; });
    $$('.step').forEach((s, i) => s.classList.toggle('on', i === on));
    $$('#storyStage .vis').forEach((v) => v.classList.toggle('on', +v.dataset.vis === on));
    $$('.stage-dots i').forEach((d, i) => d.classList.toggle('on', i === on));
  }

  // parallax
  if (!reduce) $$('[data-parallax]').forEach((el) => { const r = el.getBoundingClientRect(); const c = r.top + r.height / 2 - vh / 2; el.style.transform = `translate3d(0, ${c * +el.dataset.parallax}px, 0)`; });

  if (!farm) return;
  // which 3D scene owns the screen
  const scenes = ['home', 'season', 'whatif', 'start'].map((id) => [id, visible(sec[id])]);
  const any = scenes.some(([, v]) => v > 4);
  if (any) farm.start(); else farm.stop();
  const [owner] = scenes.reduce((a, b) => (b[1] > a[1] ? b : a));
  const phone = isPhone();
  const n = data.ok ? data.twin.weeks.length : 36;
  if (owner === 'home') {
    const p = ease(heroP);
    farm.setPose(mix([62, 44, 84], [24, 14, 31], p), mix([0, 0, 0], [1, 1.6, -2], p));
    farm.setOffset(phone ? 0 : lerp(0.14, 0, p), phone ? lerp(0.2, 0.05, p) : 0);
    farm.setWeek(heroWeek); farm.setMood('day'); farm.setWeather('clear'); if (!scenario) farm.setScenario(null);
  } else if (owner === 'season') {
    const p = progress(sec.season);
    const a = 0.5 + p * 1.15;
    const r = lerp(phone ? 74 : 64, phone ? 62 : 50, p);
    farm.setPose([Math.sin(a) * r, lerp(phone ? 46 : 36, phone ? 36 : 24, p), Math.cos(a) * r], [0, 1, 0]);
    farm.setOffset(phone ? 0 : -0.1, phone ? 0.1 : 0);
    const t = clamp((p - 0.04) / 0.9) * (n - 1);
    farm.setWeek(t); farm.setMood('day'); farm.setWeather(null); farm.setScenario(null);
    if (data.ok) seasonHud(t);
  } else if (owner === 'whatif') {
    farm.setPose(phone ? [0, 52, 46] : [30, 27, 40], [0, 0, 0]);
    farm.setOffset(phone ? 0 : 0.22);
    const hovered = $$('.wi-card').find((c) => c.matches(':hover'));
    const k = scenario || (hovered && hovered.dataset.kind);
    farm.setWeek(k ? SC_WEEK[k] : 12); farm.setMood('day'); farm.setWeather(k === 'dry_spell' ? 'dry' : 'clear');
    if (scenario) farm.setScenario(scenario); else if (!hovered) farm.setScenario(null);
  } else {
    const p = progress(sec.start);
    const a = -0.35 + p * 0.7;
    farm.setPose([Math.sin(a) * 40, phone ? 13 : 10, Math.cos(a) * 40], [0, phone ? 6 : 8, 0]);
    farm.setOffset(0);
    farm.setWeek(finalWeek); farm.setMood('golden'); farm.setWeather('clear'); farm.setScenario(null);
  }
}

function loop(now) {
  const dt = Math.min(0.05, (now - lastT) / 1000);
  lastT = now;
  if (dirty) { tick(); dirty = false; }
  else if (farm && $$('.wi-card').some((c) => c.matches(':hover'))) tick();
  // story animations only while the story is on screen
  if (visible(sec.how) > 0) { voiceTick(dt); chartTick(dt); }
  requestAnimationFrame(loop);
}
