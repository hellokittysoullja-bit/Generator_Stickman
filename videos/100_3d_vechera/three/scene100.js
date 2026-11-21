// 3D-рилс 100 «Перестал терять вечера в ленте»: Дима и кот; хук-результат в кресле, три боли (стол, кухня, спальня), кот уносит телефон, призыв ноутбуком с каналом. three.js → glb → Blender турбо.
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

// ---------- рендер и общие помощники ----------
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H); renderer.setPixelRatio(1);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene(); scene.background = new THREE.Color('#2a2420');
const camera = new THREE.PerspectiveCamera(34, W / H, 0.05, 40);
const RH = 2.8;
const wallTex = (base, stripe) => canvasTex(512, 512, (g, w, h) => {
  noiseFill(g, w, h, base, 0.06, 9000);
  for (let x = 0; x < w; x += 64) { g.fillStyle = stripe; g.fillRect(x, 0, 3, h); g.fillStyle = 'rgba(255,250,220,0.07)'; g.fillRect(x + 32, 0, 10, h); }
}, [3, 1.5]);
const tileTex = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#dfe6e2'; g.fillRect(0, 0, w, h); g.strokeStyle = '#b9c4bf'; g.lineWidth = 4; for (let k = 0; k <= w; k += 64) { g.beginPath(); g.moveTo(k, 0); g.lineTo(k, h); g.stroke(); g.beginPath(); g.moveTo(0, k); g.lineTo(w, k); g.stroke(); } }, [6, 3]);
const woodM = new THREE.MeshStandardMaterial({ map: woodTex, roughness: 0.5, color: '#c09a84' });
function wallSeg(parent, mat, w, x, z, ry, y0 = 0, h = RH) {
  const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = ry; parent.add(g);
  const pl = mesh(new THREE.PlaneGeometry(w, h - Math.max(y0, 0.12)), mat, 0, Math.max(y0, 0.12) + (h - Math.max(y0, 0.12)) / 2, 0, g); pl.castShadow = false;
  if (y0 < 0.1) mesh(new THREE.BoxGeometry(w, 0.12, 0.03), M('#efe8d8'), 0, 0.06, 0.015, g);
  return g;
}
function makeSet(x, wallMat, floorMat, opts = {}) {
  const s = new THREE.Group(); s.position.x = x; scene.add(s);
  const fl = mesh(new THREE.PlaneGeometry(6.5, 6), floorMat, 0, 0, 0, s); fl.rotation.x = -Math.PI / 2;
  wallSeg(s, wallMat, 6.5, 0, -2.3, 0);
  wallSeg(s, wallMat, 6, -2.6, 0.7, Math.PI / 2);
  if (opts.door) { wallSeg(s, wallMat, 1.3, 2.6, -1.65, -Math.PI / 2); wallSeg(s, wallMat, 2.3, 2.6, 1.05, -Math.PI / 2); wallSeg(s, wallMat, 0.9, 2.6, -0.55, -Math.PI / 2, 2.12);
    for (const [w, h, zz, y] of [[0.08, 2.15, -1.0, 1.075], [0.08, 2.15, -0.1, 1.075], [1.0, 0.08, -0.55, 2.14]]) mesh(new THREE.BoxGeometry(0.1, h, w), M('#efe9dc', { roughness: 0.6 }), 2.6, y, zz, s);
    const hall = mesh(new THREE.PlaneGeometry(1.2, 2.2), M('#3b3430', { roughness: 1 }), 3.4, 1.1, -0.55, s); hall.rotation.y = -Math.PI / 2;
    const hf = mesh(new THREE.PlaneGeometry(0.9, 1.0), M('#4a3a2c'), 3.0, 0.002, -0.55, s); hf.rotation.x = -Math.PI / 2;
  } else wallSeg(s, wallMat, 6, 2.6, 0.7, -Math.PI / 2);
  return s;
}
const floorM = new THREE.MeshStandardMaterial({ map: floorTex, roughness: 0.55 });
const setA = makeSet(0, new THREE.MeshStandardMaterial({ map: wallTex('#c9b98f', 'rgba(110,90,50,0.10)'), roughness: 0.95 }), floorM, { door: true });
const setK = makeSet(10, new THREE.MeshStandardMaterial({ map: tileTex, roughness: 0.4 }), floorM);
const setB = makeSet(20, new THREE.MeshStandardMaterial({ map: wallTex('#7f8fa8', 'rgba(40,50,80,0.12)'), roughness: 0.95 }), floorM);
const SETS = { A: setA, K: setK, B: setB };
const glowM = (c, k = 1.2) => new THREE.MeshStandardMaterial({ color: '#fff6e6', emissive: c, emissiveIntensity: k, roughness: 0.6 });
function windowOn(parent, x, y, z, ry, sky) { const g = new THREE.Group(); g.position.set(x, y, z); g.rotation.y = ry; parent.add(g);
  const pane = mesh(new THREE.PlaneGeometry(1.1, 1.2), new THREE.MeshBasicMaterial({ color: sky }), 0, 0, 0.005, g);
  for (const [w, h, xx, yy] of [[1.2, 0.07, 0, 0.63], [1.2, 0.1, 0, -0.63], [0.07, 1.3, -0.58, 0], [0.07, 1.3, 0.58, 0], [0.04, 1.2, 0, 0]]) mesh(new THREE.BoxGeometry(w, h, 0.06), M('#efe9dc'), xx, yy, 0.03, g);
  return pane; }

// ---------- гостиная (A): кресло, торшер, диван, стол с ноутбуком, дверь в коридор ----------
const fabric = M('#c4673f', { roughness: 0.95 }), fabric2 = M('#5f7d8c', { roughness: 0.95 });
const rugA = mesh(new THREE.PlaneGeometry(2.6, 2.0), new THREE.MeshStandardMaterial({ map: rugTex, roughness: 1 }), -0.6, 0.004, -0.6, setA); rugA.rotation.x = -Math.PI / 2;
const winA = windowOn(setA, -2.58, 1.55, -1.1, Math.PI / 2, '#fff4dc');
const AC = new THREE.Vector3(-0.9, 0, -1.3), ACR = 0.35;
const chair = new THREE.Group(); chair.position.copy(AC); chair.rotation.y = ACR; setA.add(chair);
mesh(roundBox(0.78, 0.2, 0.7, 0.06), fabric, 0, 0.33, 0.05, chair); mesh(roundBox(0.66, 0.12, 0.6, 0.05), fabric, 0, 0.47, 0.08, chair);
mesh(roundBox(0.78, 0.7, 0.18, 0.07), fabric, 0, 0.7, -0.26, chair);
for (const sx of [-1, 1]) mesh(roundBox(0.14, 0.36, 0.72, 0.06), fabric, sx * 0.36, 0.52, 0.04, chair);
for (const sx of [-1, 1]) for (const sz of [-1, 1]) mesh(new THREE.CylinderGeometry(0.025, 0.02, 0.24, 10), woodM, sx * 0.32, 0.12, 0.05 + sz * 0.28, chair);
mesh(roundBox(0.34, 0.3, 0.1, 0.05), M('#e9c46a', { roughness: 0.95 }), 0.18, 0.66, -0.12, chair).rotation.z = -0.2;
const lampA = new THREE.Group(); lampA.position.set(-1.75, 0, -1.75); setA.add(lampA);
mesh(new THREE.CylinderGeometry(0.16, 0.18, 0.03, 24), M('#2d2a28'), 0, 0.015, 0, lampA); mesh(new THREE.CylinderGeometry(0.012, 0.012, 1.45, 8), M('#2d2a28', { metalness: 0.6 }), 0, 0.74, 0, lampA);
const shadeA = mesh(new THREE.CylinderGeometry(0.15, 0.24, 0.3, 32, 1, true), glowM('#ffcf8a', 1.0), 0, 1.5, 0, lampA); shadeA.material.side = THREE.DoubleSide;
const sofa = new THREE.Group(); sofa.position.set(-2.1, 0, 0.2); sofa.rotation.y = Math.PI / 2; setA.add(sofa);
mesh(roundBox(1.7, 0.25, 0.8, 0.06), fabric2, 0, 0.3, 0, sofa); mesh(roundBox(1.6, 0.14, 0.7, 0.06), fabric2, 0, 0.48, 0.04, sofa); mesh(roundBox(1.7, 0.55, 0.2, 0.08), fabric2, 0, 0.7, -0.32, sofa);
for (const sx of [-1, 1]) mesh(roundBox(0.18, 0.4, 0.8, 0.07), fabric2, sx * 0.85, 0.5, 0, sofa);
mesh(roundBox(0.36, 0.3, 0.1, 0.05), M('#e8dcc4', { roughness: 0.95 }), -0.5, 0.67, -0.16, sofa).rotation.z = 0.2;
// стол, стул, ноутбук, настольная лампа
const DESK = new THREE.Vector3(1.3, 0.76, -1.6);
const desk = new THREE.Group(); desk.position.set(DESK.x, 0, DESK.z); setA.add(desk);
mesh(roundBox(1.3, 0.04, 0.6, 0.01), woodM, 0, 0.74, 0, desk);
for (const sx of [-1, 1]) for (const sz of [-1, 1]) mesh(new THREE.BoxGeometry(0.04, 0.72, 0.04), M('#2d2a28'), sx * 0.6, 0.36, sz * 0.26, desk);
const dchair = new THREE.Group(); dchair.position.set(1.3, 0, -1.02); setA.add(dchair);
mesh(roundBox(0.46, 0.06, 0.44, 0.02), M('#3b4a5a'), 0, 0.44, 0, dchair); mesh(roundBox(0.44, 0.5, 0.05, 0.02), M('#3b4a5a'), 0, 0.72, 0.21, dchair);
mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.4, 10), M('#222', { metalness: 0.6 }), 0, 0.22, 0, dchair);
const dlamp = new THREE.Group(); dlamp.position.set(0.74, 0.76, -1.76); setA.add(dlamp);
mesh(new THREE.CylinderGeometry(0.06, 0.07, 0.02, 20), M('#e4572e', { roughness: 0.5 }), 0, 0.01, 0, dlamp); const arm1 = mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.36, 8), M('#e4572e'), 0, 0.18, 0, dlamp);
const dshade = mesh(new THREE.ConeGeometry(0.08, 0.1, 24, 1, true), M('#e4572e', { side: THREE.DoubleSide }), -0.04, 0.37, 0.03, dlamp); dshade.rotation.z = 0.6;
const dbulb = mesh(new THREE.SphereGeometry(0.025, 16, 10), glowM('#ffe0a0', 0), -0.05, 0.34, 0.03, dlamp);
// полка и растения над столом
mesh(roundBox(0.9, 0.03, 0.22, 0.01), woodM, 1.3, 1.6, -2.18, setA);
for (const [x, c] of [[0.98, '#c97b4a'], [1.3, '#7aa86a'], [1.6, '#e9c46a']]) { mesh(new THREE.CylinderGeometry(0.06, 0.05, 0.12, 16), M(c), x, 1.68, -2.18, setA); mesh(new THREE.IcosahedronGeometry(0.09, 1), M('#4f8a45', { roughness: 0.9 }), x, 1.83, -2.18, setA); }
const posterA = canvasTex(256, 384, (g) => { g.fillStyle = '#f2c14e'; g.fillRect(0, 0, 256, 384); g.fillStyle = '#e4572e'; g.beginPath(); g.arc(128, 160, 80, 0, 7); g.fill(); g.fillStyle = '#20314a'; g.fillRect(40, 280, 176, 24); });
mesh(new THREE.PlaneGeometry(0.45, 0.66), new THREE.MeshStandardMaterial({ map: posterA, roughness: 0.8 }), -0.6, 1.75, -2.28, setA);
const plantA = new THREE.Group(); plantA.position.set(-2.2, 0, -1.9); setA.add(plantA); mesh(new THREE.CylinderGeometry(0.16, 0.12, 0.34, 20), M('#d8cfc0'), 0, 0.17, 0, plantA);
for (let i = 0; i < 9; i++) { const l = mesh(new THREE.SphereGeometry(0.12, 12, 8), M('#4f8a45', { roughness: 0.9 }), Math.cos(i) * 0.12, 0.5 + (i % 3) * 0.16, Math.sin(i) * 0.12, plantA); l.scale.set(1, 1.6, 0.4); l.rotation.y = i; }

// ноутбук (как в рилсе 98)
const lap = new THREE.Group(); lap.position.set(1.22, 0.783, -1.52); setA.add(lap);
const alu = M('#a3a8b0', { metalness: 0.6, roughness: 0.35 });
mesh(roundBox(0.34, 0.016, 0.23, 0.006), alu, 0, 0.008, 0, lap);
mesh(new THREE.PlaneGeometry(0.29, 0.1), M('#2b2d31', { roughness: 0.7 }), 0, 0.0165, 0.02, lap).rotation.x = -Math.PI / 2;
const hinge = new THREE.Group(); hinge.position.set(0, 0.016, -0.112); lap.add(hinge);
mesh(roundBox(0.34, 0.225, 0.009, 0.006), alu, 0, 0.1125, -0.002, hinge);
const tgCan = document.createElement('canvas'); tgCan.width = 1280; tgCan.height = 800;
const tgTex = new THREE.CanvasTexture(tgCan); tgTex.colorSpace = THREE.SRGBColorSpace; tgTex.anisotropy = 8;
const scr = new THREE.Mesh(new THREE.PlaneGeometry(0.312, 0.195), new THREE.MeshBasicMaterial({ map: tgTex, toneMapped: false })); scr.position.set(0, 0.1125, 0.0035); hinge.add(scr);
const avatar = new Image(); avatar.src = 'tg_avatar.png';

// ---------- кухня (K): столешница, гора кружек, часы с красной меткой, носки ----------
const counter = new THREE.Group(); counter.position.set(0, 0, -1.95); setK.add(counter);
mesh(roundBox(2.6, 0.86, 0.62, 0.02), M('#7d9a8c', { roughness: 0.7 }), 0, 0.43, 0, counter);
mesh(roundBox(2.64, 0.04, 0.66, 0.01), M('#efe6d6', { roughness: 0.4 }), 0, 0.88, 0, counter);
mesh(new THREE.BoxGeometry(0.6, 0.02, 0.42), M('#8a9298', { metalness: 0.7, roughness: 0.3 }), 0.2, 0.895, 0.02, counter);
const tap = mesh(new THREE.TorusGeometry(0.1, 0.012, 8, 20, Math.PI), M('#b8bec4', { metalness: 0.9, roughness: 0.2 }), 0.2, 1.0, -0.2, counter);
for (let k = 0; k < 4; k++) mesh(roundBox(0.55, 0.6, 0.32, 0.02), M('#9bb5a8', { roughness: 0.7 }), -0.9 + k * 0.6, 1.95, -0.14, counter);
const MUGC = ['#e4572e', '#f2c14e', '#2a7de1', '#f1f1f1', '#7aa86a', '#d94f70', '#6c3fa0', '#e9c46a'];
const mugs = []; let mk = 0;
for (let lvl = 0; lvl < 6; lvl++) { const n = 4 - Math.floor(lvl * 0.6); for (let i = 0; i < n; i++) { const mg = new THREE.Group(); const c = MUGC[mk++ % MUGC.length];
  mesh(new THREE.CylinderGeometry(0.045, 0.04, 0.1, 20), M(c, { roughness: 0.35 }), 0, 0.05, 0, mg); mesh(new THREE.TorusGeometry(0.028, 0.008, 8, 16), M(c, { roughness: 0.35 }), 0.048, 0.055, 0, mg);
  mg.position.set(0.35 + (i - (n - 1) / 2) * 0.1 + (rng() - 0.5) * 0.02, 0.9 + lvl * 0.1, 0.02 + (rng() - 0.5) * 0.08); mg.rotation.set((rng() - 0.5) * 0.3, rng() * 6, (rng() - 0.5) * 0.3); counter.add(mg); mugs.push(mg); } }
const clockCan = document.createElement('canvas'); clockCan.width = clockCan.height = 512; const clockTex = new THREE.CanvasTexture(clockCan); clockTex.colorSpace = THREE.SRGBColorSpace;
function drawClock(min) { const g = clockCan.getContext('2d'); g.fillStyle = '#fbf8f0'; g.fillRect(0, 0, 512, 512); g.save(); g.translate(256, 256);
  g.fillStyle = 'rgba(230,40,40,0.85)'; g.beginPath(); g.moveTo(0, 0); g.arc(0, 0, 230, -Math.PI / 2 - 0.05, -Math.PI / 2 + 0.5); g.fill();
  g.fillStyle = '#e62828'; g.beginPath(); g.arc(0, -205, 22, 0, 7); g.fill();
  g.fillStyle = '#222'; for (let k = 0; k < 12; k++) { g.save(); g.rotate(k * Math.PI / 6); g.fillRect(-6, -235, 12, 40); g.restore(); }
  const hand = (a, l, w) => { g.save(); g.rotate(a); g.fillRect(-w / 2, -l, w, l + 20); g.restore(); };
  hand((11 + min / 60) / 12 * Math.PI * 2, 130, 18); hand(min / 60 * Math.PI * 2, 200, 10); g.fillStyle = '#e62828'; g.beginPath(); g.arc(0, 0, 14, 0, 7); g.fill(); g.restore(); clockTex.needsUpdate = true; }
const clock = new THREE.Group(); clock.position.set(-0.35, 1.75, -2.27); setK.add(clock);
mesh(new THREE.CylinderGeometry(0.26, 0.26, 0.05, 48), M('#2d2a28'), 0, 0, 0, clock).rotation.x = Math.PI / 2;
mesh(new THREE.CircleGeometry(0.23, 48), new THREE.MeshStandardMaterial({ map: clockTex, roughness: 0.5 }), 0, 0, 0.027, clock);
const SOCKC = ['#e4572e', '#2a7de1', '#f2c14e', '#7aa86a', '#d94f70', '#f1f1f1', '#6c3fa0', '#2b2b2b'];
const socks = [];
for (let i = 0; i < 12; i++) { const sk = new THREE.Group(); const c = M(SOCKC[i % 8], { roughness: 0.95 });
  const s1 = mesh(new THREE.CapsuleGeometry(0.03, 0.13, 6, 12), c, 0, 0, 0, sk); s1.rotation.x = Math.PI / 2; const s2 = mesh(new THREE.CapsuleGeometry(0.03, 0.06, 6, 12), c, 0, 0, 0.085, sk); s2.position.set(0.04, 0, 0.09); s2.rotation.set(Math.PI / 2, 0, -1.2);
  sk.scale.y = 0.55; counter.add(sk); socks.push({ g: sk, i }); }
const sockPos = (i, moved) => { const pile = moved ? -0.15 : -0.55; const k = moved ? i : i; return [pile + ((k % 3) - 1) * 0.12, 0.915 + Math.floor(k / 3) * 0.025, 0.05 + ((k * 7) % 3 - 1) * 0.06]; };
const kLamp = mesh(new THREE.SphereGeometry(0.15, 24, 12, 0, Math.PI * 2, Math.PI * 0.45, Math.PI * 0.55), glowM('#ffd9a0', 0.6), 0.2, 2.35, -1.0, setK); kLamp.material.side = THREE.DoubleSide;
windowOn(setK, -2.58, 1.6, -1.0, Math.PI / 2, '#f0a878');

// ---------- спальня (B): кровать, ночь, окно с луной ----------
const bed = new THREE.Group(); bed.position.set(0, 0, -0.25); setB.add(bed);
mesh(roundBox(1.1, 0.3, 2.1, 0.03), woodM, 0, 0.18, 0, bed); mesh(roundBox(1.04, 0.16, 2.0, 0.07), M('#e8e4dc', { roughness: 0.95 }), 0, 0.4, 0.02, bed);
mesh(roundBox(1.1, 0.8, 0.07, 0.02), woodM, 0, 0.55, -1.05, bed); const pillow = mesh(roundBox(0.6, 0.12, 0.34, 0.06), M('#efe8da', { roughness: 0.95 }), 0, 0.53, -0.82, bed);
const blanket = mesh(roundBox(1.08, 0.12, 1.35, 0.06), M('#3f5f8a', { roughness: 0.95 }), 0, 0.53, 0.36, bed);
windowOn(setB, -2.58, 1.6, -0.6, Math.PI / 2, '#22345a');
const nstand = mesh(roundBox(0.4, 0.5, 0.4, 0.02), woodM, 0.8, 0.25, -1.0, setB);

// ---------- Дима: сидящий (кресло, стол) и стоящий (кухня, кровать) ----------
const DLOOK = { cloth: '#c79a3b', hair: '#3a2618', pants: '#2c3a55', face: { iris: '#5a7a4a', lid: 0.24 } };
const dS = makePerson({ ...DLOOK, seated: true }); scene.add(dS.root);
{ const pm = M('#2c3a55', { roughness: 0.9 });
  for (const sx of [-1, 1]) { const th = new THREE.CatmullRomCurve3([new THREE.Vector3(sx * 0.09, 0.5, 0.0), new THREE.Vector3(sx * 0.1, 0.5, 0.22), new THREE.Vector3(sx * 0.1, 0.49, 0.42)]);
    mesh(new THREE.TubeGeometry(th, 16, 0.075, 12, false), pm, 0, 0, 0, dS.root); mesh(new THREE.SphereGeometry(0.075, 16, 12), pm, sx * 0.1, 0.49, 0.42, dS.root);
    mesh(roundedLathe(0.065, 0.06, 0.44, 0.03), pm, sx * 0.1, 0.27, 0.45, dS.root); mesh(roundBox(0.12, 0.07, 0.24, 0.03), M('#222'), sx * 0.1, 0.035, 0.52, dS.root); } }
const dU = makePerson(DLOOK); scene.add(dU.root);
const DIMAS = [dS, dU];
for (const p of DIMAS) { p.baseY = p.torso.position.y; }
const standing = (p) => { for (const a of p.arms) { a.elbow.set(a.sx * 0.24, 0.22, 0.03); a.wrist.set(a.sx * 0.22, -0.02, 0.08); } };
// телефон Димы (в руках, дочерний к торсу) и телефон, который уносит кот
const feedCan = document.createElement('canvas'); feedCan.width = 256; feedCan.height = 512; const feedTex = new THREE.CanvasTexture(feedCan); feedTex.colorSpace = THREE.SRGBColorSpace;
function drawFeed(sc) { const g = feedCan.getContext('2d'); g.fillStyle = '#101418'; g.fillRect(0, 0, 256, 512); const C = ['#e4572e', '#f2c14e', '#2ea6ff', '#d94f70', '#7aa86a', '#9b6cf0'];
  for (let i = -1; i < 6; i++) { const y = i * 150 - (sc % 150); g.fillStyle = C[(i + Math.floor(sc / 150) + 6) % 6]; g.fillRect(14, y + 10, 228, 100); g.fillStyle = '#3a4450'; g.fillRect(14, y + 118, 160, 10); } feedTex.needsUpdate = true; }
function makePhone() { const g = new THREE.Group(); mesh(roundBox(0.075, 0.15, 0.009, 0.008), M('#1b1d22', { roughness: 0.3 }), 0, 0, 0, g);
  const s = new THREE.Mesh(new THREE.PlaneGeometry(0.066, 0.138), new THREE.MeshBasicMaterial({ map: feedTex, toneMapped: false })); s.position.z = 0.0048; g.add(s); return g; }
const phoneD = makePhone(); scene.add(phoneD);
const phoneC = makePhone(); setA.add(phoneC); const strap = new THREE.Mesh(new THREE.BufferGeometry(), M('#e9c46a', { roughness: 0.8 })); strap.castShadow = true; scene.add(strap);
const mug = new THREE.Group(); mesh(new THREE.CylinderGeometry(0.045, 0.04, 0.1, 20), M('#2a7de1', { roughness: 0.35 }), 0, 0, 0, mug); scene.add(mug);
const cat = makeCat(); scene.add(cat.g); const CS = 1.3;

// ---------- экран: документ и Телеграм (как в рилсе 98, без подмигивания аватара) ----------
function star4(g, x, y, r, a) { g.save(); g.globalAlpha = a; g.fillStyle = '#ffd34d'; g.beginPath(); for (let k = 0; k < 8; k++) { const an = k * Math.PI / 4 - Math.PI / 2, rr = k % 2 ? r * 0.28 : r; g.lineTo(x + Math.cos(an) * rr, y + Math.sin(an) * rr); } g.fill(); g.restore(); }
function pawPrint(g, x, y, s, a, rot) { g.save(); g.globalAlpha = a; g.translate(x, y); g.rotate(rot); g.fillStyle = '#e0453a'; g.beginPath(); g.ellipse(0, 6 * s, 11 * s, 9 * s, 0, 0, 7); g.fill();
  for (const [dx, dy] of [[-11, -6], [-4, -12], [4, -12], [11, -6]]) { g.beginPath(); g.ellipse(dx * s, dy * s, 4 * s, 5 * s, 0, 0, 7); g.fill(); } g.restore(); }
function rrect(g, x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
function drawDoc(lines) { const g = tgCan.getContext('2d'); g.fillStyle = '#dfe3e8'; g.fillRect(0, 0, 1280, 800); g.fillStyle = '#fff'; g.fillRect(260, 40, 760, 760);
  g.fillStyle = '#1f2a36'; g.font = '800 44px Onest'; g.fillText('План проекта', 320, 130); g.fillStyle = '#9aa4ae';
  for (let k = 0; k < 13; k++) { const w = k === Math.floor(lines) ? 600 * (lines % 1) : (k < lines ? 560 - (k * 97 % 200) : 0); if (w > 0) { rrect(g, 320, 180 + k * 44, w, 16, 8); g.fill(); } }
  if (Math.floor(lines * 6) % 2 === 0) { g.fillStyle = '#2ea6ff'; g.fillRect(325 + (600 * (lines % 1)), 172 + Math.floor(lines) * 44, 5, 32); } tgTex.needsUpdate = true; }
const POSTS = ['Это не лень', 'Две минуты — и пошло', 'Посиди со мной', 'Вечер без ленты', 'Дофаминовое меню', 'Гиперфокус'];
const BTN = { x: 70, y: 560, w: 440, h: 104 };
function drawTG(t, st) {
  const g = tgCan.getContext('2d'), W = 1280, H = 800;
  g.fillStyle = '#0e1621'; g.fillRect(0, 0, W, H);
  g.fillStyle = '#17212b'; g.fillRect(0, 0, W, 64); g.fillStyle = '#6c7883'; g.font = '600 28px Onest'; g.fillText('Telegram', 30, 42);
  g.save(); g.beginPath(); g.rect(560, 64, 720, H - 64); g.clip();
  for (let i = 0; i < 9; i++) { const y = 100 + i * 190 - st.scroll; const P = POSTS[i % POSTS.length];
    g.fillStyle = '#182533'; rrect(g, 590, y, 650, 165, 22); g.fill();
    if (avatar.complete) { g.save(); g.beginPath(); g.arc(640, y + 50, 30, 0, 7); g.clip(); g.drawImage(avatar, 610, y + 20, 60, 60); g.restore(); }
    g.fillStyle = '#ffffff'; g.font = '700 32px Onest'; g.fillText(P, 690, y + 62);
    g.fillStyle = '#3a4b5c'; for (let k = 0; k < 2; k++) { rrect(g, 615, y + 95 + k * 28, 560 - k * 160, 14, 7); g.fill(); } }
  g.restore();
  const pulse = 1 + Math.sin(t * 4) * 0.015;
  g.save(); g.translate(290, 250); g.scale(pulse, pulse); g.beginPath(); g.arc(0, 0, 130, 0, 7); g.fillStyle = '#f4f1ea'; g.fill(); g.clip();
  const al = st.alive || 0, hop = al > 0 && al < 1 ? Math.abs(Math.sin(al * Math.PI * 3)) * (1 - al) : 0;
  g.translate(0, -hop * 30); g.scale(1 + hop * 0.06, 1 - hop * 0.06);
  if (avatar.complete) g.drawImage(avatar, -130, -130, 260, 260);
  if (al > 0 && al < 1) { g.save(); g.translate(-78, 30); g.rotate(-0.6 + Math.sin(al * 20) * 0.6); g.fillStyle = '#2f2d33'; g.beginPath(); g.ellipse(0, -26, 14, 26, 0, 0, 7); g.fill(); g.fillStyle = '#e8875a'; g.beginPath(); g.arc(0, -44, 6, 0, 7); g.fill(); g.restore(); }
  g.restore();
  g.lineWidth = 6; g.strokeStyle = '#2ea6ff'; g.beginPath(); g.arc(290, 250, 136, 0, 7); g.stroke();
  for (const [x, y, ph] of [[150, 140, 0], [440, 150, 1.7], [455, 330, 3.1], [130, 340, 4.4], [300, 95, 2.4]]) star4(g, x, y, 22 + 8 * Math.sin(t * 5 + ph), 0.5 + 0.5 * Math.sin(t * 5 + ph));
  g.textAlign = 'center'; g.fillStyle = '#fff'; g.font = '800 48px Onest'; g.fillText('СДВГ | Напарник', 290, 448);
  pawPrint(g, 520, 425, 1.0, 1, 0.3);
  g.fillStyle = '#5eb5f7'; g.font = '600 32px Onest'; g.fillText('t.me/ru_adhd', 290, 500);
  const sub = st.sub;
  if (st.hideBtn) { g.fillStyle = 'rgba(0,0,0,0.35)'; rrect(g, BTN.x, BTN.y, BTN.w, BTN.h, 30); g.fill(); } else {
    g.save(); g.translate(BTN.x + BTN.w / 2, BTN.y + BTN.h / 2);
    g.fillStyle = sub ? '#4fae4e' : '#2ea6ff'; rrect(g, -BTN.w / 2, -BTN.h / 2, BTN.w, BTN.h, 30); g.fill();
    g.fillStyle = 'rgba(255,255,255,0.18)'; rrect(g, -BTN.w / 2 + 8, -BTN.h / 2 + 6, BTN.w - 16, BTN.h * 0.42, 24); g.fill();
    g.fillStyle = '#fff'; g.font = '800 44px Onest'; g.fillText(sub ? '✓ ВЫ ПОДПИСАНЫ' : 'ПОДПИСАТЬСЯ', 0, 15); g.restore(); }
  if (st.ripple > 0 && st.ripple < 1) { g.strokeStyle = `rgba(255,255,255,${1 - st.ripple})`; g.lineWidth = 10; g.beginPath(); g.arc(BTN.x + 150, BTN.y + 60, 30 + st.ripple * 260, 0, 7); g.stroke(); }
  const trail = [[1180, 760, -0.9], [1060, 730, -1.2], [940, 720, -1.4], [820, 700, -1.5], [700, 690, -1.6], [600, 650, -1.7]];
  trail.forEach(([x, y, r], k) => { const a = Math.max(0, Math.min(1, st.paws * trail.length - k)); if (a > 0) pawPrint(g, x, y, 1.3, a, r); });
  g.textAlign = 'left'; tgTex.needsUpdate = true;
}
const btnCan = document.createElement('canvas'); btnCan.width = 512; btnCan.height = 128; const btnTex = new THREE.CanvasTexture(btnCan); btnTex.colorSpace = THREE.SRGBColorSpace;
function drawBtn(sub) { const g = btnCan.getContext('2d'); g.clearRect(0, 0, 512, 128); g.fillStyle = sub ? '#4fae4e' : '#2ea6ff'; rrect(g, 4, 4, 504, 120, 40); g.fill();
  g.fillStyle = 'rgba(255,255,255,0.22)'; rrect(g, 14, 10, 484, 50, 30); g.fill(); g.fillStyle = '#fff'; g.font = '800 54px Onest'; g.textAlign = 'center'; g.fillText(sub ? '✓ ВЫ ПОДПИСАНЫ' : 'ПОДПИСАТЬСЯ', 256, 84); g.textAlign = 'left'; btnTex.needsUpdate = true; }
const btn3 = new THREE.Group(); scr.add(btn3); btn3.visible = false;
mesh(roundBox(0.106, 0.026, 0.008, 0.004), M('#1f86d6', { roughness: 0.4 }), 0, 0, 0, btn3);
const btnFace = new THREE.Mesh(new THREE.PlaneGeometry(0.104, 0.026), new THREE.MeshBasicMaterial({ map: btnTex, transparent: true, toneMapped: false })); btnFace.position.z = 0.0045; btn3.add(btnFace);
const BTN_LOCAL = new THREE.Vector3(-0.0853, -0.0517, 0);
const pawCan = document.createElement('canvas'); pawCan.width = pawCan.height = 128; pawPrint(pawCan.getContext('2d'), 64, 70, 3.2, 1, 0); const pawTex = new THREE.CanvasTexture(pawCan); pawTex.colorSpace = THREE.SRGBColorSpace;
const tablePaws = []; const PAW_PATH = [[0.86, 0.78, -1.36], [0.93, 0.78, -1.42], [0.99, 0.78, -1.35], [1.05, 0.78, -1.41], [1.1, 0.78, -1.34]];
PAW_PATH.forEach((p, k) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(0.04, 0.04), new THREE.MeshBasicMaterial({ map: pawTex, transparent: true, depthWrite: false, toneMapped: false })); m.rotation.x = -Math.PI / 2; m.rotation.z = 1.5 + k * 0.1; m.position.set(...p); m.position.y += 0.0015; m.visible = false; scene.add(m); tablePaws.push(m); });

// ---------- свет превью three.js (в Blender — свой, по настроению плана) ----------
const hemi = new THREE.HemisphereLight('#fff1d8', '#5b3e2a', 0.8); scene.add(hemi);
const key = new THREE.DirectionalLight('#fff4e0', 2.2); key.position.set(-2, 4, 3); scene.add(key, key.target);
const fill = new THREE.PointLight('#fff2e2', 1.6, 4, 1.5); camera.add(fill); fill.position.set(0.1, 0.15, 0.1); scene.add(camera);
const composer = new EffectComposer(renderer); composer.addPass(new RenderPass(scene, camera)); composer.addPass(new OutputPass());

// ---------- время ----------
const V = window.VOICE; const FPS = 30;
const cl = (x) => Math.max(0, Math.min(1, x));
const ease = (x) => { x = cl(x); return x * x * (3 - 2 * x); };
const eout = (x) => { x = cl(x); return 1 - Math.pow(1 - x, 3); };
const back2 = (x) => { x = cl(x); const c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
const mouthOf = (t) => { const m = V.mouth.dima, i = t * FPS, a = Math.floor(i); return (m[a] || 0) * (1 - (i - a)) + (m[a + 1] || 0) * (i - a); };
const blinkAt = (t, times) => { for (const b of times) { const d = (t - b) / 0.15; if (d >= 0 && d <= 1) return Math.sin(d * Math.PI); } return 0; };
const v3 = (a) => new THREE.Vector3(...a);
const LN = V.lines; const WT = (li, wi) => LN[li].words[wi].start;
const T_END = LN[7].end + 0.12;
const CLICK = WT(4, 0) + 0.04;             // «Вот» — щелчок лампы
const TAP = WT(7, 8);                       // «вернуть» — кот жмёт кнопку
const OPEN = LN[7].start - 0.05;            // Дима открывает ноутбук
const CAT_JUMP = WT(7, 1) - 0.1;            // кот запрыгивает на стол
const POP = WT(7, 4);                       // кнопка выпрыгивает
// планы: set — где, mood — свет в Blender
const SHOTS = [
  { t0: 0, t1: WT(0, 6) - 0.06, set: 'A', p: [-0.28, 1.2, 0.32], l: [-0.86, 1.0, -1.12], fov: 34, hook: true, push: 0.06, mood: 'warm', dima: 'arm' },
  { t0: WT(0, 6) - 0.06, t1: LN[1].start - 0.08, set: 'A', p: [-0.25, 1.08, 0.05], l: [-0.86, 1.0, -1.15], fov: 34, push: 0.1, mood: 'warm', dima: 'arm' },
  { t0: LN[1].start - 0.08, t1: WT(1, 5) - 0.04, set: 'A', p: [2.15, 1.35, -2.15], l: [1.25, 0.9, -1.0], fov: 36, push: 0.08, mood: 'eve1', dima: 'desk' },
  { t0: WT(1, 5) - 0.04, t1: LN[2].start - 0.08, set: 'A', p: [2.25, 1.05, -2.1], l: [1.3, 0.95, -1.15], fov: 32, push: 0.12, mood: 'eve1', dima: 'desk' },
  { t0: LN[2].start - 0.08, t1: WT(2, 7) - 0.04, set: 'K', p: [11.9, 1.55, 0.4], l: [10.15, 1.2, -1.65], fov: 38, push: 0.08, mood: 'eve2', dima: 'sink' },
  { t0: WT(2, 7) - 0.04, t1: LN[3].start - 0.08, set: 'K', p: [8.2, 1.5, 0.6], l: [9.75, 1.05, -1.55], fov: 40, push: 0.12, mood: 'eve2', dima: 'socks' },
  { t0: LN[3].start - 0.08, t1: WT(3, 4) - 0.04, set: 'B', p: [21.0, 1.75, 1.25], l: [20.0, 0.55, -0.45], fov: 34, push: 0.08, mood: 'night', dima: 'bed' },
  { t0: WT(3, 4) - 0.04, t1: LN[4].start - 0.12, set: 'B', p: [20.9, 1.45, -0.3], l: [20.0, 0.62, -0.75], fov: 34, push: 0.1, mood: 'night', dima: 'bed' },
  { t0: LN[4].start - 0.12, t1: LN[5].start - 0.08, set: 'A', p: [2.35, 1.32, -2.1], l: [1.32, 1.0, -1.05], fov: 34, push: 0.1, mood: 'click', dima: 'desk' },
  { t0: LN[5].start - 0.08, t1: WT(5, 5) - 0.04, set: 'A', p: [2.55, 1.2, -0.55], l: [1.7, 0.88, -1.5], fov: 34, push: 0.1, mood: 'warm', dima: 'desk' },
  { t0: WT(5, 5) - 0.04, t1: LN[6].start - 0.08, set: 'A', p: [1.7, 0.55, 0.6], l: [2.55, 0.25, -0.75], fov: 40, push: 0.06, mood: 'warm', dima: 'desk' },
  { t0: LN[6].start - 0.08, t1: WT(6, 5) - 0.04, set: 'A', p: [2.3, 1.3, -2.12], l: [1.3, 1.0, -1.05], fov: 34, push: 0.1, mood: 'warm', dima: 'desk', typing: true },
  { t0: WT(6, 5) - 0.04, t1: LN[7].start - 0.08, set: 'A', p: [-0.85, 1.05, 0.75], l: [-1.95, 0.75, -0.3], fov: 34, push: 0.1, mood: 'warm', dima: 'desk' },
  { t0: LN[7].start - 0.08, t1: WT(7, 5) - 0.04, set: 'A', p: [2.15, 1.45, -0.5], l: [1.1, 0.88, -1.55], fov: 34, push: 0.08, mood: 'warm', dima: 'desk', cta: true },
  { t0: WT(7, 5) - 0.04, t1: WT(7, 7) - 0.04, set: 'A', p: [2.45, 1.22, -1.22], l: [1.35, 1.0, -1.25], fov: 34, push: 0.06, mood: 'warm', dima: 'desk', cta: true, face: true },
  { t0: WT(7, 7) - 0.04, t1: T_END + 0.05, set: 'A', p: [2.15, 1.45, -0.5], l: [1.1, 0.88, -1.55], fov: 34, push: 0.14, mood: 'warm', dima: 'desk', cta: true },
  { t0: T_END + 0.05, t1: 99, set: 'A', p: [-0.28, 1.2, 0.32], l: [-0.86, 1.0, -1.12], fov: 34, push: 0.03, mood: 'warm', dima: 'arm', loop: true },
];
// свет Blender по настроению (координаты three.js; X — сдвиг набора)
const X = { A: 0, K: 10, B: 20 };
function lightsFor(sh, t) {
  const x = X[sh.set]; let mood = sh.mood; if (mood === 'click') mood = t < CLICK ? 'dusk' : 'warm';
  const L = []; const A = (p, a, e, c, s) => L.push({ k: 'AREA', p, a, e, c, s }); const P = (p, e, c) => L.push({ k: 'POINT', p, e, c });
  let cam = { e: 32, c: [1, 0.88, 0.75], s: 1.4 }, world = [1, 0.86, 0.68, 0.2], exp = -0.8;
  if (mood === 'warm') {
    L.push({ k: 'SUN', p: [x - 2, 4, 3], a: [x, 0.8, -1], e: 3.2, c: [1, 0.9, 0.75], s: 6 });
    A([x - 2.2, 1.6, -1.1], [x + 0.5, 1, -1], 160, [1, 0.85, 0.62], 1.2); A([x, 2.7, -0.9], [x, 0, -0.9], 200, [1, 0.86, 0.66], 2.2);
    P([x - 1.75, 1.45, -1.75], 25, [1, 0.75, 0.45]); if (sh.dima === 'desk' && t > CLICK - 0.5) P([0.7, 1.08, -1.74], 18, [1, 0.8, 0.5]);
  } else if (mood === 'eve1') {
    L.push({ k: 'SUN', p: [x - 4, 1.8, 0], a: [x, 0.9, -1.4], e: 2.2, c: [1, 0.6, 0.33], s: 4 });
    A([x - 2.2, 1.6, -1.1], [x + 1, 1, -1.5], 110, [1, 0.6, 0.35], 1.2); A([1.25, 1.0, -1.35], [1.3, 1.15, -1.0], 1.5, [0.75, 0.85, 1], 0.25);
    cam = { e: 40, c: [1, 0.78, 0.58], s: 1.4 }; world = [1, 0.7, 0.5, 0.12]; exp = -0.55;
  } else if (mood === 'dusk') {
    L.push({ k: 'SUN', p: [x - 4, 1.2, 0], a: [x, 0.9, -1.4], e: 0.8, c: [1, 0.5, 0.3], s: 4 });
    A([x - 2.2, 1.6, -1.1], [x + 1, 1, -1.5], 40, [0.75, 0.6, 0.85], 1.2); A([1.25, 1.0, -1.35], [1.3, 1.15, -1.0], 6, [0.75, 0.85, 1], 0.25);
    cam = { e: 35, c: [0.95, 0.8, 0.75], s: 1.4 }; world = [0.6, 0.55, 0.7, 0.06]; exp = -0.45;
  } else if (mood === 'eve2') {
    L.push({ k: 'SUN', p: [x - 4, 1.5, 0.5], a: [x, 0.9, -1.4], e: 1.4, c: [1, 0.55, 0.3], s: 4 });
    A([x + 0.2, 2.6, -1.0], [x + 0.2, 0, -1.0], 110, [1, 0.8, 0.55], 1.0);
    cam = { e: 55, c: [1, 0.8, 0.62], s: 1.4 }; world = [1, 0.7, 0.5, 0.08]; exp = -0.55;
  } else if (mood === 'night') {
    A([x - 2.4, 1.6, -0.6], [x, 0.6, -0.4], 45, [0.5, 0.62, 1], 1.2);
    const ph = phoneD.getWorldPosition(new THREE.Vector3()); A([ph.x, ph.y + 0.02, ph.z], [ph.x, ph.y - 0.3, ph.z - 0.25], 2.5, [0.72, 0.85, 1], 0.08);
    cam = { e: 10, c: [0.65, 0.72, 1], s: 1.4 }; world = [0.25, 0.3, 0.5, 0.04]; exp = -0.35;
  }
  return { lights: L, camf: cam, world, exp };
}
window.duration = V.total;
const blinks = [1.3, 3.9, 6.0, 9.6, 12.9, 16.0, 19.4, 22.2, 25.0, 29.4];
const toLocal = (obj, w) => obj.worldToLocal(w.clone());
const angLerp = (a, b, k) => { let d = b - a; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; return a + d * k; };
const yawTo = (from, x, z) => Math.atan2(x - from.x, z - from.z);
const lids = (v) => { for (const e of cat.eyes) { e.lid.rotation.x = -1.4 + v; e.p.visible = e.hl.visible = v < 2.5; } };
let lastSh = null;
window.renderFrame = (t) => {
  const si = SHOTS.findIndex((s) => t >= s.t0 && t < s.t1); const sh = SHOTS[si < 0 ? SHOTS.length - 1 : si]; lastSh = sh;
  const u = (t - sh.t0) / Math.max(0.01, sh.t1 - sh.t0);
  // камера (до поз: Дима поворачивается к камере этого кадра)
  const Pp = v3(sh.p), Lk = v3(sh.l); const dir = Pp.clone().sub(Lk);
  let k = 1 - (sh.push || 0) * ease(u); let roll = 0, fov = sh.fov || 34;
  if (sh.hook) { const hit = WT(0, 1) + 0.12; const f = eout(t / 0.22); k *= 1.45 - 0.45 * f + (t > 0.22 && t < 0.5 ? -0.06 * Math.sin((t - 0.22) / 0.28 * Math.PI) : 0);
    roll = (1 - f) * 0.065 - (t > 0.22 ? Math.sin((t - 0.22) / 0.3 * Math.PI) * 0.012 * Math.exp(-(t - 0.22) * 4) : 0); k *= 1 - 0.09 * Math.max(0, 1 - Math.abs(t - hit) / 0.12); fov *= 1 + 0.35 * (1 - f); }
  if (sh.loop) k *= 1 + 0.15 * (1 - eout((t - sh.t0) / 0.3));
  camera.position.copy(Lk).addScaledVector(dir, k);
  const shake = (t0, a) => (t > t0 ? Math.exp(-(t - t0) * 9) * a : 0); const sa = shake(CLICK, 0.012) + shake(TAP, 0.01) + (sh.hook ? shake(WT(0, 1) + 0.12, 0.012) : 0);
  camera.position.x += Math.sin(t * 1.3) * 0.003 + Math.sin(t * 61) * sa; camera.position.y += Math.sin(t * 1.7 + 1) * 0.002 + Math.cos(t * 53) * sa;
  camera.fov = fov; camera.updateProjectionMatrix(); camera.lookAt(Lk); camera.rotateZ(roll);
  for (const [k, s] of Object.entries(SETS)) s.visible = k === sh.set;
  const md = sh.dima; const P = (md === 'arm' || md === 'desk') ? dS : dU; dS.root.visible = P === dS; dU.root.visible = P === dU;
  phoneD.visible = false; mug.visible = false; strap.visible = false; phoneC.visible = sh.set === 'A' && t < LN[6].start - 0.2;
  // ----- Дима: поза по месту -----
  const s = P.face.st; s.mouth = mouthOf(t); s.blink = blinkAt(t, blinks); s.look = [0, 0]; s.brow = 0; s.frown = 0; s.smile = 0.3; s.eyesWide = 0; s.round = 0; s.sleepy = 0;
  standing(P); P.torso.position.y = P.baseY + Math.sin(t * 2.4) * 0.004; P.torso.rotation.set(0, 0, Math.sin(t * 1.1) * 0.01);
  P.root.rotation.set(0, 0, 0); P.root.position.y = 0;
  P.headPivot.rotation.set(Math.sin(t * 7.3) * 0.03 * s.mouth - 0.02, Math.sin(t * 0.9) * 0.04, Math.sin(t * 1.3) * 0.02);
  const camLook = (k = 1, max = 0.9) => { const d = angLerp(0, yawTo(P.root.position, camera.position.x, camera.position.z) - P.root.rotation.y, 1); P.headPivot.rotation.y += Math.max(-max, Math.min(max, d)) * k; };
  scene.updateMatrixWorld(true);
  if (md === 'arm') {
    P.root.position.copy(AC).add(new THREE.Vector3(Math.sin(ACR) * 0.06, 0, Math.cos(ACR) * 0.06)); P.root.rotation.y = ACR;
    s.smile = 0.6; s.sleepy = 0.12; s.brow = 0.25;
    const st = Math.sin(t * 2.6); const a = P.arms[0]; a.wrist.set(-0.02 + st * 0.05, 0.36, 0.3 + st * 0.05); a.elbow.set(-0.24, 0.22, 0.14);
    const b = P.arms[1]; b.wrist.set(0.31, 0.2, 0.28); b.elbow.set(0.3, 0.26, 0.04);
    P.torso.rotation.x = -0.08; P.headPivot.rotation.x -= 0.04;
  } else if (md === 'desk') {
    P.root.position.set(1.3, 0, -1.07); P.root.rotation.y = Math.PI;
    const typing = (t >= LN[5].start + 1.6 && t < LN[7].start - 0.1) || (t >= CLICK + 0.6 && t < LN[5].start);
    if (t < LN[2].start) { // листает телефон вместо дела
      s.smile = 0.1; s.sleepy = 0.3; s.look = [0, 0.75]; P.headPivot.rotation.x += 0.18; P.torso.rotation.x = 0.12;
      phoneD.visible = true; P.torso.add(phoneD); phoneD.position.set(0.0, 0.42, 0.3); phoneD.rotation.set(-0.9, 0, 0); drawFeed(t * 260);
      for (const a of P.arms) { a.wrist.set(a.sx * 0.05, 0.37, 0.27); a.elbow.set(a.sx * 0.24, 0.2, 0.12); }
      P.arms[1].wrist.y += Math.abs(Math.sin(t * 5)) * 0.015;
    } else if (t < CLICK + 0.6 && t >= LN[4].start - 0.2) { // «Вот что я поменял»: тянется к лампе, щелчок
      s.brow = 0.4; s.smile = 0.35; camLook(0.6);
      const k = ease((t - LN[4].start + 0.1) / 0.3) * (1 - ease((t - CLICK - 0.15) / 0.3)); const a = P.arms[1]; const lw = toLocal(P.torso, new THREE.Vector3(0.76, 0.8, -1.72));
      a.wrist.lerp(lw, k * 0.92); a.elbow.lerp(new THREE.Vector3(0.3, 0.32, 0.25), k);
      if (t > CLICK) { s.eyesWide = 0.4; s.smile = 0.6; }
    } else if (typing || sh.typing) {
      s.smile = 0.45; s.look = [0, 0.5]; P.headPivot.rotation.x += 0.12; if (sh.typing) camLook(0.25);
      for (const a of P.arms) { const ph = t * 14 + a.sx; a.wrist.set(a.sx * 0.11, 0.33 + Math.max(0, Math.sin(ph)) * 0.02, 0.45); a.elbow.set(a.sx * 0.25, 0.2, 0.2); }
    } else if (sh.cta) {
      s.smile = 0.55; s.brow = 0.35;
      if (t < OPEN + 0.6) { const k = ease((t - OPEN + 0.25) / 0.2) * (1 - ease((t - OPEN - 0.35) / 0.2)); for (const a of P.arms) { const w = toLocal(P.torso, hinge.localToWorld(new THREE.Vector3(a.sx * -0.1, 0.2, 0.02))); if (w.length() < 0.6) a.wrist.lerp(w, k); a.elbow.lerp(new THREE.Vector3(a.sx * 0.26, 0.28, 0.2), k); } }
      else { for (const a of P.arms) { a.wrist.set(a.sx * 0.12, 0.33, 0.42); a.elbow.set(a.sx * 0.25, 0.2, 0.2); } }
      const turn = ease((t - WT(7, 0)) / 0.4); P.root.rotation.y = angLerp(Math.PI, yawTo(P.root.position, camera.position.x, camera.position.z), turn * (sh.face ? 0.55 : 0.35)); camLook(turn * 0.9, 1.1);
      if (t > TAP) s.smile = 0.85;
    } else { s.smile = 0.4; for (const a of P.arms) { a.wrist.set(a.sx * 0.12, 0.33, 0.42); a.elbow.set(a.sx * 0.25, 0.2, 0.2); } }
  } else if (md === 'sink' || md === 'socks') {
    P.root.position.set(10.05, 0, -1.25); s.frown = 0.6; s.smile = -0.25; s.brow = 0.1; s.sleepy = 0.2;
    if (md === 'sink') { P.root.rotation.y = Math.PI - 1.2; camLook(0.8); mug.visible = true; P.torso.add(mug); mug.position.set(0.04, 0.08, 0.36); mug.rotation.set(Math.sin(t * 9) * 0.5, 0, 0.3);
      for (const a of P.arms) { a.wrist.set(a.sx * 0.06 + Math.sin(t * 9 + a.sx) * 0.02, 0.06, 0.36); a.elbow.set(a.sx * 0.24, 0.16, 0.16); } P.headPivot.rotation.x += 0.12; s.look = [0.3, 0.4]; }
    else { P.root.rotation.y = Math.PI + 1.0; camLook(0.6); s.look = [-0.2, 0.5]; P.headPivot.rotation.x += 0.1;
      for (const a of P.arms) { a.wrist.set(a.sx * 0.1, 0.1, 0.34); a.elbow.set(a.sx * 0.24, 0.18, 0.12); } }
  } else if (md === 'bed') {
    P.root.position.set(20, 0.6, 0.72); P.root.rotation.x = -Math.PI / 2; s.frown = 0.5; s.smile = -0.35; s.sleepy = 0.35; s.look = [0, 0]; s.brow = 0.15;
    phoneD.visible = true; P.torso.add(phoneD); phoneD.position.set(0.04, 0.26, 0.33); phoneD.rotation.set(0.35, Math.PI, 0); drawFeed(t * 140);
    for (const a of P.arms) { a.wrist.set(0.04 + a.sx * 0.05, 0.22, 0.3); a.elbow.set(a.sx * 0.27, 0.2, 0.05); }
    P.headPivot.rotation.set(0.05, 0, 0); if (t > WT(3, 4)) { s.frown = 0.8; s.sleepy = 0.45; }
  }
  // ----- кот (масштаб CS) -----
  cat.g.scale.set(CS, CS, CS); cat.setPaw(null); lids(blinkAt(t, [2.4, 8.7, 17.2, 22.9, 27.4]) * 2.9);
  cat.headPivot.rotation.set(0.05 + Math.sin(t * 1.1) * 0.03, Math.sin(t * 0.7) * 0.12, 0); cat.earR.rotation.x = 0.5; cat.g.visible = true;
  for (const e of cat.eyes) e.refl.visible = false;
  const onLap = (k) => { const lp = new THREE.Vector3(0.0, 0.53, 0.3); dS.root.updateMatrixWorld(true); const w = dS.root.localToWorld(lp); cat.g.position.copy(w); cat.g.rotation.set(0, ACR + 0.35, 0); };
  if (md === 'arm' && !sh.loop) { onLap(); const up = Math.sin(cl(t / 0.5) * Math.PI); cat.headPivot.rotation.set(-0.25 * up + 0.05, -0.5 * eout(t / 0.4) + 0.25, 0.15 * up);
    cat.earR.rotation.x = 0.5 + (t < 0.35 ? 0.45 : 0); lids(t > 0.6 && t < 3.2 ? 1.6 + Math.sin(t * 3) * 0.2 : 0); cat.g.position.y += Math.sin(t * 2.6) * 0.004; }
  else if (sh.loop) { const j = cl((t - sh.t0 - 0.15) / 0.5); onLap(); const end = cat.g.position.clone(); const from = end.clone().add(new THREE.Vector3(0.9, -0.5, 0.2));
    cat.g.position.copy(from.lerp(end, eout(j))); cat.g.position.y += Math.sin(j * Math.PI) * 0.25; const land = (t - sh.t0 - 0.65) / 0.22; const sq = land > 0 && land < 1 ? Math.sin(land * Math.PI) * 0.15 : 0;
    cat.g.scale.set(CS * (1 + sq * 0.5), CS * (1 - sq), CS * (1 + sq * 0.5)); lids(t > sh.t0 + 1.1 ? 1.6 : 0); cat.headPivot.rotation.set(0.05, j < 1 ? 0.4 : -0.2, 0); }
  else if (sh.set === 'A' && t >= LN[5].start - 0.1 && t < LN[5].start + 1.75) { // кот на столе у телефона: хватает ремешок
    cat.g.position.set(1.58, 0.76, -1.64); cat.g.rotation.set(0, Math.PI / 2 - 0.25, 0); const tg = LN[5].start;
    const bite = ease((t - tg - 0.1) / 0.3) * (1 - ease((t - tg - 0.75) / 0.3)); cat.headPivot.rotation.set(0.55 * bite, 0, 0);
    if (t > tg + 0.8) { cat.headPivot.rotation.set(-0.25, 0, 0); lids(1.4); const tr = ease((t - tg - 1.0) / 0.4); cat.g.rotation.y = Math.PI / 2 - 0.25 - tr * 0.6; }
    if (t > tg + 1.4) { const j = cl((t - tg - 1.4) / 0.35); cat.g.position.lerp(new THREE.Vector3(2.05, 0, -1.05), j); cat.g.position.y = 0.76 * (1 - j) + Math.sin(j * Math.PI) * 0.15; }
  } else if (sh.set === 'A' && t >= LN[5].start + 1.75 && t < LN[6].start) { // несёт телефон к двери
    const j = cl((t - LN[5].start - 1.75) / (LN[6].start - LN[5].start - 2.0)); const a = new THREE.Vector3(2.05, 0, -1.05), b = new THREE.Vector3(2.5, 0, -0.6), c = new THREE.Vector3(3.2, 0, -0.55);
    const pos = j < 0.6 ? a.clone().lerp(b, j / 0.6) : b.clone().lerp(c, (j - 0.6) / 0.4); cat.g.position.copy(pos); cat.g.position.y = Math.abs(Math.sin(t * 9)) * 0.02;
    cat.g.rotation.set(0, j < 0.6 ? Math.atan2(b.x - a.x, b.z - a.z) : Math.PI / 2, Math.sin(t * 9) * 0.04); cat.headPivot.rotation.set(-0.3, 0, 0); lids(1.35);
  } else if (sh.set === 'A' && t >= LN[6].start && t < CAT_JUMP) { // на диване, довольный
    cat.g.position.set(-1.95, 0.55, -0.3); cat.g.rotation.set(0, 0.9, 0); lids(2.2); cat.headPivot.rotation.set(0.1, 0.2, Math.sin(t * 1.5) * 0.06);
    cat.g.scale.set(CS, CS * (1 + Math.sin(t * 2.4) * 0.02), CS);
  } else if (sh.set === 'A' && t >= CAT_JUMP) { // запрыгивает на стол, жмёт кнопку
    const j = cl((t - CAT_JUMP) / 0.42); const from = new THREE.Vector3(0.5, 0, -0.95), to = new THREE.Vector3(0.85, 0.76, -1.5);
    const pos = from.clone().lerp(to, j); pos.y += Math.sin(j * Math.PI) * 0.22; cat.g.position.copy(pos); const land = (t - CAT_JUMP - 0.42) / 0.25; const sq = land > 0 && land < 1 ? Math.sin(land * Math.PI) * 0.18 : 0;
    cat.g.scale.set(CS * (1 + sq * 0.5), CS * (1 - sq), CS * (1 + sq * 0.5)); cat.g.rotation.set(0, Math.PI / 2 - 0.3, 0); lids(0);
    cat.headPivot.rotation.set(0.05, t < TAP + 0.4 ? 0.1 : 0.7, 0); if (t > TAP + 0.6) lids(1.5);
  } else cat.g.visible = false;
  cat.setTail(t);
  // телефон на столе / в зубах
  if (phoneC.visible) { const tg = LN[5].start; if (t < tg + 0.75 || sh.set !== 'A') { phoneC.position.set(1.84, 0.785, -1.45); phoneC.rotation.set(-Math.PI / 2, 0, 0.4); }
    else { scene.updateMatrixWorld(true); const m = cat.headPivot.localToWorld(new THREE.Vector3(0, -0.07, 0.1)); const sw = Math.sin(t * 9) * 0.02; const fw = new THREE.Vector3(Math.sin(cat.g.rotation.y), 0, Math.cos(cat.g.rotation.y)); const ph = m.clone().addScaledVector(fw, 0.12); ph.y = Math.max(cat.g.position.y + 0.11, m.y - 0.16); ph.x += sw;
      phoneC.position.copy(setA.worldToLocal(ph.clone())); phoneC.rotation.set(0, cat.g.rotation.y, sw * 3);
      const top = ph.clone().add(new THREE.Vector3(0, 0.075, 0)); const c = new THREE.CatmullRomCurve3([m, m.clone().lerp(top, 0.5).add(new THREE.Vector3(0.01, 0, 0.01)), top]);
      strap.geometry.dispose(); strap.geometry = new THREE.TubeGeometry(c, 12, 0.005, 6, false); strap.visible = true; } }
  if (phoneC.visible && !strap.visible) { const p0 = phoneC.localToWorld(new THREE.Vector3(0.03, 0.075, 0)); const c = new THREE.CatmullRomCurve3([p0, p0.clone().add(new THREE.Vector3(0.05, 0.003, 0.03)), p0.clone().add(new THREE.Vector3(0.1, 0.003, -0.02))]);
    scene.updateMatrixWorld(true); strap.geometry.dispose(); strap.geometry = new THREE.TubeGeometry(c, 12, 0.005, 6, false); strap.visible = true; }
  // ноутбук: документ, потом канал
  const op = t < OPEN ? 1 : back2((t - OPEN) / 0.5); const closed = t >= LN[6].start + 2.3 && t < OPEN;
  hinge.rotation.x = (t >= OPEN - 0.25 && t < OPEN) ? Math.PI / 2 * 0.75 : (t >= OPEN ? Math.PI / 2 * 0.75 * (1 - op) - 0.25 * op : -0.25); if (closed) hinge.rotation.x = Math.PI / 2 * 0.75;
  const sub = t >= TAP + 0.08; const pop = ease((t - POP) / 0.3) * (1 - ease((t - TAP - 0.9) / 0.25));
  if (t >= OPEN) { drawTG(t, { scroll: 40 + Math.max(0, t - OPEN) * 40, sub, ripple: (t - TAP) / 0.6, paws: cl((t - TAP - 0.3) / 1.0), alive: (t - TAP) / 1.1, hideBtn: pop > 0.02 }); }
  else drawDoc(t < LN[4].start ? 2.3 : 2.3 + Math.max(0, t - CLICK - 0.6) * 1.6);
  btn3.visible = pop > 0.02; drawBtn(sub);
  { const tapK = Math.max(0, 1 - Math.abs(t - TAP) / 0.1); const wob = t > POP ? Math.sin((t - POP) * 18) * Math.exp(-(t - POP) * 4) : 0;
    btn3.position.copy(BTN_LOCAL).add(new THREE.Vector3(0, 0, 0.004 + pop * 0.045 - tapK * 0.03)); const sc = 1 + pop * 0.3 - tapK * 0.08 + wob * 0.05; btn3.scale.set(sc, sc, sc); btn3.rotation.set(-0.15 * pop, -0.2 * pop * (1 - tapK), wob * 0.08); }
  tablePaws.forEach((m, k) => { m.visible = sh.set === 'A' && t > TAP + 0.25 + k * 0.14; });
  if (sh.cta) for (const e of cat.eyes) e.refl.visible = true;
  if (sh.cta && cat.g.visible) { scene.updateMatrixWorld(true); const btn = btn3.visible ? btn3.localToWorld(new THREE.Vector3(-0.02, 0, 0.012)) : scr.localToWorld(new THREE.Vector3(-0.1, -0.052, 0.01));
    const reach = ease((t - TAP + 0.45) / 0.35) * (1 - ease((t - TAP - 0.25) / 0.3)); const tp = Math.max(0, 1 - Math.abs(t - TAP) / 0.1);
    if (reach > 0.01) { const tgt = toLocal(cat.g, btn); const restP = new THREE.Vector3(0.05, 0.03, 0.13); const p2 = restP.clone().lerp(tgt, reach); p2.z -= tp * 0.012; cat.setPaw(p2); } }
  socks.forEach((o) => { const mv = t > WT(2, 7) + o.i * 0.1; o.g.position.set(...sockPos(o.i, mv)); o.g.rotation.y = o.i * 1.3; });
  // лампы и часы
  const lampOn = sh.set === 'A' && (sh.mood === 'warm' || (sh.mood === 'click' && t >= CLICK)); shadeA.material.emissiveIntensity = lampOn ? 1.0 : 0.05;
  dbulb.material.emissiveIntensity = sh.set === 'A' && t >= CLICK - 0.02 && sh.dima === 'desk' ? 2.0 : 0; drawClock(52 + (t - LN[2].start) * 3);
  for (const p of DIMAS) if (p.root.visible) { p.setArms(); p.face.draw(); }
  composer.render();
  scene.updateMatrixWorld(true); const bp = scr.localToWorld(new THREE.Vector3(-0.0853, -0.0517, 0.05)).project(camera);
  return { btn: [(bp.x + 1) / 2, (1 - bp.y) / 2], tap: TAP, cut: si };
};
window.debugView = (p, l, fov = 50, t = 1) => { window.renderFrame(t); camera.fov = fov; camera.updateProjectionMatrix(); camera.position.set(...p); camera.lookAt(...l); composer.render(); };
document.fonts.load('800 40px Onest').then(() => document.fonts.load('600 40px Onest')).then(() => { window.ready = true; });
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
window.exportGLB = (t) => new Promise((res, rej) => { const r = window.renderFrame(t); scene.updateMatrixWorld(true); const lt = lightsFor(lastSh, t);
  new GLTFExporter().parse([scene], (buf) => { const b = new Uint8Array(buf); let s = ''; for (let i = 0; i < b.length; i += 32768) s += String.fromCharCode.apply(null, b.subarray(i, i + 32768)); let fl = null; cat.g.traverse((o) => { if (o.isPointLight) { const w = o.getWorldPosition(new THREE.Vector3()); fl = [w.x, -w.z, w.y]; } }); res({ glb: btoa(s), cam: { pos: camera.position.toArray(), quat: camera.quaternion.toArray(), fov: camera.fov }, flame: cat.g.visible ? fl : null, ...lt, btn: r.btn, tap: r.tap }); }, rej, { binary: true, onlyVisible: true, maxTextureSize: 1024 }); });
