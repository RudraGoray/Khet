// Shared 3D farm pieces: used by the dashboard twin (twin.js) and the landing page
// (components/landing/farm.js), so both draw the field, trees and crops the same way.
import * as THREE from './vendor/three.module.min.js';
import { mergeGeometries } from './vendor/BufferGeometryUtils.js';

export const FIELD_W = 40, FIELD_D = 28, BED_Y = 0.75, ROWS = 15, COLS = 2;
export const C = (h) => new THREE.Color(h);
export const SKY = { rain: C('#9fb0bd'), dry: C('#f0d3a0'), clear: C('#b9dcf5') };
export const SUN = { rain: 1.0, dry: 3.1, clear: 2.5 };
export const SOIL = { dry: C('#9a7550'), wet: C('#5c4231'), parched: C('#b8956a'), fallow: C('#86674a') };
export const COL = { sprout: C('#8fd16f'), leaf: C('#2f8f3a'), deep: C('#25752f'), stubble: C('#9a7b4f'), sick: C('#b39b48'), dryTint: C('#a7a35a') };

// seeded random, so a farm looks the same on every render
export function seeded(seed) {
  let s = seed;
  const rnd = () => ((s = (s * 16807) % 2147483647) - 1) / 2147483646;
  rnd.reset = (v) => { s = v; };
  return rnd;
}

// ---------- procedural textures ----------
export function noiseTexture(rnd, base, spread, size = 256, stripes = 0) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  const g = c.getContext('2d');
  const col = new THREE.Color(base);
  g.fillStyle = '#' + col.getHexString();
  g.fillRect(0, 0, size, size);
  for (let i = 0; i < size * size / 6; i++) {
    const v = (rnd() - 0.5) * spread;
    const k = col.clone().offsetHSL(0, 0, v);
    g.fillStyle = '#' + k.getHexString();
    g.fillRect(rnd() * size, rnd() * size, 2, 2);
  }
  if (stripes) {
    g.globalAlpha = 0.18;
    g.fillStyle = '#000';
    for (let y = 0; y < size; y += size / stripes) g.fillRect(0, y, size, size / stripes / 3);
    g.globalAlpha = 1;
  }
  const tex = new THREE.CanvasTexture(c);
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

// ---------- world pieces ----------
export function addTree(parent, rnd, x, z, s) {
  const g = new THREE.Group();
  const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.25 * s, 0.35 * s, 2.4 * s, 6), new THREE.MeshStandardMaterial({ color: '#6b4a2f', roughness: 1 }));
  trunk.position.y = 1.2 * s;
  const leafMat = new THREE.MeshStandardMaterial({ color: new THREE.Color('#3f7a35').offsetHSL(0, 0, (rnd() - 0.5) * 0.08), roughness: 0.9, flatShading: true });
  const crown = new THREE.Mesh(new THREE.IcosahedronGeometry(1.9 * s, 0), leafMat);
  crown.position.y = 3.6 * s;
  const crown2 = new THREE.Mesh(new THREE.IcosahedronGeometry(1.3 * s, 0), leafMat);
  crown2.position.set(0.8 * s, 4.6 * s, 0.3 * s);
  [trunk, crown, crown2].forEach((m) => { m.castShadow = true; g.add(m); });
  g.position.set(x, 0, z);
  parent.add(g);
  return g;
}

export function addHouse(parent, x, z, rotY) {
  const g = new THREE.Group();
  const walls = new THREE.Mesh(new THREE.BoxGeometry(7, 3.4, 5), new THREE.MeshStandardMaterial({ color: '#efe3cb', roughness: 0.9 }));
  walls.position.y = 1.7;
  const roof = new THREE.Mesh(new THREE.ConeGeometry(5.6, 2.6, 4), new THREE.MeshStandardMaterial({ color: '#b35a34', roughness: 0.8, flatShading: true }));
  roof.position.y = 4.7;
  roof.rotation.y = Math.PI / 4;
  roof.scale.set(1.05, 1, 0.78);
  const door = new THREE.Mesh(new THREE.BoxGeometry(1.2, 2, 0.1), new THREE.MeshStandardMaterial({ color: '#6b4a2f' }));
  door.position.set(0, 1, 2.55);
  [walls, roof, door].forEach((m) => { m.castShadow = true; m.receiveShadow = true; g.add(m); });
  g.position.set(x, 0, z);
  g.rotation.y = rotY;
  parent.add(g);
  return g;
}

// ---------- plant geometry: bush (pulses, cotton), grass (cereals), stalk (oilseeds) ----------
const ni = (g) => (g.index ? g.toNonIndexed() : g);
function bushGeo() {
  const parts = [ni(new THREE.CylinderGeometry(0.04, 0.06, 0.35, 5)).translate(0, 0.175, 0)];
  [[0, 0.45, 0, 0.34], [0.22, 0.6, 0.1, 0.27], [-0.2, 0.62, -0.08, 0.25], [0.02, 0.82, 0.02, 0.22], [-0.05, 0.55, 0.22, 0.24]]
    .forEach(([x, y, z, r]) => parts.push(new THREE.IcosahedronGeometry(r, 0).translate(x, y, z)));
  return mergeGeometries(parts);
}
function bushAccent() {
  const parts = [];
  for (let i = 0; i < 7; i++) {
    const a = (i / 7) * Math.PI * 2;
    parts.push(new THREE.IcosahedronGeometry(0.075, 0).translate(Math.cos(a) * 0.3, 0.62 + (i % 3) * 0.12, Math.sin(a) * 0.3));
  }
  return mergeGeometries(parts);
}
function grassGeo() {
  const parts = [];
  for (let i = 0; i < 6; i++) {
    const b = ni(new THREE.ConeGeometry(0.06, 1.0, 4)).translate(0, 0.5, 0);
    b.rotateZ((i % 2 ? 1 : -1) * (0.12 + 0.05 * i));
    b.rotateY((i / 6) * Math.PI * 2);
    parts.push(b);
  }
  parts.push(ni(new THREE.CylinderGeometry(0.03, 0.04, 1.05, 5)).translate(0, 0.52, 0));
  return mergeGeometries(parts);
}
function grassAccent() {
  return new THREE.IcosahedronGeometry(0.1, 1).scale(1, 2.3, 1).translate(0, 1.12, 0);
}
function stalkGeo() {
  const parts = [ni(new THREE.CylinderGeometry(0.03, 0.045, 1, 5)).translate(0, 0.5, 0)];
  [0.28, 0.45, 0.62, 0.78].forEach((y, i) => {
    const l = ni(new THREE.ConeGeometry(0.09, 0.34, 4)).translate(0, 0.17, 0);
    l.rotateZ(i % 2 ? 1.0 : -1.0);
    l.rotateY(i * 1.3);
    parts.push(l.translate(0, y, 0));
  });
  return mergeGeometries(parts);
}
function stalkAccent() {
  const parts = [];
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * Math.PI * 2;
    parts.push(new THREE.IcosahedronGeometry(0.07, 0).translate(Math.cos(a) * 0.12, 0.95 + (i % 2) * 0.1, Math.sin(a) * 0.12));
  }
  return mergeGeometries(parts);
}
export function plantGeometries() {
  return { bush: [bushGeo(), bushAccent()], grass: [grassGeo(), grassAccent()], stalk: [stalkGeo(), stalkAccent()] };
}

// ---------- how one plant looks at a given stage ----------
// c: {id, meta:{height, kind}, flower, mature, sow}; pl: {v, order}; stage: 0..6 (twin.STAGES);
// g: growth 0..1; h: health 0..1; hp: harvest progress; bloom: 0..1 intro scale.
const ease = (x) => 1 - Math.pow(1 - Math.min(1, Math.max(0, x)), 3);
const tmp = new THREE.Color();
const out = { sy: 0, sxz: 0, accS: 0, col: COL.leaf, accCol: null, harvested: false, sown: false };
export function plantLook(c, pl, stage, g, h, hp, day, weather, bloom) {
  let sy = 0, sxz = 0, accS = 0;
  let col = COL.leaf, accCol = c.flower;
  const H = c.meta.height;
  const sown = day >= c.sow;
  const harvested = stage === 6 || (stage === 5 && pl.order < hp);
  if (!sown) {
    sy = sxz = 0;
  } else if (harvested) {
    sy = 0.12 * H; sxz = 0.55; col = COL.stubble;
  } else {
    const gg = Math.max(0.02, g);
    sy = H * pl.v * (0.05 + 0.95 * ease(gg * 1.12)) * bloom;
    sxz = (0.35 + 0.65 * ease(gg * 1.4)) * pl.v * bloom;
    if (stage === 1) col = COL.sprout;
    else if (stage === 2) col = tmp.copy(COL.sprout).lerp(COL.deep, Math.min(1, (gg - 0.1) / 0.35));
    else if (stage === 3) { col = COL.deep; accS = Math.min(1, (gg - 0.45) / 0.08); }
    else if (stage === 4) { col = tmp.copy(COL.deep).lerp(c.mature, Math.min(1, (gg - 0.7) / 0.3) * 0.85); accS = 1; accCol = new THREE.Color().copy(c.flower).lerp(c.mature, Math.min(1, (gg - 0.7) / 0.25)); }
    else if (stage === 5) { col = c.mature; accS = 1; accCol = c.meta.kind === 'bush' && c.id === 'cotton' ? C('#fbfbf5') : c.mature; }
    if (c.id === 'cotton' && stage >= 4) accCol = C('#fbfbf5');
    if (h < 0.999) col = new THREE.Color().copy(col).lerp(COL.sick, Math.min(1, (1 - h) * 1.8));
    if (weather === 'dry' && stage < 5) col = new THREE.Color().copy(col).lerp(COL.dryTint, 0.25);
  }
  out.sy = sy; out.sxz = sxz; out.accS = accS; out.col = col; out.accCol = accCol; out.harvested = harvested; out.sown = sown;
  return out;
}
