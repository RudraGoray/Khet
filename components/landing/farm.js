// Landing-page 3D farm. Uses the dashboard twin's kit (../twin/farmkit.js) and the sample plan's
// real twin timeline from Python, so crops grow exactly as they do in the app.
import * as THREE from '../twin/vendor/three.module.min.js';
import { FIELD_W, FIELD_D, BED_Y, ROWS, COLS, SOIL, C, seeded, noiseTexture, addTree, addHouse, plantGeometries, plantLook } from '../twin/farmkit.js';

const DAY = 86400000;
const parseDate = (s) => new Date(s + 'T00:00:00');
const SKY = { day: C('#cfe3ea'), rain: C('#a9b8c2'), dry: C('#f1d9ab'), golden: C('#f2c98f') };

export function createFarm(canvas, data, opts = {}) {
  const small = opts.small;
  const rnd = seeded(7);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: !small, powerPreference: 'high-performance' });
  let dpr = Math.min(window.devicePixelRatio || 1, small ? 1.25 : 1.6);
  renderer.setPixelRatio(dpr);
  renderer.shadowMap.enabled = !small;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.08;
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const scene = new THREE.Scene();
  scene.background = SKY.day.clone();
  scene.fog = new THREE.Fog(scene.background.clone(), 80, 260);
  const camera = new THREE.PerspectiveCamera(36, 1, 0.5, 700);
  camera.position.set(70, 50, 95);
  const look = new THREE.Vector3(0, 1, 0);

  const hemi = new THREE.HemisphereLight('#e6f2ff', '#6b5a3a', 1.05);
  scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff1d6', 2.6);
  sun.position.set(45, 60, 25);
  sun.castShadow = !small;
  sun.shadow.mapSize.set(1536, 1536);
  Object.assign(sun.shadow.camera, { left: -45, right: 45, top: 40, bottom: -40, near: 5, far: 180 });
  sun.shadow.bias = -0.0005;
  scene.add(sun);

  // ---------- world ----------
  const grassTex = noiseTexture(rnd, '#7ea653', 0.12);
  grassTex.repeat.set(36, 36);
  const ground = new THREE.Mesh(new THREE.CircleGeometry(320, 64), new THREE.MeshStandardMaterial({ map: grassTex, roughness: 1 }));
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);
  const trees = [];
  for (let i = 0; i < 60; i++) {
    const a = rnd() * Math.PI * 2, r = 40 + rnd() * 90;
    const x = Math.cos(a) * r, z = Math.sin(a) * r;
    if (Math.abs(x) < 30 && Math.abs(z) < 24) continue;
    trees.push(addTree(scene, rnd, x, z, 0.9 + rnd() * 0.9));
  }
  addHouse(scene, -FIELD_W / 2 - 12, -FIELD_D / 2 - 4, 0.5);
  const bund = new THREE.Mesh(new THREE.BoxGeometry(FIELD_W + 2.4, 0.5, FIELD_D + 2.4), new THREE.MeshStandardMaterial({ color: '#7d6040', roughness: 1 }));
  bund.position.y = 0.25;
  bund.receiveShadow = true;
  scene.add(bund);
  const plate = new THREE.Mesh(new THREE.BoxGeometry(FIELD_W, 0.3, FIELD_D), new THREE.MeshStandardMaterial({ map: noiseTexture(rnd, '#8f6c49', 0.1, 256, 24), roughness: 1 }));
  plate.position.y = 0.5;
  plate.receiveShadow = true;
  scene.add(plate);
  // the sample farm has limited water: an open well, as in the dashboard twin
  (function well() {
    const g = new THREE.Group();
    const ring = new THREE.Mesh(new THREE.CylinderGeometry(1.6, 1.8, 1.1, 18, 1, true), new THREE.MeshStandardMaterial({ color: '#9a9488', roughness: 1, side: THREE.DoubleSide }));
    ring.position.y = 0.55;
    const water = new THREE.Mesh(new THREE.CircleGeometry(1.55, 24), new THREE.MeshStandardMaterial({ color: '#3d7fb0', roughness: 0.2 }));
    water.rotation.x = -Math.PI / 2;
    water.position.y = 0.8;
    const wood = new THREE.MeshStandardMaterial({ color: '#6b4a2f' });
    const p1 = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 2.6), wood), p2 = p1.clone();
    p1.position.set(-1.5, 1.3, 0); p2.position.set(1.5, 1.3, 0);
    const beam = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 3.2), wood);
    beam.rotation.z = Math.PI / 2; beam.position.y = 2.5;
    [ring, water, p1, p2, beam].forEach((m) => { m.castShadow = true; g.add(m); });
    g.position.set(FIELD_W / 2 + 4, 0, FIELD_D / 2 - 3);
    scene.add(g);
    g.userData.water = water;
    scene.userData.well = g;
  })();

  // clouds, rain, birds, pests
  const cloudMat = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: 1, transparent: true, opacity: 0.95, flatShading: true });
  const clouds = new THREE.Group();
  for (let i = 0; i < 11; i++) {
    const g = new THREE.Group();
    for (let k = 0; k < 4; k++) {
      const m = new THREE.Mesh(new THREE.IcosahedronGeometry(3 + rnd() * 2.5, 1), cloudMat);
      m.position.set(k * 3.2 - 5, rnd() * 1.5, rnd() * 2);
      m.scale.y = 0.55;
      g.add(m);
    }
    g.position.set((rnd() - 0.5) * 220, 58 + rnd() * 16, (rnd() - 0.5) * 180);
    g.userData.v = 0.5 + rnd() * 0.8;
    clouds.add(g);
  }
  scene.add(clouds);
  const RAIN_N = small ? 1200 : 2400;
  const rainGeo = new THREE.BufferGeometry();
  const rainPos = new Float32Array(RAIN_N * 3);
  for (let i = 0; i < RAIN_N; i++) { rainPos[i * 3] = (rnd() - 0.5) * 100; rainPos[i * 3 + 1] = rnd() * 45; rainPos[i * 3 + 2] = (rnd() - 0.5) * 90; }
  rainGeo.setAttribute('position', new THREE.BufferAttribute(rainPos, 3));
  const rainMat = new THREE.PointsMaterial({ color: '#e2edff', size: 0.2, transparent: true, opacity: 0, depthWrite: false });
  scene.add(new THREE.Points(rainGeo, rainMat));
  const birds = [];
  const birdMat = new THREE.MeshBasicMaterial({ color: '#23372b', side: THREE.DoubleSide });
  for (let i = 0; i < 7; i++) {
    const b = new THREE.Group();
    const wing = new THREE.Mesh(new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute([0, 0, 0, 0.9, 0, -0.35, 0, 0, -0.5], 3)), birdMat);
    const w2 = wing.clone(); w2.scale.x = -1;
    b.add(wing, w2);
    b.userData = { wing, w2, r: 30 + i * 2.2, h: 22 + (i % 3) * 1.6, off: i * 0.35, sp: 0.09 + (i % 2) * 0.012 };
    birds.push(b);
    scene.add(b);
  }
  const PEST_N = 220;
  const pestGeo = new THREE.BufferGeometry();
  pestGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(PEST_N * 3), 3));
  const pestMat = new THREE.PointsMaterial({ color: '#c8322a', size: 0.34, transparent: true, opacity: 0, depthWrite: false });
  scene.add(new THREE.Points(pestGeo, pestMat));
  const pestBase = [];

  // ---------- the sample plan, planted ----------
  const ok = data && data.ok;
  const tw = ok ? data.twin : null;
  const GEO = plantGeometries();
  const beds = [], drips = [], crops = [];
  if (ok) {
    const order = tw.strip_order, sw = FIELD_W / order.length;
    order.forEach((cid, i) => {
      const x = -FIELD_W / 2 + sw * (i + 0.5);
      const bed = new THREE.Mesh(new THREE.BoxGeometry(sw * 0.8, 0.25, FIELD_D - 1.2), new THREE.MeshStandardMaterial({ color: SOIL.dry.clone(), roughness: 1 }));
      bed.position.set(x, BED_Y - 0.125, -0.2);
      bed.receiveShadow = true;
      bed.userData.crop = cid;
      scene.add(bed);
      beds.push(bed);
      const m = data.crops[cid];
      const rib = new THREE.Mesh(new THREE.BoxGeometry(sw * 0.8, 0.16, 0.7), new THREE.MeshStandardMaterial({ color: m.color, roughness: 0.5, emissive: m.color, emissiveIntensity: 0.15 }));
      rib.position.set(x, BED_Y + 0.02, FIELD_D / 2 - 0.45);
      scene.add(rib);
      if (m.irrigated) {
        const d = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, FIELD_D - 1.4, 6), new THREE.MeshStandardMaterial({ color: '#2f6fa8', emissive: '#4aa3ff', emissiveIntensity: 0 }));
        d.rotation.x = Math.PI / 2;
        d.position.set(x, BED_Y + 0.06, -0.2);
        scene.add(d);
        drips.push(d);
      }
    });
    tw.crops.forEach((c, ci) => {
      const m = data.crops[c.id];
      const [bodyGeo, accGeo] = GEO[m.kind] || GEO.bush;
      const strips = order.map((id, i) => (id === c.id ? i : -1)).filter((i) => i >= 0);
      const count = strips.length * ROWS * COLS;
      const body = new THREE.InstancedMesh(bodyGeo, new THREE.MeshStandardMaterial({ roughness: 0.85, flatShading: true }), count);
      const acc = new THREE.InstancedMesh(accGeo, new THREE.MeshStandardMaterial({ roughness: 0.6, flatShading: true }), count);
      body.castShadow = acc.castShadow = !small;
      body.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(count * 3), 3);
      acc.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(count * 3), 3);
      const plants = [];
      strips.forEach((s) => {
        const x0 = -FIELD_W / 2 + sw * (s + 0.5);
        for (let r = 0; r < ROWS; r++) for (let k = 0; k < COLS; k++) {
          plants.push({ x: x0 + (k - (COLS - 1) / 2) * sw * 0.38 + (rnd() - 0.5) * 0.12, z: -FIELD_D / 2 + 1.0 + (r + 0.5) * ((FIELD_D - 2.8) / ROWS) + (rnd() - 0.5) * 0.25,
            rot: rnd() * Math.PI * 2, v: 0.85 + rnd() * 0.3, order: r / ROWS + rnd() * 0.06 });
        }
      });
      scene.add(body, acc);
      crops.push({ id: c.id, ci, body, acc, plants, strips, meta: m, sow: parseDate(c.sow), hs: parseDate(c.harvest_start), he: parseDate(c.harvest_end),
                   flower: new THREE.Color(m.flower), mature: new THREE.Color(m.mature) });
    });
  }

  // ---------- state ----------
  const st = { week: 0, scenario: null, mood: 'day', weatherOverride: null, bloom: 1, active: true, pose: null, offsetX: 0, offsetY: 0, pointer: { x: 0, y: 0 } };
  const camGoal = { pos: camera.position.clone(), look: look.clone() };
  const dummy = new THREE.Object3D();
  const lerp = (a, b, f) => a + (b - a) * f;
  const weekVal = (arr, tt) => { const i = Math.floor(tt), f = tt - i; const a = arr[Math.min(i, arr.length - 1)], b = arr[Math.min(arr.length - 1, i + 1)]; return lerp(a, b, f); };

  function setPest(target) {
    pestBase.length = 0;
    if (!target) return;
    const sw = FIELD_W / tw.strip_order.length, pos = pestGeo.attributes.position.array;
    for (let i = 0; i < PEST_N; i++) {
      const s = target.strips[i % target.strips.length];
      const b = [-FIELD_W / 2 + sw * (s + 0.5) + (rnd() - 0.5) * sw, BED_Y + 0.6 + rnd() * 1.4, (rnd() - 0.5) * (FIELD_D - 3)];
      pestBase.push(b);
      pos.set(b, i * 3);
    }
    pestGeo.attributes.position.needsUpdate = true;
  }

  function weather() {
    if (st.weatherOverride) return st.weatherOverride;
    if (st.scenario && st.scenario.kind === 'dry_spell') return 'dry';
    return tw ? tw.weather[Math.min(tw.weeks.length - 1, Math.floor(st.week))] : 'clear';
  }

  function updatePlants(time, wx) {
    if (!ok) return;
    const nW = tw.weeks.length, tt = Math.min(nW - 1, Math.max(0, st.week)), wi = Math.floor(tt);
    const day = new Date(parseDate(tw.weeks[0]).getTime() + tt * 7 * DAY + 3 * DAY);
    const sc = st.scenario;
    crops.forEach((c) => {
      const stage = tw.stage[c.ci][wi];
      const g = weekVal(tw.growth[c.ci], tt);
      const h = sc && sc.health ? weekVal(sc.health[c.ci], tt) : weekVal(tw.health[c.ci], tt);
      const hp = (day - c.hs) / (c.he - c.hs + DAY);
      for (let p = 0; p < c.plants.length; p++) {
        const pl = c.plants[p];
        const L = plantLook(c, pl, stage, g, h, hp, day, wx, st.bloom);
        const sway = small ? 0 : Math.sin(time * 1.5 + pl.x * 0.3 + pl.z * 0.12) * 0.07;
        dummy.position.set(pl.x, BED_Y, pl.z);
        dummy.rotation.set(sway * 0.5, pl.rot, sway);
        dummy.scale.set(Math.max(1e-4, L.sxz), Math.max(1e-4, L.sy), Math.max(1e-4, L.sxz));
        dummy.updateMatrix();
        c.body.setMatrixAt(p, dummy.matrix);
        c.body.setColorAt(p, L.col);
        const a = L.harvested || !L.sown ? 1e-4 : Math.max(1e-4, L.accS);
        dummy.scale.set(L.sxz * a, L.sy * a + 1e-4, L.sxz * a);
        dummy.updateMatrix();
        c.acc.setMatrixAt(p, dummy.matrix);
        c.acc.setColorAt(p, L.accCol);
      }
      c.body.instanceMatrix.needsUpdate = c.acc.instanceMatrix.needsUpdate = true;
      c.body.instanceColor.needsUpdate = c.acc.instanceColor.needsUpdate = true;
    });
  }

  function updateEnv(dt, time, wx) {
    const k = Math.min(1, dt * 2.2);
    const target = st.mood === 'golden' ? SKY.golden : wx === 'rain' ? SKY.rain : wx === 'dry' ? SKY.dry : SKY.day;
    scene.background.lerp(target, k);
    scene.fog.color.copy(scene.background);
    sun.intensity = lerp(sun.intensity, st.mood === 'golden' ? 2.2 : wx === 'rain' ? 1.2 : wx === 'dry' ? 3.1 : 2.6, k);
    sun.color.lerp(st.mood === 'golden' ? C('#ffc58a') : C('#fff1d6'), k);
    const sunPos = st.mood === 'golden' ? [-60, 18, 30] : [45, 60, 25];
    sun.position.set(lerp(sun.position.x, sunPos[0], k), lerp(sun.position.y, sunPos[1], k), lerp(sun.position.z, sunPos[2], k));
    rainMat.opacity = lerp(rainMat.opacity, wx === 'rain' && st.mood !== 'golden' ? 0.7 : 0, Math.min(1, dt * 2.5));
    if (rainMat.opacity > 0.02) {
      for (let i = 0; i < RAIN_N; i++) { rainPos[i * 3 + 1] -= dt * 36; if (rainPos[i * 3 + 1] < 0) rainPos[i * 3 + 1] += 45; }
      rainGeo.attributes.position.needsUpdate = true;
    }
    cloudMat.color.lerp(wx === 'rain' ? C('#909ba5') : st.mood === 'golden' ? C('#ffe2c2') : C('#ffffff'), k);
    cloudMat.opacity = lerp(cloudMat.opacity, wx === 'dry' ? 0.2 : 0.95, k);
    clouds.children.forEach((g) => { g.position.x += dt * g.userData.v; if (g.position.x > 110) g.position.x = -110; });
    const sc = st.scenario;
    const parched = wx === 'dry' || (sc && sc.kind === 'water_cut');
    beds.forEach((b) => {
      const irrigatedCrop = data.crops[b.userData.crop].irrigated;
      const soil = wx === 'rain' ? SOIL.wet : parched && (wx === 'dry' || irrigatedCrop) ? SOIL.parched : SOIL.dry;
      b.material.color.lerp(soil, Math.min(1, dt * 3));
    });
    const dripOn = !(sc && sc.kind === 'water_cut') && wx !== 'rain' && st.mood !== 'golden';
    const pulse = 0.55 + 0.45 * Math.sin(time * 3.2);
    drips.forEach((d) => { d.material.emissiveIntensity = lerp(d.material.emissiveIntensity, dripOn ? pulse : 0, Math.min(1, dt * 4)); });
    const well = scene.userData.well.userData.water;
    well.material.color.lerp(sc && sc.kind === 'water_cut' ? C('#6b5a44') : C('#3d7fb0'), Math.min(1, dt * 2));
    // pests
    const pestOn = sc && sc.kind === 'pest' && pestBase.length;
    pestMat.opacity = lerp(pestMat.opacity, pestOn ? 0.95 : 0, Math.min(1, dt * 3));
    if (pestMat.opacity > 0.02) {
      const pos = pestGeo.attributes.position.array, n = time * 1.6;
      pestBase.forEach((b, i) => { pos[i * 3] = b[0] + Math.sin(n + i) * 0.4; pos[i * 3 + 1] = b[1] + Math.sin(n * 1.7 + i * 0.5) * 0.3; pos[i * 3 + 2] = b[2] + Math.cos(n + i * 0.7) * 0.4; });
      pestGeo.attributes.position.needsUpdate = true;
    }
    // birds glide in a loose loop and flap
    birds.forEach((b) => {
      const u = b.userData, a = time * u.sp + u.off;
      b.position.set(Math.cos(a) * u.r, u.h + Math.sin(time * 0.7 + u.off) * 1.2, Math.sin(a) * u.r * 0.7 - 10);
      b.rotation.y = -a;
      const f = Math.sin(time * 9 + u.off * 4) * 0.6;
      u.wing.rotation.z = f; u.w2.rotation.z = -f;
    });
  }

  // ---------- camera ----------
  function setPose(pos, target) { camGoal.pos.set(...pos); camGoal.look.set(...target); }

  let w = 1, h = 1;
  function resize() {
    w = canvas.clientWidth || window.innerWidth;
    h = canvas.clientHeight || window.innerHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.fov = w < 760 ? 46 : 36;
    applyOffset();
    camera.updateProjectionMatrix();
  }
  let offNow = 0, offYNow = 0;
  // shift the picture sideways (or up) so the field sits beside the text instead of under it
  function applyOffset() {
    if (Math.abs(offNow) > 0.002 || Math.abs(offYNow) > 0.002) camera.setViewOffset(w, h, -offNow * w, offYNow * h, w, h);
    else camera.clearViewOffset();
  }

  let last = performance.now(), slow = 0, quality = 2, running = false, raf = 0;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function frame(now) {
    raf = 0;
    if (!running) return;
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    const time = reduce ? 0 : now / 1000;
    const wx = weather();
    const damp = 1 - Math.exp(-dt * (reduce ? 30 : 3.2));
    const px = st.pointer.x * 3, py = st.pointer.y * 2;
    camera.position.lerp(new THREE.Vector3(camGoal.pos.x + px, camGoal.pos.y + py, camGoal.pos.z), damp);
    look.lerp(camGoal.look, damp);
    camera.lookAt(look);
    offNow = lerp(offNow, st.offsetX, damp);
    offYNow = lerp(offYNow, st.offsetY, damp);
    applyOffset();
    camera.updateProjectionMatrix();
    updatePlants(time, wx);
    updateEnv(dt, time, wx);
    renderer.render(scene, camera);
    // slow device: drop resolution, then shadows
    slow = dt > 0.045 ? slow + 1 : Math.max(0, slow - 1);
    if (slow > 40 && quality > 0) {
      slow = 0; quality -= 1;
      if (quality === 1) { dpr = 1; renderer.setPixelRatio(1); }
      else { renderer.shadowMap.enabled = false; dpr = 0.75; renderer.setPixelRatio(0.75); scene.traverse((o) => { if (o.material) o.material.needsUpdate = true; }); }
      resize();
    }
    raf = requestAnimationFrame(frame);
  }

  return {
    ok,
    resize,
    setWeek(t) { st.week = t; },
    setMood(m) { st.mood = m; },
    setWeather(wx) { st.weatherOverride = wx; },
    setPose,
    setOffset(x, y = 0) { st.offsetX = x; st.offsetY = y; },
    setPointer(x, y) { st.pointer.x = x; st.pointer.y = y; },
    setScenario(kind) {
      if (!ok) return;
      const s = kind ? data.scenarios[kind] : null;
      st.scenario = s ? { kind, health: s.health, crop: s.crop } : null;
      setPest(s && kind === 'pest' ? crops.find((c) => c.id === s.crop) : null);
    },
    start() { if (!running) { running = true; last = performance.now(); raf = requestAnimationFrame(frame); } },
    stop() { running = false; if (raf) cancelAnimationFrame(raf); raf = 0; },
    jump() { camera.position.copy(camGoal.pos); look.copy(camGoal.look); offNow = st.offsetX; offYNow = st.offsetY; },
  };
}
