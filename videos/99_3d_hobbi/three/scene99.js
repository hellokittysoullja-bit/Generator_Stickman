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
