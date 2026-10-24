// KhetPlan 3D farm digital twin (Three.js). Receives data from Python through the
// Streamlit component protocol and animates the season in the browser.
import * as THREE from './vendor/three.module.min.js';
import { OrbitControls } from './vendor/OrbitControls.js';
import { FIELD_W, FIELD_D, BED_Y, ROWS, COLS, SKY, SUN, SOIL, C, noiseTexture, addTree, addHouse, plantGeometries, plantLook } from './farmkit.js';

// ---------- Streamlit bridge ----------
const post = (type, data) => window.parent.postMessage(Object.assign({ isStreamlitMessage: true, type }, data), '*');
const setHeight = () => post('streamlit:setFrameHeight', { height: document.getElementById('app').offsetHeight + 4 });

// ---------- constants ----------
const DAY = 86400000;

// ---------- state ----------
let args = null, twin = null, mode = 'none', planKey = null, version = null;
let t = 0, playing = false, speed = 1, lastFrame = performance.now(), introT = 1, firedUpTo = -1;
let autoRotate = false;
const parseDate = (s) => new Date(s + 'T00:00:00');

// ---------- renderer / scene ----------
const canvas = document.getElementById('gl');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.background = SKY.clear.clone();
scene.fog = new THREE.Fog(scene.background.clone(), 90, 230);

const camera = new THREE.PerspectiveCamera(40, 1, 0.5, 600);
const HOME = new THREE.Vector3(34, 30, 44), TOP = new THREE.Vector3(0.01, 70, 0.01);
camera.position.copy(HOME);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.maxPolarAngle = 1.42;
controls.minDistance = 14;
controls.maxDistance = 150;
controls.target.set(0, 0, 0);
controls.autoRotateSpeed = 0.6;
let camFly = null; // {from, to, t}

const hemi = new THREE.HemisphereLight('#dceeff', '#6b5a3a', 1.0);
scene.add(hemi);
const sun = new THREE.DirectionalLight('#fff1d6', 2.5);
sun.position.set(45, 60, 25);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -45, right: 45, top: 40, bottom: -40, near: 5, far: 180 });
sun.shadow.bias = -0.0005;
scene.add(sun);

// seeded random so the farm looks the same on every render
let seed = 7;
const rnd = () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;

// ---------- procedural textures ----------

// ---------- world: ground, trees, house, field ----------
const world = new THREE.Group();
scene.add(world);
const grassTex = noiseTexture(rnd, '#7aa34f', 0.12);
grassTex.repeat.set(30, 30);
const ground = new THREE.Mesh(new THREE.CircleGeometry(260, 64), new THREE.MeshStandardMaterial({ map: grassTex, roughness: 1 }));
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
world.add(ground);

for (let i = 0; i < 34; i++) {
  const a = rnd() * Math.PI * 2, r = 42 + rnd() * 50;
  const x = Math.cos(a) * r, z = Math.sin(a) * r;
  if (Math.abs(x) < 30 && Math.abs(z) < 24) continue;
  addTree(world, rnd, x, z, 0.9 + rnd() * 0.8);
}

addHouse(world, -FIELD_W / 2 - 12, -FIELD_D / 2 - 4, 0.5); // farmhouse

const field = new THREE.Group();
world.add(field);
const bund = new THREE.Mesh(new THREE.BoxGeometry(FIELD_W + 2.4, 0.5, FIELD_D + 2.4), new THREE.MeshStandardMaterial({ color: '#7d6040', roughness: 1 }));
bund.position.y = 0.25;
bund.receiveShadow = true;
field.add(bund);
const soilTex = noiseTexture(rnd, '#8f6c49', 0.1, 256, 24);
soilTex.repeat.set(1, 1);
const plate = new THREE.Mesh(new THREE.BoxGeometry(FIELD_W, 0.3, FIELD_D), new THREE.MeshStandardMaterial({ map: soilTex, color: '#ffffff', roughness: 1 }));
plate.position.y = 0.5;
plate.receiveShadow = true;
field.add(plate);

// water features
const waterGroup = new THREE.Group();
field.add(waterGroup);
function buildWater(level) {
  waterGroup.clear();
  if (level === 'limited') {
    const ring = new THREE.Mesh(new THREE.CylinderGeometry(1.6, 1.8, 1.1, 18, 1, true), new THREE.MeshStandardMaterial({ color: '#9a9488', roughness: 1, side: THREE.DoubleSide }));
    ring.position.y = 0.55;
    const water = new THREE.Mesh(new THREE.CircleGeometry(1.55, 24), new THREE.MeshStandardMaterial({ color: '#3d7fb0', roughness: 0.2, metalness: 0.1 }));
    water.rotation.x = -Math.PI / 2;
    water.position.y = 0.8;
    const post1 = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 2.6), new THREE.MeshStandardMaterial({ color: '#6b4a2f' }));
    const post2 = post1.clone();
    post1.position.set(-1.5, 1.3, 0);
    post2.position.set(1.5, 1.3, 0);
    const beam = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 3.2), new THREE.MeshStandardMaterial({ color: '#6b4a2f' }));
    beam.rotation.z = Math.PI / 2;
    beam.position.y = 2.5;
    const g = new THREE.Group();
    [ring, water, post1, post2, beam].forEach((m) => { m.castShadow = true; g.add(m); });
    g.position.set(FIELD_W / 2 + 4, 0, FIELD_D / 2 - 3);
    waterGroup.add(g);
  } else if (level === 'assured') {
    const g = new THREE.Group();
    const pump = new THREE.Mesh(new THREE.BoxGeometry(1.6, 1.2, 1.2), new THREE.MeshStandardMaterial({ color: '#2f6fa8', roughness: 0.5, metalness: 0.3 }));
    pump.position.y = 0.6;
    const pipe = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 2.4), new THREE.MeshStandardMaterial({ color: '#c7ccd1', metalness: 0.6, roughness: 0.3 }));
    pipe.position.set(0.5, 1.6, 0);
    const tank = new THREE.Mesh(new THREE.CylinderGeometry(1.0, 1.0, 1.8, 16), new THREE.MeshStandardMaterial({ color: '#2a2f33', roughness: 0.6 }));
    tank.position.set(-1.6, 0.9, 0);
    const main = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, FIELD_W, 8), new THREE.MeshStandardMaterial({ color: '#2f6fa8' }));
    main.rotation.z = Math.PI / 2;
    main.position.set(-FIELD_W / 2 - 4, 0.55, -FIELD_D / 2 - 4 - (FIELD_D / 2 - 3) + 0);
    [pump, pipe, tank].forEach((m) => { m.castShadow = true; g.add(m); });
    g.position.set(FIELD_W / 2 + 4, 0, -FIELD_D / 2 + 2);
    waterGroup.add(g);
    const header = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, FIELD_W, 8), new THREE.MeshStandardMaterial({ color: '#2f6fa8', roughness: 0.4 }));
    header.rotation.z = Math.PI / 2;
    header.position.set(0, 0.7, -FIELD_D / 2 - 0.6);
    waterGroup.add(header);
  }
}

// rain, clouds, pests, irrigation spray
const RAIN_N = 2600;
const rainGeo = new THREE.BufferGeometry();
const rainPos = new Float32Array(RAIN_N * 3);
for (let i = 0; i < RAIN_N; i++) {
  rainPos[i * 3] = (rnd() - 0.5) * 90;
  rainPos[i * 3 + 1] = rnd() * 45;
  rainPos[i * 3 + 2] = (rnd() - 0.5) * 80;
}
rainGeo.setAttribute('position', new THREE.BufferAttribute(rainPos, 3));
const rainMat = new THREE.PointsMaterial({ color: '#d8e8ff', size: 0.22, transparent: true, opacity: 0, depthWrite: false });
const rain = new THREE.Points(rainGeo, rainMat);
scene.add(rain);

const clouds = new THREE.Group();
const cloudMat = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: 1, transparent: true, opacity: 0.92, flatShading: true });
for (let i = 0; i < 9; i++) {
  const g = new THREE.Group();
  for (let k = 0; k < 4; k++) {
    const m = new THREE.Mesh(new THREE.IcosahedronGeometry(3 + rnd() * 2.5, 1), cloudMat);
    m.position.set(k * 3.2 - 5, rnd() * 1.5, rnd() * 2);
    m.scale.y = 0.55;
    g.add(m);
  }
  g.position.set((rnd() - 0.5) * 160, 34 + rnd() * 10, (rnd() - 0.5) * 120);
  g.userData.v = 0.6 + rnd() * 0.8;
  clouds.add(g);
}
scene.add(clouds);

const PEST_N = 260;
const pestGeo = new THREE.BufferGeometry();
pestGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(PEST_N * 3), 3));
const pestMat = new THREE.PointsMaterial({ color: '#d0312d', size: 0.32, transparent: true, opacity: 0, depthWrite: false });
const pests = new THREE.Points(pestGeo, pestMat);
pests.userData.base = [];
scene.add(pests);

// ---------- plant geometry (shared with the landing page, see farmkit.js) ----------
const GEO = plantGeometries();

// ---------- per-plan objects ----------
const planGroup = new THREE.Group();
field.add(planGroup);
let beds = [], ribbons = [], drips = [], cropObjs = [], stripCrop = [];

function disposeGroup(g) {
  g.traverse((o) => { if (o.geometry && !Object.values(GEO).flat().includes(o.geometry)) o.geometry.dispose(); if (o.material) o.material.dispose(); });
  g.clear();
}

function buildPlan() {
  seed = 11; // same plant layout for every scenario of a plan
  disposeGroup(planGroup);
  beds = []; ribbons = []; drips = []; cropObjs = []; stripCrop = [];
  if (mode !== 'plan') return;
  const order = twin.strip_order, n = order.length, sw = FIELD_W / n;
  const meta = args.crops;
  order.forEach((cid, i) => {
    const x = -FIELD_W / 2 + sw * (i + 0.5);
    const bed = new THREE.Mesh(new THREE.BoxGeometry(sw * 0.8, 0.25, FIELD_D - 1.2), new THREE.MeshStandardMaterial({ color: SOIL.dry.clone(), roughness: 1 }));
    bed.position.set(x, BED_Y - 0.125, -0.2);
    bed.receiveShadow = true;
    bed.userData = { strip: i, crop: cid };
    planGroup.add(bed);
    beds.push(bed);
    const rib = new THREE.Mesh(new THREE.BoxGeometry(sw * 0.8, 0.16, 0.7), new THREE.MeshStandardMaterial({ color: meta[cid].color, roughness: 0.5, emissive: meta[cid].color, emissiveIntensity: 0.15 }));
    rib.position.set(x, BED_Y + 0.02, FIELD_D / 2 - 0.45);
    rib.scale.y = 0.001;
    rib.userData.delay = i * 0.05;
    planGroup.add(rib);
    ribbons.push(rib);
    stripCrop.push(cid);
    if (meta[cid].irrigated && args.farm.water !== 'rainfed') {
      const d = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, FIELD_D - 1.4, 6), new THREE.MeshStandardMaterial({ color: '#2f6fa8', emissive: '#4aa3ff', emissiveIntensity: 0 }));
      d.rotation.x = Math.PI / 2;
      d.position.set(x, BED_Y + 0.06, -0.2);
      planGroup.add(d);
      drips.push(d);
    }
  });
  twin.crops.forEach((c, ci) => {
    const m = meta[c.id];
    const [bodyGeo, accGeo] = GEO[m.kind] || GEO.bush;
    const strips = order.map((id, i) => (id === c.id ? i : -1)).filter((i) => i >= 0);
    const count = strips.length * ROWS * COLS;
    const body = new THREE.InstancedMesh(bodyGeo, new THREE.MeshStandardMaterial({ roughness: 0.85, flatShading: true }), count);
    const acc = new THREE.InstancedMesh(accGeo, new THREE.MeshStandardMaterial({ roughness: 0.6, flatShading: true }), count);
    body.castShadow = true;
    acc.castShadow = true;
    body.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    acc.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    const plants = [];
    strips.forEach((s) => {
      const x0 = -FIELD_W / 2 + sw * (s + 0.5);
      for (let r = 0; r < ROWS; r++) {
        for (let k = 0; k < COLS; k++) {
          plants.push({
            x: x0 + (k - (COLS - 1) / 2) * sw * 0.38 + (rnd() - 0.5) * 0.12,
            z: -FIELD_D / 2 + 1.0 + (r + 0.5) * ((FIELD_D - 2.8) / ROWS) + (rnd() - 0.5) * 0.25,
            rot: rnd() * Math.PI * 2,
            v: 0.85 + rnd() * 0.3,
            order: r / ROWS + rnd() * 0.06,
            strip: s,
          });
        }
      }
    });
    body.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(count * 3), 3);
    acc.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(count * 3), 3);
    planGroup.add(body);
    planGroup.add(acc);
    cropObjs.push({ id: c.id, ci, body, acc, plants, meta: m, sow: parseDate(c.sow), hs: parseDate(c.harvest_start), he: parseDate(c.harvest_end),
                    strips, flower: new THREE.Color(m.flower), mature: new THREE.Color(m.mature) });
  });
  // pests hover over the targeted crop
  const w = twin.what_if;
  pests.userData.base = [];
  if (w.kind === 'pest' && w.crop) {
    const target = cropObjs.find((c) => c.id === w.crop);
    if (target) {
      const pos = pestGeo.attributes.position.array;
      for (let i = 0; i < PEST_N; i++) {
        const s = target.strips[i % target.strips.length];
        const b = [-FIELD_W / 2 + sw * (s + 0.5) + (rnd() - 0.5) * sw, BED_Y + 0.6 + rnd() * 1.4, (rnd() - 0.5) * (FIELD_D - 3)];
        pests.userData.base.push(b);
        pos.set(b, i * 3);
      }
      pestGeo.attributes.position.needsUpdate = true;
    }
  }
}

// ---------- updates ----------
const dummy = new THREE.Object3D();
const tmp = new THREE.Color();
const ease = (x) => 1 - Math.pow(1 - Math.min(1, Math.max(0, x)), 3);
const lerp = (a, b, f) => a + (b - a) * f;

function weekValue(arr, tt) {
  const i = Math.floor(tt), f = tt - i, j = Math.min(arr.length - 1, i + 1);
  return lerp(arr[Math.min(i, arr.length - 1)], arr[j], f);
}

function updatePlants(tt, weather) {
  const nW = twin.weeks.length;
  const wi = Math.min(nW - 1, Math.floor(tt));
  const day = new Date(parseDate(twin.weeks[0]).getTime() + tt * 7 * DAY + 3 * DAY);
  const bloom = introT; // plants pop in after the intro
  cropObjs.forEach((c) => {
    const stage = twin.stage[c.ci][wi];
    const g = weekValue(twin.growth[c.ci], tt);
    const h = weekValue(twin.health[c.ci], tt);
    const hp = (day - c.hs) / (c.he - c.hs + DAY);
    for (let p = 0; p < c.plants.length; p++) {
      const pl = c.plants[p];
      const { sy, sxz, accS, col, accCol, harvested, sown } = plantLook(c, pl, stage, g, h, hp, day, weather, bloom);
      dummy.position.set(pl.x, BED_Y, pl.z);
      dummy.rotation.set(0, pl.rot, 0);
      dummy.scale.set(Math.max(0.0001, sxz), Math.max(0.0001, sy), Math.max(0.0001, sxz));
      dummy.updateMatrix();
      c.body.setMatrixAt(p, dummy.matrix);
      c.body.setColorAt(p, col);
      const a = harvested || !sown ? 0.0001 : Math.max(0.0001, accS);
      dummy.scale.set(sxz * a, sy * a + 0.0001, sxz * a);
      dummy.updateMatrix();
      c.acc.setMatrixAt(p, dummy.matrix);
      c.acc.setColorAt(p, accCol);
    }
    c.body.instanceMatrix.needsUpdate = true;
    c.acc.instanceMatrix.needsUpdate = true;
    c.body.instanceColor.needsUpdate = true;
    c.acc.instanceColor.needsUpdate = true;
  });
}

function updateEnvironment(weather, dt, irrigating) {
  const target = SKY[weather] || SKY.clear;
  scene.background.lerp(target, Math.min(1, dt * 2));
  scene.fog.color.copy(scene.background);
  sun.intensity = lerp(sun.intensity, SUN[weather] || 2.5, Math.min(1, dt * 2));
  rainMat.opacity = lerp(rainMat.opacity, weather === 'rain' ? 0.75 : 0, Math.min(1, dt * 2.5));
  cloudMat.color.lerp(weather === 'rain' ? C('#8e99a3') : C('#ffffff'), Math.min(1, dt * 2));
  cloudMat.opacity = lerp(cloudMat.opacity, weather === 'dry' ? 0.25 : 0.92, Math.min(1, dt * 2));
  if (rainMat.opacity > 0.02) {
    const pos = rainGeo.attributes.position.array;
    for (let i = 0; i < RAIN_N; i++) {
      pos[i * 3 + 1] -= dt * 38;
      if (pos[i * 3 + 1] < 0) pos[i * 3 + 1] += 45;
    }
    rainGeo.attributes.position.needsUpdate = true;
  }
  clouds.children.forEach((g) => { g.position.x += dt * g.userData.v; if (g.position.x > 90) g.position.x = -90; });
  const soil = weather === 'rain' ? SOIL.wet : weather === 'dry' ? SOIL.parched : SOIL.dry;
  beds.forEach((b) => {
    const wet = irrigating && args.crops[b.userData.crop].irrigated ? SOIL.wet : soil;
    b.material.color.lerp(wet, Math.min(1, dt * 3));
  });
  const pulse = 0.6 + 0.4 * Math.sin(performance.now() / 300);
  drips.forEach((d) => { d.material.emissiveIntensity = irrigating ? pulse : 0; });
  ribbons.forEach((r) => { r.scale.y = Math.min(1, Math.max(0.001, (introT * 1.6 - r.userData.delay))); });
}

function updatePests(tt) {
  const w = twin && twin.what_if;
  const on = mode === 'plan' && w && w.kind === 'pest' && pests.userData.base.length && tt >= w.week;
  const target = on ? cropObjs.find((c) => c.id === w.crop) : null;
  const active = target && twin.stage[target.ci][Math.min(twin.weeks.length - 1, Math.floor(tt))] < 5;
  pestMat.opacity = lerp(pestMat.opacity, active ? 0.95 : 0, 0.08);
  if (pestMat.opacity > 0.02) {
    const pos = pestGeo.attributes.position.array, now = performance.now() / 600;
    pests.userData.base.forEach((b, i) => {
      pos[i * 3] = b[0] + Math.sin(now + i) * 0.4;
      pos[i * 3 + 1] = b[1] + Math.sin(now * 1.7 + i * 0.5) * 0.3;
      pos[i * 3 + 2] = b[2] + Math.cos(now + i * 0.7) * 0.4;
    });
    pestGeo.attributes.position.needsUpdate = true;
  }
}

// ---------- HUD ----------
const $ = (id) => document.getElementById(id);
const L = (k, p = {}) => {
  let s = (args && args.labels && args.labels[k]) || k;
  Object.entries(p).forEach(([a, b]) => { s = s.split('{' + a + '}').join(b); });
  return s;
};
const inr = (v) => {
  const neg = v < 0; let s = Math.round(Math.abs(v)).toString();
  if (s.length > 3) { let head = s.slice(0, -3); const tail = s.slice(-3); const parts = []; while (head.length > 2) { parts.unshift(head.slice(-2)); head = head.slice(0, -2); } if (head) parts.unshift(head); s = parts.join(',') + ',' + tail; }
  return (neg ? '−₹' : '₹') + s;
};
const fmtDate = (d) => `${d.getDate()} ${args.months[d.getMonth()]} ${d.getFullYear()}`;
const WX_ICON = { rain: '🌧', dry: '☀️', clear: '⛅' };
const EV_ICON = { ev_sow: '🌱', ev_flower: '🌸', ev_harvest: '🌾', ev_done: '✅', ev_dry_spell: '☀️', ev_pest: '🐛', ev_price: '📉', ev_water_cut: '🚱' };

function cropName(id) { return id && args.crops[id] ? args.crops[id].name : L('all_crops'); }

function buildHud() {
  const plan = mode === 'plan';
  $('controls').classList.toggle('hidden', !plan);
  $('mini').classList.toggle('hidden', !plan);
  $('crops').classList.toggle('hidden', !plan);
  $('k_sales').textContent = plan ? L('sales') : L('plot');
  $('k_water').textContent = plan ? L('water_week') : L('water');
  $('k_labour').textContent = plan ? L('labour_week') : L('season');
  if (!plan) {
    $('v_sales').innerHTML = `${args.farm.acres_label}`;
    $('v_water').innerHTML = `<span style="font-size:15px">${args.farm.water_label}</span>`;
    $('v_labour').innerHTML = `<span style="font-size:15px">${args.farm.season_label}</span>`;
    $('date').textContent = args.farm.title;
    $('weekline').textContent = args.farm.subtitle;
    $('wx').textContent = '';
    $('progress').style.width = '0%';
    return;
  }
  // crops panel
  $('crops').innerHTML = twin.crops.map((c) => {
    const m = args.crops[c.id];
    return `<div class="crop" data-id="${c.id}"><div class="top"><span class="dot" style="background:${m.color}"></span><span title="${m.name}">${m.short}</span><span class="share">${Math.round(c.share * 100)}% · ${c.acres.toFixed(2)} ${L('acre')}</span></div>
      <div class="stage"><b class="st">—</b><span class="pc"></span></div><div class="g"><i style="background:${m.color}"></i></div><div class="hl"></div></div>`;
  }).join('');
  // speed buttons
  $('speed').innerHTML = [0.5, 1, 2, 4].map((s) => `<button data-s="${s}" class="${s === speed ? 'on' : ''}">${s}×</button>`).join('');
  $('speed').querySelectorAll('button').forEach((b) => b.onclick = () => { speed = +b.dataset.s; buildSpeed(); });
  // scrubber, ticks, months
  const n = twin.weeks.length;
  const sc = $('scrub');
  sc.max = n - 1;
  $('ticks').innerHTML = twin.events.map((e) => {
    const col = e.crop && args.crops[e.crop] ? args.crops[e.crop].color : '#b0412a';
    return `<span title="${L(e.key, { crop: cropName(e.crop) })}" style="left:${(e.week / (n - 1)) * 100}%;background:${col}"></span>`;
  }).join('');
  const seen = new Set(), ms = [];
  twin.weeks.forEach((w) => { const d = parseDate(w); const k = d.getMonth(); if (!seen.has(k)) { seen.add(k); ms.push(args.months[k]); } });
  $('months').innerHTML = ms.map((m) => `<span>${m}</span>`).join('');
  $('mini_t').textContent = L('mini_title');
  $('mini_leg').innerHTML = `<span><i style="background:#4a90d9"></i>${L('legend_water')}</span><span><i style="background:#1d7a3e"></i>${L('legend_sales')}</span>` +
    (twin.what_if.kind !== 'none' ? `<span><i style="background:#999"></i>${L('legend_ref')}</span>` : '');
}
function buildSpeed() { $('speed').querySelectorAll('button').forEach((b) => b.classList.toggle('on', +b.dataset.s === speed)); }

function drawMini(tt) {
  const cv = $('minic'), g = cv.getContext('2d'), W = cv.width, H = cv.height;
  g.clearRect(0, 0, W, H);
  const n = twin.weeks.length, bw = W / n;
  const wmax = Math.max(...twin.water_m3, 1);
  twin.water_m3.forEach((v, i) => {
    const h = (v / wmax) * (H * 0.55);
    g.fillStyle = i <= tt ? '#4a90d9' : 'rgba(74,144,217,0.25)';
    g.fillRect(i * bw + 1, H - h, bw - 2, h);
  });
  const smax = Math.max(twin.ref_cum_sales[n - 1], twin.cum_sales[n - 1], 1);
  const line = (arr, color, dash) => {
    g.beginPath(); g.setLineDash(dash); g.strokeStyle = color; g.lineWidth = 4;
    arr.forEach((v, i) => { const x = i * bw + bw / 2, y = H - 6 - (v / smax) * (H - 14); i ? g.lineTo(x, y) : g.moveTo(x, y); });
    g.stroke(); g.setLineDash([]);
  };
  if (twin.what_if.kind !== 'none') line(twin.ref_cum_sales, '#9a9a9a', [10, 8]);
  line(twin.cum_sales, '#1d7a3e', []);
  g.strokeStyle = '#13231a'; g.lineWidth = 2; g.beginPath();
  const x = tt * bw + bw / 2; g.moveTo(x, 0); g.lineTo(x, H); g.stroke();
}

let lastHudWeek = -2;
function updateHud(tt) {
  if (mode !== 'plan') return;
  const n = twin.weeks.length, wi = Math.min(n - 1, Math.floor(tt));
  const day = new Date(parseDate(twin.weeks[0]).getTime() + tt * 7 * DAY);
  $('date').textContent = fmtDate(day);
  $('weekline').textContent = L('week_of', { i: wi + 1, n });
  $('progress').style.width = `${(tt / (n - 1)) * 100}%`;
  const wx = twin.weather[wi];
  $('wx').textContent = `${WX_ICON[wx]} ${L('wx_' + wx)}`;
  const sales = weekValue(twin.cum_sales, tt), total = twin.totals.scenario_gross;
  const down = twin.what_if.kind !== 'none' && total < twin.totals.reference_gross - 1;
  $('v_sales').innerHTML = `${inr(sales)} <small>/ ${inr(total)}</small>`;
  $('v_sales').classList.toggle('down', down);
  const irr = twin.irrigation_m3[wi];
  $('v_water').innerHTML = `${Math.round(twin.water_m3[wi])} <small>m³${irr > 0.5 ? ' · 💧' + Math.round(irr) : ''}</small>`;
  $('v_labour').innerHTML = `${twin.labour_days[wi].toFixed(1)} <small>${L('person_days')}</small>`;
  document.querySelectorAll('#crops .crop').forEach((el) => {
    const c = twin.crops.find((x) => x.id === el.dataset.id), ci = c.index;
    const st = twin.stage[ci][wi], g = weekValue(twin.growth[ci], tt), h = weekValue(twin.health[ci], tt);
    el.querySelector('.st').textContent = L('stage_' + st);
    const hs = parseDate(c.harvest_start), he = parseDate(c.harvest_end);
    const pct = st === 5 ? Math.min(1, (day - hs) / (he - hs + DAY)) : st === 6 ? 1 : g;
    el.querySelector('.pc').textContent = st === 0 ? `${L('sow_on')} ${fmtDate(parseDate(c.sow))}` : st === 5 ? `${L('harvested')} ${Math.round(pct * 100)}%` : st === 6 ? '' : `${Math.round(g * 100)}%`;
    el.querySelector('.g i').style.width = `${Math.round(pct * 100)}%`;
    el.querySelector('.hl').textContent = h < 0.999 ? `${L('health')} ${Math.round(h * 100)}%` : '';
  });
  if (wi !== lastHudWeek) { drawMini(tt); lastHudWeek = wi; }
  $('scrub').value = tt;
}

function fireEvents(tt) {
  if (mode !== 'plan' || !playing) return;
  const wk = Math.floor(tt);
  if (wk <= firedUpTo) return;
  twin.events.filter((e) => e.week > firedUpTo && e.week <= wk).slice(0, 3).forEach((e) => {
    const el = document.createElement('div');
    el.className = 'toast';
    el.textContent = `${EV_ICON[e.key] || '•'} ${L(e.key, { crop: cropName(e.crop) })}`;
    $('toasts').appendChild(el);
    setTimeout(() => el.remove(), 3300);
  });
  firedUpTo = wk;
}

// floating crop labels
const v3 = new THREE.Vector3();
function updateLabels(tt) {
  const box = $('labels');
  if (mode !== 'plan') {
    box.innerHTML = '';
    if (args && args.farm) {
      const items = [[new THREE.Vector3(0, 1.0, FIELD_D / 2 + 1.5), args.farm.width_label], [new THREE.Vector3(FIELD_W / 2 + 1.5, 1.0, 0), args.farm.depth_label]];
      box.innerHTML = items.map(([p, txt]) => { p.project(camera); return p.z < 1 ? `<div class="chip dim" style="left:${(p.x + 1) / 2 * box.clientWidth}px;top:${(1 - p.y) / 2 * box.clientHeight}px">${txt}</div>` : ''; }).join('');
    }
    return;
  }
  const wi = Math.min(twin.weeks.length - 1, Math.floor(tt));
  const sw = FIELD_W / twin.strip_order.length;
  const nC = cropObjs.length;
  box.innerHTML = cropObjs.map((c, k) => {
    // spread chips across the field: each crop's strip nearest to its own slot
    const target = (0.08 + 0.62 * (k + 0.5) / nC) * twin.strip_order.length; // right side sits under the crop panel
    const s = c.strips.reduce((best, x) => (Math.abs(x + 0.5 - target) < Math.abs(best + 0.5 - target) ? x : best), c.strips[0]);
    const g = twin.growth[c.ci][wi];
    v3.set(-FIELD_W / 2 + sw * (s + 0.5), BED_Y + c.meta.height * Math.max(0.2, g) + 1.4, -FIELD_D / 2 + 2 + k * (FIELD_D * 0.62) / Math.max(1, nC - 1));
    v3.project(camera);
    if (v3.z > 1) return '';
    const x = (v3.x + 1) / 2 * box.clientWidth, y = (1 - v3.y) / 2 * box.clientHeight;
    return `<div class="chip" style="left:${x}px;top:${y}px"><span class="sw" style="background:${c.meta.color}"></span>${c.meta.short}<small>${Math.round(twin.crops[c.ci].share * 100)}%</small></div>`;
  }).join('');
}

// hover tooltip
const ray = new THREE.Raycaster(), mouse = new THREE.Vector2();
canvas.addEventListener('pointermove', (e) => {
  if (mode !== 'plan') return;
  const r = canvas.getBoundingClientRect();
  mouse.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(mouse, camera);
  const hit = ray.intersectObjects(beds, false)[0];
  const tip = $('tip');
  if (!hit) { tip.style.display = 'none'; return; }
  const { strip, crop } = hit.object.userData;
  const c = twin.crops.find((x) => x.id === crop), wi = Math.min(twin.weeks.length - 1, Math.floor(t));
  const acres = args.farm.acres / twin.strip_order.length;
  tip.innerHTML = `<b>${args.crops[crop].name}</b><br>${L('strip')} ${strip + 1} · ${acres.toFixed(3)} ${L('acre')}<br>${L('stage_' + twin.stage[c.index][wi])}`;
  tip.style.left = `${e.clientX - r.left}px`;
  tip.style.top = `${e.clientY - r.top}px`;
  tip.style.display = 'block';
});
canvas.addEventListener('pointerleave', () => { $('tip').style.display = 'none'; });

// ---------- controls ----------
function setPlaying(p) { playing = p; $('b_play').textContent = p ? '❚❚' : '▶'; if (p && t >= twin.weeks.length - 1.001) { t = 0; firedUpTo = -1; } }
$('b_play').onclick = () => setPlaying(!playing);
$('b_restart').onclick = () => { t = 0; firedUpTo = -1; setPlaying(false); };
$('b_back').onclick = () => { setPlaying(false); t = Math.max(0, Math.ceil(t) - 1); firedUpTo = Math.floor(t); };
$('b_fwd').onclick = () => { setPlaying(false); t = Math.min(twin.weeks.length - 1, Math.floor(t) + 1); firedUpTo = Math.floor(t); };
$('scrub').oninput = (e) => { setPlaying(false); t = +e.target.value; firedUpTo = Math.floor(t); };
$('b_orbit').onclick = () => { autoRotate = !autoRotate; controls.autoRotate = autoRotate; };
$('b_top').onclick = () => { camFly = { from: camera.position.clone(), to: TOP.clone(), t: 0 }; };
$('b_home').onclick = () => { camFly = { from: camera.position.clone(), to: HOME.clone(), t: 0 }; };
window.addEventListener('keydown', (e) => { if (e.code === 'Space' && mode === 'plan') { e.preventDefault(); setPlaying(!playing); } });

// ---------- sizing ----------
function resize() {
  const st = $('stage');
  const w = st.clientWidth;
  const h = Math.max(420, Math.min(args ? args.height : 620, Math.round(w * 0.72)));
  st.style.height = (w < 760 ? Math.max(440, Math.round(w * 1.15)) : h) + 'px';
  renderer.setSize(st.clientWidth, st.clientHeight, false);
  camera.aspect = st.clientWidth / st.clientHeight;
  camera.fov = w < 760 ? 52 : 40;
  camera.updateProjectionMatrix();
  setHeight();
}
new ResizeObserver(resize).observe(document.body);

// ---------- intro ----------
function intro(text, sub) {
  $('introText').innerHTML = `${text}<small>${sub || ''}</small>`;
  $('intro').classList.remove('hidden');
  $('introText').style.opacity = 1;
  setTimeout(() => { $('introText').style.opacity = 0; }, 1900);
  setTimeout(() => $('intro').classList.add('hidden'), 2600);
}

// ---------- receive data ----------
window.addEventListener('message', (event) => {
  if (!event.data || event.data.type !== 'streamlit:render') return;
  const a = event.data.args;
  if (a.version === version) return;
  const newPlan = a.plan_key !== planKey || a.mode !== mode;
  args = a; version = a.version; mode = a.mode; planKey = a.plan_key; twin = a.twin;
  buildWater(a.farm.water);
  if (newPlan) {
    // (layout seed reset in buildPlan)
    buildPlan();
    t = 0; firedUpTo = -1; introT = 0;
    camFly = { from: new THREE.Vector3(0.01, 95, 20), to: HOME.clone(), t: 0 };
    plate.scale.set(0.001, 1, 0.001);
    intro(mode === 'plan' ? L('intro_plan') : L('intro_preview'), mode === 'plan' ? L('intro_plan_sub') : L('intro_preview_sub'));
    if (mode === 'plan' && a.autoplay) {
      setTimeout(() => setPlaying(true), 2600);
      // bring the freshly planted field into view
      try { window.frameElement && window.frameElement.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch (e) { /* cross-origin: ignore */ }
    }
  } else if (mode === 'plan') {
    buildPlan(); // scenario changed: same plan, new outcomes
    introT = 1;
    const w = twin.what_if;
    if (w && w.kind && w.kind !== 'none') {
      // replay from just before the shock so its effect is seen on the field
      t = Math.max(0, Math.min(twin.weeks.length - 1, (w.week || 0) - 1));
      firedUpTo = Math.floor(t) - 1;
      setPlaying(true);
    }
  }
  buildHud();
  lastHudWeek = -2;
  resize();
});

// ---------- loop ----------
function frame(now) {
  const dt = Math.min(0.05, (now - lastFrame) / 1000);
  lastFrame = now;
  introT = Math.min(1, introT + dt / 2.2);
  const s = ease(introT);
  plate.scale.set(Math.max(0.001, s), 1, Math.max(0.001, s));
  if (camFly) {
    camFly.t = Math.min(1, camFly.t + dt / 2.2);
    camera.position.lerpVectors(camFly.from, camFly.to, ease(camFly.t));
    if (camFly.t >= 1) camFly = null;
  }
  let weather = args && args.farm && args.farm.season === 'kharif' ? 'rain' : 'clear';
  let irrigating = false;
  if (mode === 'plan' && twin) {
    const n = twin.weeks.length;
    if (playing) {
      t += dt * speed / 0.9;
      if (t >= n - 1) { t = n - 1; setPlaying(false); }
    }
    const wi = Math.min(n - 1, Math.floor(t));
    weather = twin.weather[wi];
    irrigating = twin.irrigation_m3[wi] > 0.5;
    updatePlants(t, weather);
    updateHud(t);
    fireEvents(t);
  }
  updateEnvironment(weather, dt, irrigating);
  updatePests(t);
  controls.update();
  renderer.render(scene, camera);
  updateLabels(t);
  adaptQuality(dt);
  requestAnimationFrame(frame);
}
// slow device (no GPU, old phone): drop resolution and soften shadows instead of stuttering
let slowFrames = 0, quality = 2;
function adaptQuality(dt) {
  if (quality === 0 || dt <= 0) return;
  slowFrames = dt > 0.045 ? slowFrames + 1 : Math.max(0, slowFrames - 1);
  if (slowFrames < 40) return;
  slowFrames = 0;
  quality -= 1;
  if (quality === 1) renderer.setPixelRatio(1);
  else { renderer.shadowMap.type = THREE.PCFShadowMap; sun.shadow.mapSize.set(1024, 1024); if (sun.shadow.map) { sun.shadow.map.dispose(); sun.shadow.map = null; } renderer.setPixelRatio(0.75); }
  resize();
}
post('streamlit:componentReady', { apiVersion: 1 });
resize();
requestAnimationFrame(frame);
