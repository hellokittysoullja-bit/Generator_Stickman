// 3D-проба: Дима знакомит родителей с котом. three.js, рендер по кадрам из Playwright.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const W = 1080, H = 1920;
const rng = (() => { let s = 7; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();

// ---------- текстуры кодом ----------
function canvasTex(w, h, draw, repeat) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...repeat); }
  return t;
}
const noiseFill = (g, w, h, base, amp, n = 4000) => {
  g.fillStyle = base; g.fillRect(0, 0, w, h);
  for (let i = 0; i < n; i++) { const v = (rng() - 0.5) * amp; g.fillStyle = `rgba(${v > 0 ? 255 : 0},${v > 0 ? 255 : 0},${v > 0 ? 255 : 0},${Math.abs(v)})`; g.fillRect(rng() * w, rng() * h, 2, 2); }
};
const wallpaperTex = canvasTex(512, 512, (g, w, h) => {
  noiseFill(g, w, h, '#b3ab83', 0.06, 9000);
  for (let x = 0; x < w; x += 64) { g.fillStyle = 'rgba(90,80,40,0.10)'; g.fillRect(x, 0, 3, h); g.fillStyle = 'rgba(255,250,220,0.08)'; g.fillRect(x + 32, 0, 10, h); }
  for (let y = 16; y < h; y += 64) for (let x = 16; x < w; x += 64) { g.fillStyle = 'rgba(120,105,60,0.18)'; g.beginPath(); g.arc(x + ((y / 64) % 2) * 32, y, 4, 0, 7); g.fill(); }
}, [3, 1.5]);
const woodTex = canvasTex(512, 512, (g, w, h) => {
  noiseFill(g, w, h, '#4b2c1c', 0.08, 6000);
  for (let i = 0; i < 70; i++) { g.strokeStyle = `rgba(20,8,2,${0.1 + rng() * 0.2})`; g.lineWidth = 1 + rng() * 2; g.beginPath(); const y = rng() * h; g.moveTo(0, y); g.bezierCurveTo(w / 3, y + rng() * 20 - 10, 2 * w / 3, y + rng() * 20 - 10, w, y + rng() * 10 - 5); g.stroke(); }
});
const floorTex = canvasTex(1024, 1024, (g, w, h) => {
  for (let i = 0; i < 8; i++) { const c = 110 + rng() * 30; g.fillStyle = `rgb(${c},${c * 0.68},${c * 0.45})`; g.fillRect(i * 128, 0, 128, h); g.fillStyle = 'rgba(30,15,5,0.6)'; g.fillRect(i * 128, 0, 3, h); }
  for (let i = 0; i < 400; i++) { g.strokeStyle = `rgba(40,20,5,${rng() * 0.15})`; g.beginPath(); const x = rng() * w; g.moveTo(x, 0); g.lineTo(x + rng() * 6 - 3, h); g.stroke(); }
}, [3, 3]);
const rugTex = canvasTex(1024, 1024, (g, w, h) => {
  g.fillStyle = '#5b2620'; g.fillRect(0, 0, w, h);
  g.strokeStyle = '#c9a46a'; g.lineWidth = 18; g.strokeRect(40, 40, w - 80, h - 80);
  g.strokeStyle = '#2b3b45'; g.lineWidth = 30; g.strokeRect(90, 90, w - 180, h - 180);
  for (let y = 180; y < h - 160; y += 110) for (let x = 180; x < w - 160; x += 110) { g.fillStyle = (x + y) % 220 ? '#a8693d' : '#d2b27a'; g.save(); g.translate(x, y); g.rotate(Math.PI / 4); g.fillRect(-22, -22, 44, 44); g.restore(); }
  noiseFill(g, 0, 0, 'rgba(0,0,0,0)', 0, 0);
});
const clothTex = canvasTex(512, 512, (g, w, h) => {
  g.fillStyle = '#8fb1a6'; g.fillRect(0, 0, w, h);
  for (let y = 0; y < h; y += 85) for (let x = 0; x < w; x += 85) {
    const cx = x + ((y / 85) % 2) * 42 + 20, cy = y + 20;
    g.fillStyle = '#f2efe4'; for (let k = 0; k < 6; k++) { g.beginPath(); g.ellipse(cx + Math.cos(k) * 11, cy + Math.sin(k) * 11, 9, 5, k, 0, 7); g.fill(); }
    g.fillStyle = '#e3b24a'; g.beginPath(); g.arc(cx, cy, 5, 0, 7); g.fill();
    g.strokeStyle = '#6b8a5c'; g.lineWidth = 2; g.beginPath(); g.moveTo(cx + 12, cy + 12); g.quadraticCurveTo(cx + 26, cy + 22, cx + 34, cy + 16); g.stroke();
  }
}, [3, 2]);
const plateArt = (hue) => canvasTex(256, 256, (g, w, h) => {
  g.fillStyle = '#f4efe2'; g.fillRect(0, 0, w, h);
  g.fillStyle = '#8a5a3c'; g.beginPath(); g.arc(128, 128, 120, 0, 7); g.fill();
  g.fillStyle = '#efe6d2'; g.beginPath(); g.arc(128, 128, 100, 0, 7); g.fill();
  g.fillStyle = `hsl(${hue},25%,70%)`; g.beginPath(); g.arc(128, 128, 70, 0, 7); g.fill();
  g.fillStyle = `hsl(${hue},30%,45%)`; g.beginPath(); g.moveTo(60, 160); g.lineTo(110, 95); g.lineTo(140, 130); g.lineTo(170, 100); g.lineTo(198, 160); g.closePath(); g.fill();
});

// ---------- материалы и формы ----------
const M = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.75, metalness: 0, ...o });
function roundedLathe(rBot, rTop, h, bevel, seg = 64) {
  const p = []; const b = bevel;
  p.push(new THREE.Vector2(0, -h / 2));
  for (let i = 0; i <= 8; i++) { const a = -Math.PI / 2 + (i / 8) * Math.PI / 2; p.push(new THREE.Vector2(rBot - b + Math.cos(a) * b, -h / 2 + b + Math.sin(a) * b)); }
  for (let i = 0; i <= 8; i++) { const a = (i / 8) * Math.PI / 2; p.push(new THREE.Vector2(rTop - b + Math.cos(a) * b, h / 2 - b + Math.sin(a) * b)); }
  p.push(new THREE.Vector2(0, h / 2));
  return new THREE.LatheGeometry(p, seg);
}
function mesh(geo, mat, x = 0, y = 0, z = 0, parent) {
  const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true;
  if (parent) parent.add(m); return m;
}
function roundBox(w, h, d, r = 0.02) {
  const s = new THREE.Shape(); const x = -w / 2, y = -h / 2;
  s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r); s.lineTo(x + w, y + h - r);
  s.quadraticCurveTo(x + w, y + h, x + w - r, y + h); s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r);
  s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y);
  const g = new THREE.ExtrudeGeometry(s, { depth: d - 2 * r, bevelEnabled: true, bevelSize: r, bevelThickness: r, bevelSegments: 4, curveSegments: 6 });
  g.translate(0, 0, -(d - 2 * r) / 2); return g;
}

// ---------- лицо: канвас на оболочке головы ----------
class Face {
  constructor(head, r, opts) {
    this.o = { iris: '#4f7fa6', brow: '#2a1d16', skinLine: '#8a5a44', glasses: false, ...opts };
    this.c = document.createElement('canvas'); this.c.width = 1024; this.c.height = 512; this.g = this.c.getContext('2d');
    this.tex = new THREE.CanvasTexture(this.c); this.tex.colorSpace = THREE.SRGBColorSpace; this.tex.anisotropy = 8;
    const geo = new THREE.CylinderGeometry(r + 0.0015, r + 0.0015, 0.2, 96, 1, true, -1.2, 2.4);
    const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ map: this.tex, transparent: true, roughness: 0.6, depthWrite: false }));
    m.position.y = 0.0; head.add(m); this.st = { round: 0, blink: 0, mouth: 0, look: [0, 0], brow: 0, eyesWide: 0, smile: 0.4 };
  }
  draw() {
    const g = this.g, s = this.st, o = this.o; g.clearRect(0, 0, 1024, 512); g.save(); g.translate(512, 300); g.scale(1.22, 1.22); g.translate(-512, -300);
    const eyeY = 250 - s.brow * 6, eyeDX = 105, ew = 60 + s.eyesWide * 6, eh = 50 + s.eyesWide * 14;
    for (const sx of [-1, 1]) {
      const cx = 512 + sx * eyeDX, open = Math.max(0.02, 1 - s.blink), e2 = eh * open;
      const lid = Math.min(0.85, (o.lid ?? 0.28) + (s.sleepy || 0) - s.eyesWide * 0.25);
      const almond = () => { g.beginPath(); g.moveTo(cx - ew, eyeY + 4); g.bezierCurveTo(cx - ew * 0.55, eyeY - e2 * 1.3, cx + ew * 0.55, eyeY - e2 * 1.3, cx + ew, eyeY - 2 * sx);
        g.bezierCurveTo(cx + ew * 0.5, eyeY + e2 * 0.95, cx - ew * 0.5, eyeY + e2 * 0.95, cx - ew, eyeY + 4); };
      const lidY = eyeY - e2 * 0.98 * (1 - 1.15 * lid), cY = 2 * lidY - eyeY;
      g.save(); almond(); g.clip();
      g.fillStyle = '#f7f4ee'; g.fillRect(cx - ew, eyeY - eh * 2, ew * 2, eh * 4);
      const ix = cx + s.look[0] * 14, iy = eyeY + s.look[1] * 8 + 4;
      g.fillStyle = o.iris; g.beginPath(); g.arc(ix, iy, 31, 0, 7); g.fill();
      g.strokeStyle = 'rgba(0,0,0,0.35)'; g.lineWidth = 3; g.stroke();
      g.fillStyle = '#121212'; g.beginPath(); g.arc(ix, iy, 15, 0, 7); g.fill();
      g.fillStyle = 'rgba(255,255,255,0.95)'; g.beginPath(); g.arc(ix - 9, iy - 10, 6, 0, 7); g.fill();
      g.fillStyle = o.skinHex || '#d8b48f'; g.beginPath(); g.moveTo(cx - ew - 6, eyeY - eh * 2); g.lineTo(cx + ew + 6, eyeY - eh * 2); g.lineTo(cx + ew + 6, eyeY - 2 * sx); g.quadraticCurveTo(cx, cY, cx - ew - 6, eyeY + 4); g.fill();
      g.fillStyle = 'rgba(60,30,20,0.18)'; g.beginPath(); g.moveTo(cx - ew, eyeY + 4); g.quadraticCurveTo(cx, cY + 14, cx + ew, eyeY); g.lineTo(cx + ew, eyeY - 6); g.quadraticCurveTo(cx, cY + 2, cx - ew, eyeY - 2); g.fill();
      g.restore();
      g.strokeStyle = '#1e1512'; g.lineCap = 'round'; g.lineWidth = 10; g.beginPath(); g.moveTo(cx - ew - 4, eyeY + 5); g.quadraticCurveTo(cx, cY, cx + ew + 6, eyeY - 3 * sx); g.stroke();
      g.strokeStyle = 'rgba(70,40,30,0.35)'; g.lineWidth = 4; g.beginPath(); g.moveTo(cx - ew * 0.7, eyeY + e2 * 0.75); g.quadraticCurveTo(cx, eyeY + e2 * 0.95, cx + ew * 0.7, eyeY + e2 * 0.72); g.stroke();
      if (o.lashes) { g.strokeStyle = '#1e1512'; g.lineWidth = 6; const ox = cx + sx * (ew + 4), oy = eyeY - 4;
        for (const [dx, dy] of [[16, -14], [22, -2], [12, -24]]) { g.beginPath(); g.moveTo(ox - sx * 6, oy - 6 + dy * 0.2); g.quadraticCurveTo(ox + sx * dx * 0.5, oy + dy * 0.6, ox + sx * dx, oy + dy); g.stroke(); } }
      g.strokeStyle = o.brow; g.lineWidth = o.browW || 11;
      g.beginPath(); const by = eyeY - eh - 30 - s.brow * 22 - s.eyesWide * 12 + (s.frown || 0) * 14;
      g.moveTo(cx - sx * 50, by + 8 + sx * (s.frown || 0) * 10 * -sx); g.quadraticCurveTo(cx, by - 10, cx + sx * 50, by + 8 - (s.frown || 0) * 6); g.stroke();
    }
    if (o.mustache) { g.fillStyle = '#3a2c22'; for (let k = 0; k < 7; k++) g.fillRect(476 + k * 11, 345 + Math.abs(k - 3) * 2, 5, 17); }
    // нос
    g.strokeStyle = 'rgba(140,90,70,0.55)'; g.lineWidth = 6; g.beginPath(); g.moveTo(505, 300); g.quadraticCurveTo(520, 325, 500, 333); g.stroke();
    // рот
    const my = 382, mw = 58 + s.smile * 10, mo = s.mouth * 52;
    if (s.round > 0.05) { g.fillStyle = '#4a1a18'; g.beginPath(); g.ellipse(512, my + 14, 26 + s.round * 8, 20 + s.round * 30, 0, 0, 7); g.fill(); g.fillStyle = '#b8454c'; g.beginPath(); g.ellipse(512, my + 30 + s.round * 14, 18, 10, 0, 0, 7); g.fill(); }
    else if (mo > 3) {
      g.fillStyle = '#5a1f1c'; g.beginPath(); g.moveTo(512 - mw, my - s.smile * 6);
      g.quadraticCurveTo(512, my + 8 - s.smile * 2, 512 + mw, my - s.smile * 6);
      g.quadraticCurveTo(512 + mw * 0.6, my + mo * 1.2, 512, my + mo * 1.25);
      g.quadraticCurveTo(512 - mw * 0.6, my + mo * 1.2, 512 - mw, my - s.smile * 6); g.fill();
      g.fillStyle = '#f2ece2'; g.beginPath(); g.ellipse(512, my + 3, mw * 0.62, Math.min(9, mo * 0.25), 0, 0, Math.PI); g.fill();
      g.fillStyle = '#c4545a'; g.beginPath(); g.ellipse(512, my + mo * 1.05, mw * 0.45, mo * 0.25, 0, 0, 7); g.fill();
    } else {
      g.strokeStyle = '#4a2420'; g.lineWidth = 8; g.beginPath(); g.moveTo(512 - mw, my - s.smile * 12); g.quadraticCurveTo(512, my + s.smile * 22 - 4, 512 + mw, my - s.smile * 12); g.stroke();
    }
    // румянец
    g.fillStyle = 'rgba(214,110,100,0.16)'; for (const sx of [-1, 1]) { g.beginPath(); g.ellipse(512 + sx * 170, 330, 45, 26, 0, 0, 7); g.fill(); }
    g.restore(); this.tex.needsUpdate = true;
  }
}

// ---------- персонаж ----------
function makePerson(o) {
  const root = new THREE.Group();
  const skin = M(o.skin || '#d8b48f', { roughness: 0.55 });
  const cloth = M(o.cloth, { roughness: 0.9 });
  const pants = M(o.pants || '#2c3a55', { roughness: 0.9 });
  const legH = o.seated ? 0.0 : 0.78;
  if (!o.seated) { mesh(roundedLathe(0.07, 0.07, legH, 0.03), pants, -0.09, legH / 2, 0, root); mesh(roundedLathe(0.07, 0.07, legH, 0.03), pants, 0.09, legH / 2, 0, root);
    for (const sx of [-1, 1]) { const sh = mesh(roundBox(0.12, 0.07, 0.22, 0.03), M('#222'), sx * 0.09, 0.035, 0.04, root); } }
  const torso = new THREE.Group(); torso.position.y = legH + (o.seated ? 0.45 : 0.02); root.add(torso);
  const tH = 0.52; mesh(roundedLathe(0.2, 0.17, tH, 0.07), cloth, 0, tH / 2, 0, torso).scale.set(1, 1, 0.78);
  if (o.necklace) for (let i = 0; i < 13; i++) { const a = -1.0 + i / 12 * 2.0; mesh(new THREE.SphereGeometry(0.012, 12, 8), M('#e8e0c8', { roughness: 0.3 }), Math.sin(a) * 0.11, tH - 0.06 - Math.cos(a) * 0.05, Math.cos(a) * 0.12 + 0.02, torso); }
  if (o.collar) { mesh(roundBox(0.18, 0.05, 0.12, 0.02), M(o.collar), 0, tH - 0.01, 0.03, torso); }
  const neck = mesh(new THREE.CylinderGeometry(0.06, 0.065, 0.06, 24), skin, 0, tH + 0.01, 0, torso);
  const headPivot = new THREE.Group(); headPivot.position.y = tH + 0.025; torso.add(headPivot);
  const r = 0.155, hh = 0.36;
  const head = mesh(roundedLathe(r * 0.97, r, hh, 0.06), skin, 0, hh / 2, 0, headPivot); head.scale.z = 0.94;
  // уши
  for (const sx of [-1, 1]) { const e = mesh(new THREE.SphereGeometry(0.035, 16, 12), skin, sx * r * 0.98, hh * 0.47, 0, headPivot); e.scale.set(0.5, 1, 0.8); }
  const faceHolder = new THREE.Group(); faceHolder.position.y = hh * 0.52; headPivot.add(faceHolder); faceHolder.scale.z = 0.94;
  const face = new Face(faceHolder, r, { skinHex: o.skin || '#d8b48f', ...(o.face || {}) });
  // волосы
  const hairM = M(o.hair || '#2b1d16', { roughness: 0.85 });
  if (o.curly) {
    for (let i = 0; i < 70; i++) { const a = rng() * Math.PI * 2, y = hh * (0.7 + rng() * 0.45); const back = Math.cos(a) < 0.25 || y > hh * 0.95;
      if (!back) continue; const rr = r + 0.03 + rng() * 0.02; mesh(new THREE.IcosahedronGeometry(0.05 + rng() * 0.02, 2), hairM, Math.sin(a) * rr, y, Math.cos(a) * rr * 0.95, headPivot); }
    for (let i = 0; i < 14; i++) { const x = (i / 13 - 0.5) * 0.3; mesh(new THREE.IcosahedronGeometry(0.045, 2), hairM, x, hh + 0.02 - Math.abs(x) * 0.4, 0.09 - Math.abs(x) * 0.3, headPivot); }
    for (let i = 0; i < 22; i++) { const sx = i % 2 ? 1 : -1; mesh(new THREE.IcosahedronGeometry(0.045 + rng() * 0.015, 2), hairM, sx * (r + 0.02 + rng() * 0.03), hh * (0.3 + rng() * 0.6), -0.02 - rng() * 0.12, headPivot); }
  } else if (o.flatHair) {
    const h = mesh(roundedLathe(r * 1.07, r * 1.07, 0.15, 0.06), hairM, 0, hh - 0.045, -0.006, headPivot); h.scale.z = 0.97;
    const bk = mesh(roundedLathe(r * 1.07, r * 1.07, 0.2, 0.05, 48), hairM, 0, hh * 0.58, -0.02, headPivot); bk.scale.set(1, 1, 0.95);
    const cut = mesh(new THREE.BoxGeometry(r * 2.4, 0.22, r * 1.3), hairM, 0, 0, 0, headPivot); cut.visible = false;
  } else {
    const cap = new THREE.SphereGeometry(r * 1.06, 64, 32, 0, Math.PI * 2, 0, Math.PI * 0.5);
    const h = mesh(cap, hairM, 0, hh * 0.78, -0.012, headPivot); h.scale.set(1.0, 0.75, 1.02);
    for (let i = 0; i < 90; i++) { const a = rng() * Math.PI * 2, el = rng() * 1.2; const front = Math.cos(a) > 0.55;
      const y = hh * (front ? 0.93 + el * 0.06 : 0.62 + el * 0.32); const rr = (r + 0.008) * (front ? 0.92 : 1.0) * (0.9 + 0.1 * Math.cos(el));
      const b2 = mesh(new THREE.IcosahedronGeometry(0.03 + rng() * 0.012, 2), hairM, Math.sin(a) * rr, y + (front ? 0.0 : 0), Math.cos(a) * rr * 0.95, headPivot); b2.scale.set(1.2, 0.8, 1.0); }
    for (let i = 0; i < 9; i++) { const x = (i / 8 - 0.5) * 0.25; mesh(new THREE.IcosahedronGeometry(0.035, 2), hairM, x, hh * 0.95 - Math.abs(x) * 0.2 - (i % 2) * 0.012, r * 0.82, headPivot).scale.set(1.3, 0.7, 0.9); }
  }
  if (o.earrings) for (const sx of [-1, 1]) { mesh(new THREE.SphereGeometry(0.011, 16, 12), M('#e3c46e', { metalness: 0.9, roughness: 0.2 }), sx * r * 1.0, hh * 0.36, 0.0, headPivot); mesh(new THREE.SphereGeometry(0.016, 16, 12), M('#9fd6c9', { roughness: 0.15 }), sx * r * 1.0, hh * 0.3, 0.0, headPivot); }
  if (o.tie) { mesh(roundBox(0.05, 0.3, 0.014, 0.006), M('#141414', { roughness: 0.5 }), 0, tH - 0.19, 0.152, torso).rotation.x = -0.08; mesh(new THREE.BoxGeometry(0.06, 0.008, 0.01), M('#c9c9c9', { metalness: 0.9, roughness: 0.2 }), 0, tH - 0.2, 0.162, torso);
    mesh(roundBox(0.06, 0.05, 0.03, 0.01), M('#141414'), 0, tH - 0.03, 0.135, torso); }
  if (o.glasses) {
    const gm = M('#111', { roughness: 0.35 });
    for (const sx of [-1, 1]) {
      const s = new THREE.Shape(); const w = 0.085, h2 = 0.06, rr = 0.016; const x = -w / 2, y = -h2 / 2;
      s.moveTo(x + rr, y); s.lineTo(x + w - rr, y); s.quadraticCurveTo(x + w, y, x + w, y + rr); s.lineTo(x + w, y + h2 - rr); s.quadraticCurveTo(x + w, y + h2, x + w - rr, y + h2); s.lineTo(x + rr, y + h2); s.quadraticCurveTo(x, y + h2, x, y + h2 - rr); s.lineTo(x, y + rr); s.quadraticCurveTo(x, y, x + rr, y);
      const hole = new THREE.Path(); const iw = w - 0.022, ih = h2 - 0.022, ix = -iw / 2, iy = -ih / 2; hole.moveTo(ix, iy); hole.lineTo(ix + iw, iy); hole.lineTo(ix + iw, iy + ih); hole.lineTo(ix, iy + ih); hole.lineTo(ix, iy); s.holes.push(hole);
      const g = new THREE.ExtrudeGeometry(s, { depth: 0.012, bevelEnabled: true, bevelSize: 0.003, bevelThickness: 0.003, bevelSegments: 2 });
      const m = mesh(g, gm, sx * 0.052, hh * 0.52 + 0.005, r * 0.92, headPivot); m.rotation.y = sx * 0.28;
    }
    mesh(new THREE.BoxGeometry(0.03, 0.01, 0.01), gm, 0, hh * 0.52 + 0.012, r * 0.99, headPivot);
  }
  // руки — гибкие трубки, обновляются каждый кадр
  const arms = [];
  for (const sx of [-1, 1]) {
    const shoulder = new THREE.Vector3(sx * 0.19, tH - 0.07, 0);
    const tube = new THREE.Mesh(new THREE.BufferGeometry(), cloth); tube.castShadow = tube.receiveShadow = true; torso.add(tube);
    const hand = new THREE.Group(); torso.add(hand);
    mesh(new THREE.SphereGeometry(0.042, 24, 16), skin, 0, 0.03, 0, hand).scale.set(1.0, 1.1, 0.6);
    const fing = mesh(new THREE.CapsuleGeometry(0.028, 0.035, 8, 16), skin, 0, 0.08, 0.004, hand); fing.scale.set(1.35, 1, 0.7); fing.rotation.x = 0.3;
    const th = mesh(new THREE.CapsuleGeometry(0.013, 0.028, 6, 12), skin, -sx * 0.038, 0.045, 0.012, hand); th.rotation.z = sx * 0.7; th.rotation.x = -0.3;
    if (o.watch && sx < 0) { const wt = mesh(new THREE.TorusGeometry(0.036, 0.008, 10, 24), M('#1a1a1a', { roughness: 0.4 }), 0, -0.005, 0, hand); wt.rotation.x = Math.PI / 2; mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.006, 20), M('#d9c27a', { metalness: 0.8, roughness: 0.25 }), 0, -0.005, 0.04, hand).rotation.x = Math.PI / 2; }
    if (o.ring && sx > 0) mesh(new THREE.TorusGeometry(0.02, 0.004, 8, 20), M('#e2c26a', { metalness: 0.9, roughness: 0.2 }), 0, 0.075, 0, hand).rotation.x = Math.PI / 2;
    const cuff = mesh(new THREE.TorusGeometry(0.038, 0.012, 10, 24), cloth, 0, 0, 0, torso);
    arms.push({ sx, shoulder, tube, hand, cuff, elbow: new THREE.Vector3(sx * 0.27, tH - 0.3, 0.05), wrist: new THREE.Vector3(sx * 0.24, tH - 0.5, 0.1) });
  }
  const setArms = () => { for (const a of arms) {
    const c = new THREE.CatmullRomCurve3([a.shoulder, a.shoulder.clone().lerp(a.elbow, 0.5).add(new THREE.Vector3(a.sx * 0.02, 0, 0)), a.elbow, a.wrist]);
    a.tube.geometry.dispose(); a.tube.geometry = new THREE.TubeGeometry(c, 40, 0.042, 14, false);
    const tg = c.getTangent(1); a.hand.position.copy(a.wrist).addScaledVector(tg, 0.012); a.hand.lookAt(a.hand.position.clone().add(tg)); a.hand.rotateX(Math.PI / 2);
    a.cuff.position.copy(a.wrist); a.cuff.lookAt(a.wrist.clone().add(tg));
  } };
  return { root, torso, headPivot, face, arms, setArms, tH };
}

// ---------- кот ----------
function makeCat() {
  const g = new THREE.Group(); const fur = M('#141215', { roughness: 0.9 });
  const body = mesh(new THREE.SphereGeometry(0.12, 40, 28), fur, 0, 0.1, 0, g); body.scale.set(1, 0.95, 1.25);
  const headPivot = new THREE.Group(); headPivot.position.set(0, 0.22, 0.08); g.add(headPivot);
  const head = mesh(new THREE.SphereGeometry(0.105, 48, 32), fur, 0, 0, 0, headPivot); head.scale.set(1.12, 0.95, 0.95);
  const earL = mesh(new THREE.ConeGeometry(0.045, 0.08, 24), fur, -0.07, 0.1, -0.005, headPivot); earL.rotation.z = 0.35;
  const earR = mesh(new THREE.ConeGeometry(0.045, 0.08, 24), fur, 0.07, 0.085, -0.005, headPivot); earR.rotation.set(0.5, 0, -0.9); // загнутое ухо
  for (const [e, sx] of [[earL, -1], [earR, 1]]) { const inn = mesh(new THREE.ConeGeometry(0.028, 0.05, 16), M('#c98b8b'), 0, -0.008, 0.012, e); }
  const eyes = [];
  for (const sx of [-1, 1]) {
    const ew = mesh(new THREE.SphereGeometry(0.03, 32, 20), M('#6fbf3f', { roughness: 0.2, emissive: '#1e4010' }), sx * 0.042, 0.012, 0.085, headPivot); ew.scale.set(1, 1.1, 0.45);
    const p = mesh(new THREE.SphereGeometry(0.02, 20, 14), M('#050505', { roughness: 0.1 }), 0, 0, 0.022, ew); p.scale.set(0.7, 1.4, 0.5);
    const hl = mesh(new THREE.SphereGeometry(0.006, 12, 8), new THREE.MeshBasicMaterial({ color: '#ffffff' }), -0.009, 0.011, 0.028, ew);
    const lid = mesh(new THREE.SphereGeometry(0.032, 32, 20, 0, Math.PI * 2, 0, Math.PI / 2), fur, 0, 0, 0, ew); lid.scale.set(1.05, 1, 1.4); lid.rotation.x = -1.4;
    const refl = new THREE.Mesh(new THREE.PlaneGeometry(0.009, 0.0055), new THREE.MeshBasicMaterial({ color: '#9fd4ff', transparent: true, opacity: 0.45, toneMapped: false })); refl.position.set(0.009, -0.006, 0.037); refl.rotation.z = 0.15; refl.visible = false; ew.add(refl);
    eyes.push({ ew, lid, p, hl, refl });
  }
  mesh(new THREE.SphereGeometry(0.011, 16, 10), M('#c47a80'), 0, -0.022, 0.104, headPivot).scale.set(1.3, 0.8, 0.7);
  for (const sx of [-1, 1]) for (let k = 0; k < 2; k++) { const w = mesh(new THREE.CylinderGeometry(0.0015, 0.0015, 0.11, 6), M('#d8d2c8'), sx * 0.085, -0.025 - k * 0.012, 0.075, headPivot); w.rotation.z = Math.PI / 2 + sx * (0.08 + k * 0.12); }
  // хвост с огоньком
  const tail = new THREE.Mesh(new THREE.BufferGeometry(), fur); tail.castShadow = true; g.add(tail);
  const flameM = new THREE.MeshBasicMaterial({ color: '#ffb23a', transparent: true, opacity: 0.95 });
  const flame = new THREE.Mesh(new THREE.ConeGeometry(0.03, 0.09, 24, 1, true), flameM); g.add(flame);
  const core = new THREE.Mesh(new THREE.ConeGeometry(0.016, 0.05, 16), new THREE.MeshBasicMaterial({ color: '#fff3b0' })); flame.add(core); core.position.y = -0.012;
  const flameLight = new THREE.PointLight('#ff9a3c', 0.6, 0.8, 2); flame.add(flameLight);
  const setTail = (t) => {
    const pts = []; for (let i = 0; i <= 6; i++) { const u = i / 6; pts.push(new THREE.Vector3(0.1 + u * 0.16 + Math.sin(t * 2.2 + u * 3) * 0.03 * u, 0.06 + u * 0.22 + Math.sin(u * 3.0) * 0.05, -0.1 - u * 0.05 + Math.cos(t * 1.7 + u * 2) * 0.03 * u)); }
    const c = new THREE.CatmullRomCurve3(pts); tail.geometry.dispose(); tail.geometry = new THREE.TubeGeometry(c, 40, 0.022, 12, false);
    const end = c.getPoint(1); flame.position.copy(end).add(new THREE.Vector3(0, 0.045, 0));
    flame.scale.set(1 + Math.sin(t * 23) * 0.08, 1 + Math.sin(t * 17 + 1) * 0.15, 1); flame.rotation.z = Math.sin(t * 9) * 0.15; flameLight.intensity = 0.5 + Math.sin(t * 21) * 0.15;
  };
  const paw = new THREE.Mesh(new THREE.BufferGeometry(), fur); paw.castShadow = true; g.add(paw);
  const pawBall = mesh(new THREE.SphereGeometry(0.026, 20, 14), fur, 0, 0, 0, g); pawBall.scale.set(1, 0.8, 1.15);
  for (const sx of [-1, 1]) { const fl = mesh(new THREE.SphereGeometry(0.03, 20, 14), fur, sx * 0.055, 0.02, 0.1, g); fl.scale.set(0.9, 0.7, 1.3); }
  const setPaw = (target) => { // target — точка в координатах кота или null (лапа поджата)
    const a = new THREE.Vector3(0.05, 0.14, 0.09); const b = target || new THREE.Vector3(0.05, 0.03, 0.13);
    const m = a.clone().lerp(b, 0.5).add(new THREE.Vector3(0, 0.04, 0.02));
    const c = new THREE.CatmullRomCurve3([a, m, b]); paw.geometry.dispose(); paw.geometry = new THREE.TubeGeometry(c, 20, 0.024, 10, false); pawBall.position.copy(b); };
  setPaw(null);
  return { g, headPivot, eyes, earR, setTail, setPaw };
}

// ---------- сцена ----------
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H); renderer.setPixelRatio(1);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene(); scene.background = new THREE.Color('#2a2420');
const camera = new THREE.PerspectiveCamera(32, W / H, 0.05, 40);

const RW = 5.2, RD = 5.6, RH = 2.8;
const wallM = new THREE.MeshStandardMaterial({ map: wallpaperTex, roughness: 0.95 });
const wainM = new THREE.MeshStandardMaterial({ map: woodTex, roughness: 0.6, color: '#8a6a58' });
const woodM = new THREE.MeshStandardMaterial({ map: woodTex, roughness: 0.5, color: '#b08a78' });
const floor = mesh(new THREE.PlaneGeometry(RW, RD), new THREE.MeshStandardMaterial({ map: floorTex, roughness: 0.55 }), 0, 0, 0, scene); floor.rotation.x = -Math.PI / 2;
const rug = mesh(new THREE.PlaneGeometry(2.8, 2.2), new THREE.MeshStandardMaterial({ map: rugTex, roughness: 1 }), 0, 0.005, 0, scene); rug.rotation.x = -Math.PI / 2;
const ceil = mesh(new THREE.PlaneGeometry(RW, RD), M('#e8e2d2', { roughness: 1 }), 0, RH, 0, scene); ceil.rotation.x = Math.PI / 2;
function wall(w, x, z, ry) {
  const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = ry; scene.add(g);
  mesh(new THREE.PlaneGeometry(w, RH - 0.9), wallM, 0, 0.9 + (RH - 0.9) / 2, 0, g).castShadow = false;
  mesh(new THREE.BoxGeometry(w, 0.9, 0.04), wainM, 0, 0.45, 0.02, g);
  mesh(new THREE.BoxGeometry(w, 0.05, 0.07), woodM, 0, 0.92, 0.035, g);
  for (let x2 = -w / 2 + 0.35; x2 < w / 2 - 0.2; x2 += 0.62) mesh(new THREE.BoxGeometry(0.48, 0.55, 0.012), wainM, x2 + 0.24, 0.47, 0.045, g);
  mesh(new THREE.BoxGeometry(w, 0.1, 0.03), M('#efe8d8'), 0, RH - 0.05, 0.015, g);
  return g;
}
const back = wall(RW, 0, -RD / 2, 0);
const front = wall(RW, 0, RD / 2, Math.PI);
const left = wall(RD, -RW / 2, 0, Math.PI / 2);
const right = wall(RD, RW / 2, 0, -Math.PI / 2);
const plateGeo = new THREE.CylinderGeometry(0.12, 0.11, 0.015, 48);
function wallPlates(g, cx, cy, cols, rows, step = 0.3) {
  for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) {
    const m = new THREE.Mesh(plateGeo, [M('#efe7d6', { roughness: 0.3 }), new THREE.MeshStandardMaterial({ map: plateArt(20 + rng() * 180), roughness: 0.3 }), M('#efe7d6')]);
    m.rotation.x = Math.PI / 2; m.position.set(cx + (i - (cols - 1) / 2) * step, cy + (j - (rows - 1) / 2) * step * 0.9, 0.02); m.castShadow = true; g.add(m);
  }
}
// задняя стена: сервант + тарелки по бокам
const sb = new THREE.Group(); sb.position.set(0, 0, -RD / 2 + 0.26); scene.add(sb);
mesh(new THREE.BoxGeometry(1.7, 2.1, 0.46), woodM, 0, 1.05, 0, sb);
const glassM = new THREE.MeshPhysicalMaterial({ color: '#dfe8e4', roughness: 0.05, transmission: 0.0, transparent: true, opacity: 0.18 });
for (const sx of [-1, 1]) {
  const fr = new THREE.Group(); fr.position.set(sx * 0.42, 1.45, 0.235); sb.add(fr);
  mesh(new THREE.BoxGeometry(0.8, 1.15, 0.01), M('#2b1a12'), 0, 0, -0.2, fr);
  for (const [w, h, x, y] of [[0.8, 0.05, 0, 0.55], [0.8, 0.05, 0, -0.55], [0.05, 1.15, -0.38, 0], [0.05, 1.15, 0.38, 0], [0.04, 1.15, 0, 0], [0.8, 0.03, 0, 0]]) mesh(new THREE.BoxGeometry(w, h, 0.03), woodM, x, y, 0, fr);
  mesh(new THREE.PlaneGeometry(0.74, 1.08), glassM, 0, 0, 0.005, fr);
  for (const sh of [-0.28, 0.27]) { mesh(new THREE.BoxGeometry(0.76, 0.02, 0.36), woodM, 0, sh - 0.18, -0.18, fr);
    for (let k = 0; k < 3; k++) { const p = mesh(new THREE.CylinderGeometry(0.085, 0.08, 0.012, 40), M('#f1ece2', { roughness: 0.25 }), -0.22 + k * 0.22, sh - 0.08, -0.3, fr); p.rotation.x = Math.PI / 2 - 0.15; }
    const bt = mesh(new THREE.CylinderGeometry(0.025, 0.035, 0.22, 24), new THREE.MeshPhysicalMaterial({ color: '#cfd8cf', roughness: 0.1, transparent: true, opacity: 0.6 }), 0.3, sh - 0.06, -0.2, fr); }
}
for (let k = 0; k < 2; k++) { const d = mesh(new THREE.BoxGeometry(0.78, 0.6, 0.02), woodM, (k - 0.5) * 0.82, 0.45, 0.24, sb); mesh(new THREE.SphereGeometry(0.018, 12, 8), M('#c9a24a', { metalness: 0.8, roughness: 0.3 }), (k - 0.5) * 0.82 + (k ? -0.3 : 0.3), 0.55, 0.26, sb); }
wallPlates(back, -1.75, 1.85, 2, 4);
// передняя стена (за Димой): дверь, бра, тарелки
const door = new THREE.Group(); door.position.set(-0.9, 0, 0.02); front.add(door);
for (const [w, h, x, y] of [[0.1, 2.15, -0.5, 1.075], [0.1, 2.15, 0.5, 1.075], [1.1, 0.1, 0, 2.15]]) mesh(new THREE.BoxGeometry(w, h, 0.06), M('#efe9dc', { roughness: 0.6 }), x, y, 0.03, door);
mesh(new THREE.BoxGeometry(0.9, 2.1, 0.01), M('#6f6a62'), 0, 1.05, -0.01, door);
const lampG = new THREE.Group(); lampG.position.set(0.25, 1.75, 0.05); front.add(lampG);
mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.08, 16), M('#3a2a1c', { metalness: 0.6, roughness: 0.4 }), 0, 0, 0, lampG);
mesh(new THREE.SphereGeometry(0.09, 32, 20, 0, Math.PI * 2, 0, Math.PI * 0.75), new THREE.MeshStandardMaterial({ color: '#fff2d6', emissive: '#ffd89a', emissiveIntensity: 1.6 }), 0, 0.12, 0.07, lampG);
const sconce = new THREE.PointLight('#ffcf8a', 2.2, 4, 2); sconce.position.set(0.25, 1.9, RD / 2 - 0.25); scene.add(sconce);
const hooks = new THREE.Group(); hooks.position.set(0.95, 1.45, 0.03); front.add(hooks); mesh(new THREE.BoxGeometry(0.6, 0.06, 0.03), woodM, 0, 0, 0, hooks);
for (let k = 0; k < 3; k++) mesh(new THREE.TorusGeometry(0.025, 0.007, 8, 16, Math.PI), M('#222', { metalness: 0.7 }), -0.2 + k * 0.2, -0.03, 0.03, hooks).rotation.z = Math.PI;
wallPlates(front, 0.95, 2.15, 3, 2, 0.28); wallPlates(front, 1.9, 1.5, 2, 4);
// окно слева
const win = new THREE.Group(); win.position.set(0.4, 1.55, 0.02); left.add(win);
mesh(new THREE.PlaneGeometry(1.2, 1.1), new THREE.MeshBasicMaterial({ color: '#f6f1e2' }), 0, 0, 0.005, win);
for (const [w, h, x, y] of [[1.3, 0.07, 0, 0.58], [1.3, 0.1, 0, -0.58], [0.07, 1.2, -0.62, 0], [0.07, 1.2, 0.62, 0], [0.04, 1.1, 0, 0], [1.2, 0.04, 0, 0.1]]) mesh(new THREE.BoxGeometry(w, h, 0.06), M('#efe9dc'), x, y, 0.03, win);
// люстра
const ch = new THREE.Group(); ch.position.set(0, RH - 0.02, 0); scene.add(ch);
mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.35, 8), M('#4a3a22', { metalness: 0.6 }), 0, -0.17, 0, ch);
mesh(new THREE.SphereGeometry(0.16, 32, 16, 0, Math.PI * 2, Math.PI * 0.45, Math.PI * 0.55), new THREE.MeshStandardMaterial({ color: '#fff6e6', emissive: '#ffe2b0', emissiveIntensity: 1.2, side: THREE.DoubleSide }), 0, -0.3, 0, ch);
// стол
const table = new THREE.Group(); scene.add(table);
mesh(new THREE.BoxGeometry(1.9, 0.05, 1.0), woodM, 0, 0.74, 0, table);
for (const [x, z] of [[-0.85, -0.42], [0.85, -0.42], [-0.85, 0.42], [0.85, 0.42]]) mesh(new THREE.CylinderGeometry(0.035, 0.03, 0.72, 16), woodM, x, 0.36, z, table);
const clothM = new THREE.MeshStandardMaterial({ map: clothTex, roughness: 0.95 });
mesh(roundBox(2.06, 0.012, 1.16, 0.005), clothM, 0, 0.77, 0, table);
for (const [w, d, x, z, ry] of [[2.06, 0.006, 0, 0.58, 0], [2.06, 0.006, 0, -0.58, 0], [1.16, 0.006, 1.03, 0, Math.PI / 2], [1.16, 0.006, -1.03, 0, Math.PI / 2]]) { const s = mesh(new THREE.BoxGeometry(w, 0.24, d), clothM, x, 0.655, z, table); s.rotation.y = ry; }
const plateM = M('#f6f2ea', { roughness: 0.2 });
const lp = (r) => new THREE.LatheGeometry([new THREE.Vector2(0, 0), new THREE.Vector2(r * 0.6, 0), new THREE.Vector2(r * 0.65, 0.008), new THREE.Vector2(r, 0.02), new THREE.Vector2(r * 0.98, 0.024), new THREE.Vector2(r * 0.62, 0.012), new THREE.Vector2(0, 0.012)], 48);
for (const [x, z] of [[-0.55, 0.3], [0.55, 0.3], [-0.55, -0.3], [0.55, -0.3], [0, -0.32]]) mesh(lp(0.13), plateM, x, 0.777, z, table);
// салат и закуски
const bowl = mesh(new THREE.LatheGeometry([new THREE.Vector2(0, 0), new THREE.Vector2(0.08, 0), new THREE.Vector2(0.17, 0.07), new THREE.Vector2(0.18, 0.08), new THREE.Vector2(0.16, 0.075), new THREE.Vector2(0.07, 0.01)], 48), plateM, -0.1, 0.777, 0.02, table);
for (let i = 0; i < 90; i++) { const a = rng() * 7, rr = Math.sqrt(rng()) * 0.14; const col = ['#e7d38a', '#8fae5a', '#d9a24a', '#f0e6c0', '#c2533e'][i % 5]; mesh(new THREE.BoxGeometry(0.022, 0.022, 0.022), M(col, { roughness: 0.5 }), -0.1 + Math.cos(a) * rr, 0.84 + rng() * 0.02, 0.02 + Math.sin(a) * rr, table).rotation.set(rng() * 3, rng() * 3, 0); }
const tom = mesh(lp(0.15), plateM, 0.35, 0.777, 0.0, table);
for (let i = 0; i < 9; i++) { const a = i / 9 * 7; const t = mesh(new THREE.SphereGeometry(0.035, 20, 14), M('#c8352b', { roughness: 0.35 }), 0.35 + Math.cos(a) * 0.08, 0.81, Math.sin(a) * 0.08, table); t.scale.y = 0.6; mesh(new THREE.SphereGeometry(0.012, 10, 8), M('#4d7a35'), 0, 0.03, 0, t); }
for (const [x, z] of [[-0.3, -0.25], [0.3, -0.22], [0.75, 0.05]]) { const cup = mesh(new THREE.CylinderGeometry(0.04, 0.032, 0.07, 32, 1, true), M('#f6f2ea', { roughness: 0.25, side: THREE.DoubleSide }), x, 0.815, z, table); mesh(new THREE.CircleGeometry(0.038, 24), M('#6b3a1a', { roughness: 0.1 }), 0, 0.025, 0, cup).rotation.x = -Math.PI / 2; mesh(new THREE.TorusGeometry(0.022, 0.006, 8, 16), M('#f6f2ea'), 0.045, 0, 0, cup); }
const bottle = mesh(new THREE.LatheGeometry([new THREE.Vector2(0, 0), new THREE.Vector2(0.04, 0), new THREE.Vector2(0.042, 0.18), new THREE.Vector2(0.03, 0.23), new THREE.Vector2(0.014, 0.27), new THREE.Vector2(0.014, 0.31), new THREE.Vector2(0, 0.31)], 32), new THREE.MeshPhysicalMaterial({ color: '#2f5a32', roughness: 0.08, clearcoat: 1 }), -0.75, 0.777, -0.05, table);
// стулья
function chair(x, z, ry) { const c = new THREE.Group(); c.position.set(x, 0, z); c.rotation.y = ry; scene.add(c);
  mesh(new THREE.BoxGeometry(0.46, 0.05, 0.44), woodM, 0, 0.46, 0, c); for (const [a, b] of [[-0.2, -0.19], [0.2, -0.19], [-0.2, 0.19], [0.2, 0.19]]) mesh(new THREE.BoxGeometry(0.04, 0.46, 0.04), woodM, a, 0.23, b, c);
  mesh(new THREE.BoxGeometry(0.46, 0.5, 0.04), woodM, 0, 0.75, -0.2, c); return c; }
chair(0.4, -0.8, 0); chair(-0.45, -0.8, 0); chair(0, 0.82, Math.PI);

// ---------- люди ----------
const dad = makePerson({ cloth: '#d99cbc', seated: true, flatHair: true, hair: '#6b7562', tie: true, collar: '#e8afc9', ring: true, skin: '#d9b08c',
  face: { iris: '#6a8a6a', brow: '#2a2420', mustache: true, lid: 0.3, browW: 13 } });
dad.root.position.set(0.4, 0, -0.78); scene.add(dad.root);
const mom = makePerson({ cloth: '#1f1c1e', seated: true, curly: true, glasses: true, earrings: true, watch: true, hair: '#1b1615', skin: '#dcb592',
  face: { iris: '#6b8aa6', brow: '#151010', lashes: true, lid: 0.22 } });
mom.root.position.set(-0.45, 0, -0.78); scene.add(mom.root);
const dima = makePerson({ cloth: '#c79a3b', seated: true, hair: '#3a2618', face: { iris: '#5a7a4a', lid: 0.24 } });
dima.root.position.set(0, 0, 0.8); dima.root.rotation.y = Math.PI; scene.add(dima.root);
const PEOPLE = { dad, mom, dima };
for (const p of Object.values(PEOPLE)) p.baseY = p.torso.position.y;
const rest = (p) => { p.arms[0].elbow.set(-0.27, 0.13, 0.14); p.arms[0].wrist.set(-0.15, 0.32, 0.33); p.arms[1].elbow.set(0.27, 0.13, 0.14); p.arms[1].wrist.set(0.15, 0.32, 0.33); };
for (const p of Object.values(PEOPLE)) { rest(p); p.setArms(); }
// вилка в руке папы
const steel = M('#c8ccd0', { metalness: 0.9, roughness: 0.25 });
const fork = new THREE.Group(); dad.torso.add(fork);
mesh(new THREE.CylinderGeometry(0.005, 0.006, 0.12, 10), steel, 0, 0.07, 0, fork);
mesh(new THREE.BoxGeometry(0.03, 0.012, 0.004), steel, 0, 0.135, 0, fork);
for (let k = 0; k < 4; k++) mesh(new THREE.CylinderGeometry(0.0018, 0.0018, 0.045, 6), steel, -0.0115 + k * 0.0077, 0.162, 0, fork);
// телефон папы
const phoneG = new THREE.Group(); dad.torso.add(phoneG); phoneG.visible = false;
mesh(roundBox(0.08, 0.16, 0.01, 0.008), M('#111', { roughness: 0.3, metalness: 0.3 }), 0, 0, 0, phoneG);
const phoneCan = document.createElement('canvas'); phoneCan.width = 600; phoneCan.height = 1200;
const phoneTex = new THREE.CanvasTexture(phoneCan); phoneTex.colorSpace = THREE.SRGBColorSpace;
const phoneScr = new THREE.Mesh(new THREE.PlaneGeometry(0.072, 0.144), new THREE.MeshBasicMaterial({ map: phoneTex, toneMapped: false })); phoneScr.position.z = 0.0062; phoneG.add(phoneScr);

// ---------- полка, дрель, мелочи ----------
const shelf = new THREE.Group(); shelf.position.set(1.4, 1.74, 0.0); back.add(shelf);
const board = mesh(roundBox(0.72, 0.035, 0.22, 0.01), woodM, 0, 0, 0.12, shelf); board.rotation.z = -0.16;
mesh(new THREE.CylinderGeometry(0.004, 0.004, 0.05, 8), M('#777', { metalness: 0.9 }), -0.28, 0.06, 0.03, shelf).rotation.x = Math.PI / 2;
const brk = mesh(new THREE.BoxGeometry(0.02, 0.14, 0.12), M('#3a3a3a', { metalness: 0.6, roughness: 0.4 }), -0.27, -0.03, 0.07, shelf);
for (const [x, y] of [[-0.15, 0.22], [0.05, 0.19], [0.22, 0.25], [0.3, 0.05], [-0.05, -0.12], [0.12, -0.2], [-0.32, 0.18]]) mesh(new THREE.CircleGeometry(0.008, 12), M('#1c140e'), x, y, 0.004, shelf);
mesh(new THREE.PlaneGeometry(0.66, 0.05), M('#cfc6a0', { roughness: 1 }), 0.02, 0.11, 0.002, shelf); // светлый след от старой полки
const drill = new THREE.Group(); drill.position.set(0.6, 2.12, -RD / 2 + 0.3); drill.rotation.y = -0.6; scene.add(drill);
mesh(roundBox(0.2, 0.07, 0.06, 0.02), M('#e0702a', { roughness: 0.5 }), 0, 0.07, 0, drill);
mesh(roundBox(0.06, 0.13, 0.05, 0.015), M('#222', { roughness: 0.6 }), -0.05, 0.0, 0, drill).rotation.z = 0.25;
mesh(new THREE.CylinderGeometry(0.016, 0.02, 0.05, 16), M('#444', { metalness: 0.7 }), 0.12, 0.07, 0, drill).rotation.z = Math.PI / 2;
mesh(new THREE.CylinderGeometry(0.004, 0.004, 0.09, 8), steel, 0.19, 0.07, 0, drill).rotation.z = Math.PI / 2;
const dust = M('#bdb5a0', { roughness: 1, transparent: true, opacity: 0.5 }); mesh(new THREE.BoxGeometry(0.2, 0.004, 0.06), dust, 0, 0.107, 0, drill);
// картина и выключатель на передней стене
const pic = new THREE.Group(); pic.position.set(-1.9, 1.75, 0.03); front.add(pic);
mesh(new THREE.BoxGeometry(0.5, 0.4, 0.03), woodM, 0, 0, 0, pic);
mesh(new THREE.PlaneGeometry(0.42, 0.32), new THREE.MeshStandardMaterial({ map: plateArt(110), roughness: 0.8 }), 0, 0, 0.017, pic);
mesh(roundBox(0.08, 0.12, 0.02, 0.006), M('#f1ece0'), -0.25, 1.2, 0.03, front);
// закуски
const food = (geo, col, x, z, y = 0.79) => mesh(geo, M(col, { roughness: 0.6 }), x, y, z, table);
mesh(lp(0.12), plateM, -0.55, 0.777, 0.0, table);
for (let i = 0; i < 6; i++) { const a = i / 6 * 6.28; const c = food(new THREE.CylinderGeometry(0.03, 0.03, 0.006, 20), '#c4685e', -0.55 + Math.cos(a) * 0.055, Math.sin(a) * 0.055, 0.795); for (let k = 0; k < 4; k++) mesh(new THREE.CircleGeometry(0.004, 8), M('#f1e6d8'), (rng() - 0.5) * 0.03, 0.004, (rng() - 0.5) * 0.03, c).rotation.x = -Math.PI / 2; }
mesh(lp(0.11), plateM, 0.72, 0.777, -0.3, table);
for (let i = 0; i < 4; i++) { const p = food(new THREE.CapsuleGeometry(0.014, 0.05, 6, 12), '#4f6d34', 0.69 + i * 0.022, -0.3, 0.8); p.rotation.z = Math.PI / 2; p.rotation.y = 0.3; }
for (let i = 0; i < 3; i++) food(roundBox(0.06, 0.02, 0.05, 0.006), '#efd38a', 0.2 + i * 0.07, 0.05, 0.79).rotation.y = i * 0.3;
for (let i = 0; i < 3; i++) food(roundBox(0.07, 0.016, 0.055, 0.01), '#d7a76b', -0.25 + i * 0.03, -0.05 + i * 0.01, 0.787 + i * 0.012).rotation.y = i * 0.5;
for (const [x, z, ry] of [[0.4, -0.46, 0], [-0.45, -0.46, 0], [0, 0.46, Math.PI]]) {
  const f2 = mesh(new THREE.BoxGeometry(0.012, 0.004, 0.17), steel, x - 0.17, 0.781, z * 0.83, table); f2.rotation.y = ry;
  const kn = mesh(new THREE.BoxGeometry(0.014, 0.004, 0.19), steel, x + 0.17, 0.781, z * 0.83, table); kn.rotation.y = ry;
  mesh(new THREE.BoxGeometry(0.09, 0.004, 0.13), M('#f3efe6', { roughness: 0.9 }), x - 0.17, 0.779, z * 0.83, table);
}
for (const [x, z] of [[0.62, -0.18], [-0.68, -0.15], [0.2, 0.3]]) mesh(new THREE.CylinderGeometry(0.03, 0.026, 0.1, 24, 1, true), new THREE.MeshPhysicalMaterial({ color: '#e9f1ee', roughness: 0.05, transparent: true, opacity: 0.35, side: THREE.DoubleSide }), x, 0.83, z, table);

// ---------- ноутбук с каналом ----------
const lap = new THREE.Group(); lap.position.set(0, 0.783, 0.36); scene.add(lap);
const alu = M('#a3a8b0', { metalness: 0.6, roughness: 0.35 });
mesh(roundBox(0.34, 0.016, 0.23, 0.006), alu, 0, 0.008, 0, lap);
mesh(new THREE.PlaneGeometry(0.29, 0.1), M('#2b2d31', { roughness: 0.7 }), 0, 0.0165, -0.02, lap).rotation.x = -Math.PI / 2;
const hinge = new THREE.Group(); hinge.position.set(0, 0.016, -0.112); lap.add(hinge);
mesh(roundBox(0.34, 0.225, 0.009, 0.006), alu, 0, 0.1125, -0.002, hinge);
const tgCan = document.createElement('canvas'); tgCan.width = 1280; tgCan.height = 800;
const tgTex = new THREE.CanvasTexture(tgCan); tgTex.colorSpace = THREE.SRGBColorSpace; tgTex.anisotropy = 8;
const scr = new THREE.Mesh(new THREE.PlaneGeometry(0.312, 0.195), new THREE.MeshBasicMaterial({ map: tgTex, toneMapped: false })); scr.position.set(0, 0.1125, 0.0035); hinge.add(scr);
const scrLight = new THREE.PointLight('#e4ecff', 0, 1.2, 2); scrLight.position.set(0, 0.11, 0.15); hinge.add(scrLight);
const avatar = new Image(); avatar.src = 'tg_avatar.png';

const cat = makeCat(); scene.add(cat.g);

// ---------- искры ----------
const starCan = document.createElement('canvas'); starCan.width = starCan.height = 128;
{ const g = starCan.getContext('2d'); const gr = g.createRadialGradient(64, 64, 2, 64, 64, 60); gr.addColorStop(0, 'rgba(255,240,170,1)'); gr.addColorStop(0.3, 'rgba(255,200,60,0.9)'); gr.addColorStop(1, 'rgba(255,180,0,0)');
  g.fillStyle = gr; g.beginPath(); for (let k = 0; k < 8; k++) { const a = k * Math.PI / 4, rr = k % 2 ? 14 : 62; g.lineTo(64 + Math.cos(a) * rr, 64 + Math.sin(a) * rr); } g.fill(); }
const starTex = new THREE.CanvasTexture(starCan);
const sparks = []; for (let i = 0; i < 26; i++) { const m = new THREE.Mesh(new THREE.PlaneGeometry(0.03, 0.03), new THREE.MeshBasicMaterial({ map: starTex, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false }));
  m.visible = false; scene.add(m); sparks.push({ m, v: new THREE.Vector3((rng() - 0.5) * 0.9, 0.3 + rng() * 0.8, 0.2 + rng() * 0.6), s: 0.6 + rng() * 0.9, d: rng() * 0.15 }); }

// ---------- экран Телеграма ----------
function star4(g, x, y, r, a) { g.save(); g.globalAlpha = a; g.fillStyle = '#ffd34d'; g.beginPath(); for (let k = 0; k < 8; k++) { const an = k * Math.PI / 4 - Math.PI / 2, rr = k % 2 ? r * 0.28 : r; g.lineTo(x + Math.cos(an) * rr, y + Math.sin(an) * rr); } g.fill(); g.restore(); }
function pawPrint(g, x, y, s, a, rot) { g.save(); g.globalAlpha = a; g.translate(x, y); g.rotate(rot); g.fillStyle = '#e0453a'; g.beginPath(); g.ellipse(0, 6 * s, 11 * s, 9 * s, 0, 0, 7); g.fill();
  for (const [dx, dy] of [[-11, -6], [-4, -12], [4, -12], [11, -6]]) { g.beginPath(); g.ellipse(dx * s, dy * s, 4 * s, 5 * s, 0, 0, 7); g.fill(); } g.restore(); }
function rrect(g, x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
const POSTS = ['Это не лень', 'Дофаминовое меню', 'Почему ты гений в 3 ночи', 'Слепота ко времени', 'Посиди со мной', 'Гиперфокус'];
const BTN = { x: 70, y: 560, w: 440, h: 104 };
function drawTG(t, st) {
  const g = tgCan.getContext('2d'), W = 1280, H = 800;
  g.fillStyle = '#0e1621'; g.fillRect(0, 0, W, H);
  g.fillStyle = '#17212b'; g.fillRect(0, 0, W, 64); g.fillStyle = '#6c7883'; g.font = '600 28px Onest'; g.fillText('Telegram', 30, 42);
  // правая колонка: посты, листаются
  g.save(); g.beginPath(); g.rect(560, 64, 720, H - 64); g.clip();
  for (let i = 0; i < 9; i++) { const y = 100 + i * 190 - st.scroll; const P = POSTS[i % POSTS.length];
    g.fillStyle = '#182533'; rrect(g, 590, y, 650, 165, 22); g.fill();
    if (avatar.complete) { g.save(); g.beginPath(); g.arc(640, y + 50, 30, 0, 7); g.clip(); g.drawImage(avatar, 610, y + 20, 60, 60); g.restore(); }
    g.fillStyle = '#ffffff'; g.font = '700 32px Onest'; g.fillText(P, 690, y + 62);
    g.fillStyle = '#3a4b5c'; for (let k = 0; k < 2; k++) { rrect(g, 615, y + 95 + k * 28, 560 - k * 160, 14, 7); g.fill(); } }
  g.restore();
  // левая колонка: аватар, имя, кнопка
  const pulse = 1 + Math.sin(t * 4) * 0.015;
  g.save(); g.translate(290, 250); g.scale(pulse, pulse); g.beginPath(); g.arc(0, 0, 130, 0, 7); g.fillStyle = '#f4f1ea'; g.fill(); g.clip();
  const al = st.alive || 0, hop = al > 0 && al < 1 ? Math.abs(Math.sin(al * Math.PI * 3)) * (1 - al) : 0;
  g.translate(0, -hop * 30); g.scale(1 + hop * 0.06, 1 - hop * 0.06);
  if (avatar.complete) g.drawImage(avatar, -130, -130, 260, 260);
  if (al > 0.08 && al < 0.75) { g.fillStyle = '#2f2d33'; g.beginPath(); g.arc(26, 0, 22, 0, 7); g.fill(); g.strokeStyle = '#141216'; g.lineWidth = 5; g.beginPath(); g.moveTo(10, 4); g.quadraticCurveTo(26, -10, 42, 4); g.stroke(); }
  if (al > 0 && al < 1) { g.save(); g.translate(-78, 30); g.rotate(-0.6 + Math.sin(al * 20) * 0.6); g.fillStyle = '#2f2d33'; g.beginPath(); g.ellipse(0, -26, 14, 26, 0, 0, 7); g.fill(); g.fillStyle = '#e8875a'; g.beginPath(); g.arc(0, -44, 6, 0, 7); g.fill(); g.restore(); }
  g.restore();
  g.lineWidth = 6; g.strokeStyle = '#2ea6ff'; g.beginPath(); g.arc(290, 250, 136, 0, 7); g.stroke();
  for (const [x, y, ph] of [[150, 140, 0], [440, 150, 1.7], [455, 330, 3.1], [130, 340, 4.4], [300, 95, 2.4]]) star4(g, x, y, 22 + 8 * Math.sin(t * 5 + ph), 0.5 + 0.5 * Math.sin(t * 5 + ph));
  g.textAlign = 'center'; g.fillStyle = '#fff'; g.font = '800 48px Onest'; g.fillText('СДВГ | Напарник', 290, 448);
  pawPrint(g, 520, 425, 1.0, 1, 0.3);
  g.fillStyle = '#5eb5f7'; g.font = '600 32px Onest'; g.fillText('t.me/ru_adhd', 290, 500);
  // кнопка
  const press = st.press || 0, sub = st.sub;
  if (st.hideBtn) { g.fillStyle = 'rgba(0,0,0,0.35)'; rrect(g, BTN.x, BTN.y, BTN.w, BTN.h, 30); g.fill(); } else {
  g.save(); g.translate(BTN.x + BTN.w / 2, BTN.y + BTN.h / 2); const sc = 1 - press * 0.06; g.scale(sc, sc);
  g.fillStyle = sub ? '#4fae4e' : '#2ea6ff'; rrect(g, -BTN.w / 2, -BTN.h / 2, BTN.w, BTN.h, 30); g.fill();
  g.fillStyle = 'rgba(255,255,255,0.18)'; rrect(g, -BTN.w / 2 + 8, -BTN.h / 2 + 6, BTN.w - 16, BTN.h * 0.42, 24); g.fill();
  g.fillStyle = '#fff'; g.font = '800 44px Onest'; g.fillText(sub ? '✓ ВЫ ПОДПИСАНЫ' : 'ПОДПИСАТЬСЯ', 0, 15); g.restore(); }
  if (st.ripple > 0 && st.ripple < 1) { g.strokeStyle = `rgba(255,255,255,${1 - st.ripple})`; g.lineWidth = 10; g.beginPath(); g.arc(BTN.x + 150, BTN.y + 60, 30 + st.ripple * 260, 0, 7); g.stroke(); }
  // красные следы лап к кнопке
  const trail = [[1180, 760, -0.9], [1060, 730, -1.2], [940, 720, -1.4], [820, 700, -1.5], [700, 690, -1.6], [600, 650, -1.7]];
  trail.forEach(([x, y, r], k) => { const a = Math.max(0, Math.min(1, st.paws * trail.length - k)); if (a > 0) pawPrint(g, x, y, 1.3, a, r); });
  if (st.burst > 0 && st.burst < 1) for (let k = 0; k < 12; k++) { const an = k / 12 * 6.28, d = 40 + st.burst * 220; star4(g, BTN.x + 150 + Math.cos(an) * d, BTN.y + 60 + Math.sin(an) * d * 0.7, 26 * (1 - st.burst * 0.6), 1 - st.burst); }
  g.textAlign = 'left'; tgTex.needsUpdate = true;
}
function drawPhone(t) {
  const g = phoneCan.getContext('2d'), W = 600, H = 1200;
  g.fillStyle = '#0e1621'; g.fillRect(0, 0, W, H); g.textAlign = 'center';
  g.save(); g.beginPath(); g.arc(300, 210, 110, 0, 7); g.fillStyle = '#f4f1ea'; g.fill(); g.clip(); if (avatar.complete) g.drawImage(avatar, 190, 100, 220, 220); g.restore();
  for (const [x, y, ph] of [[150, 120, 0], [460, 140, 2], [470, 300, 4]]) star4(g, x, y, 20 + 6 * Math.sin(t * 5 + ph), 0.6 + 0.4 * Math.sin(t * 5 + ph));
  g.fillStyle = '#fff'; g.font = '800 46px Onest'; g.fillText('СДВГ | Напарник', 300, 380);
  g.fillStyle = '#4fae4e'; rrect(g, 70, 420, 460, 90, 28); g.fill(); g.fillStyle = '#fff'; g.font = '800 38px Onest'; g.fillText('✓ ВЫ ПОДПИСАНЫ', 300, 478);
  g.fillStyle = '#182533'; rrect(g, 40, 560, 520, 560, 26); g.fill();
  g.textAlign = 'left'; g.fillStyle = '#fff'; g.font = '700 40px Onest'; g.fillText('Это не лень', 80, 630);
  g.fillStyle = '#3a4b5c'; for (let k = 0; k < 9; k++) { rrect(g, 80, 670 + k * 44, 440 - (k % 3) * 70, 18, 9); g.fill(); }
  g.fillStyle = '#2ea6ff'; rrect(g, 560, 570, 10, 60, 5); g.fill(); // ползунок прокрутки в самом верху: первый пост, начало
  phoneTex.needsUpdate = true;
}
// ---------- свет ----------
scene.add(new THREE.HemisphereLight('#fff1d8', '#5b3e2a', 0.75));
const key = new THREE.DirectionalLight('#fff4e0', 2.4); key.position.set(-3.5, 3.2, 1.2); key.target.position.set(0, 0.8, 0); scene.add(key, key.target);
key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.camera.left = -3; key.shadow.camera.right = 3; key.shadow.camera.top = 3; key.shadow.camera.bottom = -3; key.shadow.bias = -0.0004; key.shadow.normalBias = 0.02; key.shadow.radius = 6;
const top = new THREE.PointLight('#ffe3b8', 3.0, 6, 2); top.position.set(0, RH - 0.45, 0); top.castShadow = true; top.shadow.mapSize.set(1024, 1024); top.shadow.radius = 8; top.shadow.bias = -0.002; scene.add(top);
const rim = new THREE.SpotLight('#fff0dc', 6, 6, 0.6, 0.8, 2); rim.position.set(1.8, 2.4, -1.5); rim.target.position.set(0.3, 1.3, 1.2); scene.add(rim, rim.target);

const fill = new THREE.PointLight('#fff2e2', 1.6, 4, 1.5); camera.add(fill); fill.position.set(0.15, 0.2, 0.1); scene.add(camera);
// ---------- пост ----------
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const gtao = new GTAOPass(scene, camera, W, H); gtao.updateGtaoMaterial({ radius: 0.35, distanceExponent: 1.5, thickness: 1, scale: 1.2, samples: 16 }); gtao.blendIntensity = 0.85; composer.addPass(gtao);
const bokeh = new BokehPass(scene, camera, { focus: 1.5, aperture: 0.0012, maxblur: 0.006 }); composer.addPass(bokeh);
composer.addPass(new OutputPass());


// ---------- объёмная кнопка, следы на столе ----------
const btnCan = document.createElement('canvas'); btnCan.width = 512; btnCan.height = 128; const btnTex = new THREE.CanvasTexture(btnCan); btnTex.colorSpace = THREE.SRGBColorSpace;
function drawBtn(sub) { const g = btnCan.getContext('2d'); g.clearRect(0, 0, 512, 128); g.fillStyle = sub ? '#4fae4e' : '#2ea6ff'; rrect(g, 4, 4, 504, 120, 40); g.fill();
  g.fillStyle = 'rgba(255,255,255,0.22)'; rrect(g, 14, 10, 484, 50, 30); g.fill(); g.fillStyle = '#fff'; g.font = '800 54px Onest'; g.textAlign = 'center'; g.fillText(sub ? '✓ ВЫ ПОДПИСАНЫ' : 'ПОДПИСАТЬСЯ', 256, 84); g.textAlign = 'left'; btnTex.needsUpdate = true; }
const btn3 = new THREE.Group(); scr.add(btn3); btn3.visible = false;
const btnBody = new THREE.Mesh(roundBox(0.106, 0.026, 0.008, 0.004), M('#1f86d6', { roughness: 0.4 })); btn3.add(btnBody);
const btnFace = new THREE.Mesh(new THREE.PlaneGeometry(0.104, 0.026), new THREE.MeshBasicMaterial({ map: btnTex, transparent: true, toneMapped: false })); btnFace.position.z = 0.0045; btn3.add(btnFace);
const BTN_LOCAL = new THREE.Vector3(-0.0853, -0.0517, 0);
const pawCan = document.createElement('canvas'); pawCan.width = pawCan.height = 128; pawPrint(pawCan.getContext('2d'), 64, 70, 3.2, 1, 0); const pawTex = new THREE.CanvasTexture(pawCan); pawTex.colorSpace = THREE.SRGBColorSpace;
const tablePaws = []; const PAW_PATH = [[-0.12, 0.8, 0.27], [-0.14, 0.8, 0.33], [-0.18, 0.785, 0.38], [-0.21, 0.785, 0.42], [-0.25, 0.785, 0.44]];
PAW_PATH.forEach((p, k) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(0.035, 0.035), new THREE.MeshBasicMaterial({ map: pawTex, transparent: true, depthWrite: false, toneMapped: false })); m.rotation.x = -Math.PI / 2; m.rotation.z = 0.6 + k * 0.1; m.position.set(...p); m.position.y += 0.0015; m.visible = false; scene.add(m); tablePaws.push(m); });
// ---------- анимация ----------
const V = window.VOICE; const FPS = 30;
const cl = (x) => Math.max(0, Math.min(1, x));
const ease = (x) => { x = cl(x); return x * x * (3 - 2 * x); };
const eout = (x) => { x = cl(x); return 1 - Math.pow(1 - x, 3); };
const back2 = (x) => { x = cl(x); const c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
const mouthOf = (sp, t) => { const m = V.mouth[sp], i = t * FPS, a = Math.floor(i); return (m[a] || 0) * (1 - (i - a)) + (m[a + 1] || 0) * (i - a); };
const blinkAt = (t, times) => { for (const b of times) { const d = (t - b) / 0.15; if (d >= 0 && d <= 1) return Math.sin(d * Math.PI); } return 0; };
const v3 = (a) => new THREE.Vector3(...a);
const SHOTS = [
  { t0: 0, t1: 2.86, p: [0.47, 1.22, 0.5], l: [0.4, 1.13, -0.78], hook: true },
  { t0: 2.86, t1: 4.62, p: [-0.05, 1.22, -0.5], l: [0, 1.13, 0.8], push: 0.08 },
  { t0: 4.62, t1: 6.45, p: [-0.55, 1.22, 0.72], l: [-0.45, 1.15, -0.78], push: 0.08 },
  { t0: 6.45, t1: 8.2, p: [0.85, 1.62, -1.05], l: [1.3, 1.86, -2.62], fov: 40, push: 0.18 },
  { t0: 8.2, t1: 11.25, p: [0.12, 1.2, 0.42], l: [0.4, 1.14, -0.78], push: 0.1 },
  { t0: 11.25, t1: 14.3, p: [0.95, 1.32, -1.0], l: [0, 1.12, 0.8], push: 0.1 },
  { t0: 14.3, t1: 15.9, p: [0.1, 1.3, -0.4], l: [0, 1.08, 0.7], push: 0.06 },
  { t0: 15.9, t1: 19.65, p: [-0.3, 1.03, 1.08], l: [-0.08, 0.9, 0.28], fov: 40, push: 0.15, noDima: true },
  { t0: 19.65, t1: 23.2, p: [0.5, 1.2, 0.55], l: [0.45, 1.12, -0.78], push: 0.08 },
  { t0: 23.2, t1: 99, p: [-0.12, 1.06, 1.05], l: [-0.31, 0.98, 0.3], push: 0.06, noDima: true },
];
const SHELF_POS = [1.36, 1.765, -2.66];
const CAT_TABLE = [-0.33, 0.783, 0.3];
const TAP = 18.62;
const blinks = { dad: [2.3, 5.1, 9.2, 13.3, 21.0], mom: [2.2, 7.3, 10.6, 17.5, 22.3], dima: [3.9, 7.9, 12.6, 16.4, 23.6] };
const tmp = new THREE.Vector3();
function toLocal(obj, w) { return obj.worldToLocal(w.clone()); }
window.duration = V.total;
window.renderFrame = (t) => {
  const si = SHOTS.findIndex((s) => t >= s.t0 && t < s.t1); const sh = SHOTS[si < 0 ? SHOTS.length - 1 : si];
  const u = (t - sh.t0) / Math.max(0.01, sh.t1 - sh.t0);
  const P = v3(sh.p), L = v3(sh.l); const dir = P.clone().sub(L);
  let k = 1 - (sh.push || 0) * u; let roll = 0;
  if (sh.hook) { const f = eout(t / 0.38); k *= 1.75 - 0.75 * f + (t > 0.38 && t < 0.6 ? -0.03 * Math.sin((t - 0.38) / 0.22 * Math.PI) : 0); roll = (1 - f) * 0.06; }
  camera.position.copy(L).addScaledVector(dir, k); camera.position.x += Math.sin(t * 1.3) * 0.004; camera.position.y += Math.sin(t * 1.7 + 1) * 0.003;
  camera.fov = sh.fov || 32; camera.updateProjectionMatrix(); camera.lookAt(L); camera.rotateZ(roll);
  bokeh.uniforms.focus.value = dir.length() * k; fill.intensity = Math.min(1.6, Math.max(0.35, (dir.length() * k - 0.5) * 1.6));
  dima.root.visible = !sh.noDima;
  scene.updateMatrixWorld(true);

  // --- голоса и лица ---
  for (const [name, p] of Object.entries(PEOPLE)) {
    const m = mouthOf(name, t); p.face.st.mouth = m; p.face.st.blink = blinkAt(t, blinks[name]);
    p.headPivot.rotation.set(Math.sin(t * 7.3) * 0.035 * m - 0.03, Math.sin(t * 0.9 + name.length) * 0.04, Math.sin(t * 1.3 + name.length) * 0.02);
    p.torso.position.y = p.baseY + Math.sin(t * 2.4 + name.length) * 0.004; p.torso.rotation.set(0, 0, Math.sin(t * 1.1 + name.length) * 0.012);
    p.face.st.look = [0, 0]; p.face.st.brow = 0; p.face.st.frown = 0; p.face.st.smile = 0.35; p.face.st.eyesWide = 0; p.face.st.round = 0; p.face.st.sleepy = 0;
    rest(p);
  }
  // папа: ест, говорит не поднимая глаз
  { const s = dad.face.st, h = dad.headPivot.rotation;
    if (t < 2.86) { s.look = [0, 0.9]; s.sleepy = 0.25; s.smile = 0.1; h.x += 0.1; const chew = t < 2.6 && dad.face.st.mouth < 0.1 ? Math.abs(Math.sin(t * 9)) * 0.25 : 0; s.mouth = Math.max(s.mouth, chew);
      dad.arms[1].wrist.set(0.17, 0.36 + 0.12 * eout(t / 0.3) + Math.sin(t * 6) * 0.02, 0.3); dad.arms[1].elbow.set(0.29, 0.16, 0.12); }
    else if (t < 8.2) { s.look = [-0.7, 0.2]; s.smile = 0.15; h.y += -0.25 * ease((t - 4.7) / 0.3); s.frown = 0.3 * ease((t - 5.0) / 0.3); }
    else if (t < 11.25) { const sh2 = ease((t - 8.4) / 0.35) * (1 - ease((t - 10.6) / 0.4)); dad.torso.position.y += sh2 * 0.025;
      dad.arms[0].wrist.set(-0.24 - sh2 * 0.08, 0.36 + sh2 * 0.12, 0.3); dad.arms[1].wrist.set(0.24 + sh2 * 0.08, 0.36 + sh2 * 0.12, 0.3);
      s.look = t > 9.6 ? [0.3, -0.8] : [0, 0]; s.sleepy = t > 9.6 ? 0.2 : 0; s.smile = 0.5; s.brow = t > 9.6 ? 0.6 : 0.2; h.x += t > 9.6 ? -0.08 : 0; }
    else if (t < 19.65) { s.look = [0, 0]; s.frown = 0.2; s.smile = 0.2; if (t > 12.6) { s.eyesWide = 0.3; s.brow = 0.4; } }
    else { const up = eout((t - 19.68) / 0.3); phoneG.visible = true; phoneG.position.set(0.12, 0.3 + up * 0.17, 0.28 + up * 0.06); phoneG.rotation.set(-0.15, -0.12, 0.05);
      dad.arms[1].wrist.set(0.12, 0.24 + up * 0.17, 0.27 + up * 0.06); dad.arms[1].elbow.set(0.3, 0.12, 0.15); s.smile = 0.75; s.brow = 0.5; s.look = [0.1, 0.1]; if (t > 21.7) { s.look = [0, 0.6]; s.sleepy = 0.15; } }
    if (t < 19.65) phoneG.visible = false;
  }
  // мама
  { const s = mom.face.st, h = mom.headPivot.rotation;
    if (t >= 4.62 && t < 6.6) { s.frown = 0.8; s.smile = -0.3; s.look = [0.9, 0]; h.y += 0.35 * ease((t - 4.62) / 0.2); }
    else if (t >= 6.6 && t < 8.3) { s.frown = 0.5; s.look = [0.6, 0]; h.y += 0.3; }
    else if (t >= 19.65) { s.look = [0.9, 0.1]; s.sleepy = 0.35; s.smile = 0.1; h.y += 0.3; if (t > 21.8) { s.look = [0.2, -0.9]; } } // закатывает глаза
    else { s.look = [0.5, 0]; }
    mom.arms[0].wrist.set(-0.12, 0.33, 0.32); mom.arms[1].wrist.set(0.1, 0.34, 0.31);
  }
  // Дима
  { const s = dima.face.st;
    if (t >= 2.86 && t < 4.62) { s.brow = 0.6; s.smile = 0.15; s.look = [0, 0]; }
    else if (t >= 11.25 && t < 14.3) { s.smile = 0.45; s.brow = 0.3; s.sleepy = 0.15; }
    else if (t >= 14.3 && t < 15.9) { s.smile = 0.6; s.look = t > 15.0 ? [0, 0] : [0, 0.8]; if (t > 15.0) dima.headPivot.rotation.x -= 0.06; }
    else { s.look = [0, 0]; }
  }
  // ноутбук
  const op = back2((t - 14.45) / 0.5); hinge.rotation.x = Math.PI / 2 * (1 - op) - 0.2 * op;
  scr.visible = op > 0.3; scrLight.intensity = op * 0.5;
  if (t >= 14.3 && t < 15.1) { scene.updateMatrixWorld(true); for (const [i, sx] of [[0, -1], [1, 1]]) { const w = hinge.localToWorld(new THREE.Vector3(sx * 0.1, 0.22, 0.02)); const loc = toLocal(dima.torso, w);
    const a = ease((t - 14.3) / 0.2); if (loc.length() < 0.55) dima.arms[i].wrist.lerp(loc, a * (1 - ease((t - 14.6) / 0.18))); } }
  const sub = t >= TAP + 0.08;
  const pop = ease((t - 17.55) / 0.3) * (1 - ease((t - 19.0) / 0.25)); const hide2d = pop > 0.02;
  drawTG(t, { scroll: 40 + Math.max(0, t - 15) * 60, press: 0, sub, ripple: (t - TAP) / 0.6, burst: 0, paws: cl((t - 16.6) / 1.0), alive: (t - TAP) / 1.1, hideBtn: hide2d });
  btn3.visible = pop > 0.02 && t < 19.4; drawBtn(sub);
  { const tapK = Math.max(0, 1 - Math.abs(t - TAP) / 0.1); const wob = Math.sin((t - 17.55) * 18) * Math.exp(-(t - 17.55) * 4) * (t > 17.55 ? 1 : 0);
    btn3.position.copy(BTN_LOCAL).add(new THREE.Vector3(0, 0, 0.004 + pop * 0.045 - tapK * 0.03)); const sc = 1 + pop * 0.3 - tapK * 0.08 + wob * 0.05; btn3.scale.set(sc, sc, sc); btn3.rotation.set(-0.15 * pop, 0.2 * pop * (1 - tapK), wob * 0.08); }
  tablePaws.forEach((m, k) => { m.visible = t > TAP + 0.25 + k * 0.14 && t < 24.4; });
  for (const e of cat.eyes) e.refl.visible = op > 0.3 && (sh === SHOTS[7] || sh === SHOTS[9]);
  if (t > 19.5) drawPhone(t);

  // кот
  const lids = (v) => { for (const e of cat.eyes) { e.lid.rotation.x = -1.4 + v; e.p.visible = e.hl.visible = v < 2.5; } };
  if (t < 15.95) { cat.g.position.set(...SHELF_POS); cat.g.rotation.set(0, 0.2, -0.16); lids(1.25); cat.headPivot.rotation.set(0.25, 0.1, 0.1); cat.setPaw(null); lids(2.95);
    cat.g.scale.set(1, 1 + Math.sin(t * 2.2) * 0.02, 1); }
  else {
    const j = cl((t - 15.95) / 0.42); const from = v3([-0.7, 1.3, 0.2]), to = v3(CAT_TABLE);
    const pos = from.clone().lerp(to, j); pos.y += Math.sin(j * Math.PI) * 0.18; cat.g.position.copy(pos);
    const land = (t - 16.37) / 0.25; const sq = land > 0 && land < 1 ? Math.sin(land * Math.PI) * 0.18 : 0; cat.g.scale.set(1 + sq * 0.5, 1 - sq, 1 + sq * 0.5);
    cat.g.rotation.set(0, t > 23.2 ? 0.25 : 0.55, 0);
    lids(t > 23.2 && t < 23.65 ? 1.6 : 0.0);
    if (t > 23.65) { cat.eyes[1].lid.rotation.x = -1.4 + 2.95; cat.eyes[1].p.visible = cat.eyes[1].hl.visible = cat.eyes[1].refl.visible = false; } // один глаз хитро прищурен
    cat.headPivot.rotation.set(0.05 + Math.sin(t * 1.1) * 0.03, t < 18.9 ? -0.35 : 0.1, 0);
    scene.updateMatrixWorld(true);
    const btn = btn3.visible ? btn3.localToWorld(new THREE.Vector3(-0.02, 0, 0.012)) : scr.localToWorld(new THREE.Vector3(-0.1, -0.052, 0.01));
    const reach = ease((t - 17.9) / 0.5) * (1 - ease((t - TAP - 0.25) / 0.3)); const tap = Math.max(0, 1 - Math.abs(t - TAP) / 0.1);
    if (reach > 0.01) { const tgt = toLocal(cat.g, btn); const restP = new THREE.Vector3(0.05, 0.03, 0.13); const p2 = restP.clone().lerp(tgt, reach); p2.z -= tap * 0.012; cat.setPaw(p2); } else cat.setPaw(null);
  }
  cat.earR.rotation.x = 0.5 + (Math.abs(t - 16.5) < 0.08 || Math.abs(t - 23.9) < 0.08 ? 0.4 : 0);
  cat.setTail(t);
  // искры из экрана
  scene.updateMatrixWorld(true); const origin = scr.localToWorld(new THREE.Vector3(-0.085, -0.052, 0.05));
  for (const s2 of sparks) { const age = t - TAP - s2.d; if (false) { s2.m.visible = true; s2.m.position.copy(origin).addScaledVector(s2.v, age * 0.45 * s2.s); s2.m.position.y -= age * age * 0.25; s2.m.quaternion.copy(camera.quaternion); const sc = (1 - age / 0.9) * s2.s * 1.4; s2.m.scale.set(sc, sc, sc); } else s2.m.visible = false; }

  for (const p of Object.values(PEOPLE)) { p.setArms(); p.face.draw(); }
  fork.visible = t < 19.65; fork.position.copy(dad.arms[1].hand.position).add(new THREE.Vector3(0.0, 0.02, 0.02)); fork.rotation.set(0.25, 0, -0.15);
  composer.render();
  const bp = origin.clone().project(camera); return { btn: [(bp.x + 1) / 2, (1 - bp.y) / 2], tap: TAP };
};
window.debugView = (p, l, fov = 50, t = 1) => { window.renderFrame(t); camera.fov = fov; camera.updateProjectionMatrix(); camera.position.set(...p); camera.lookAt(...l); bokeh.uniforms.aperture.value = 0; dima.root.visible = true; composer.render(); camera.fov = 32; camera.updateProjectionMatrix(); bokeh.uniforms.aperture.value = 0.0012; };
document.fonts.load('800 40px Onest').then(() => { window.ready = true; });
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
window.exportGLB = (t) => new Promise((res, rej) => { window.renderFrame(t); scene.updateMatrixWorld(true);
  const cam = camera.clone(); cam.name = 'ShotCam';
  new GLTFExporter().parse([scene], (buf) => { const b = new Uint8Array(buf); let s = ''; for (let i = 0; i < b.length; i += 32768) s += String.fromCharCode.apply(null, b.subarray(i, i + 32768)); res({ glb: btoa(s), cam: { pos: camera.position.toArray(), quat: camera.quaternion.toArray(), fov: camera.fov } }); }, rej, { binary: true, onlyVisible: true, maxTextureSize: 2048 }); });
