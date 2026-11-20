// 3D-ситком 99 «9 брошенных хобби»: мама открывает шкаф Димы, лавина хобби, папа под гантелями, кот закрывает шкаф. three.js → glb → Blender.
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

// ---------- комната Димы ----------
const door = new THREE.Group(); door.position.set(-1.4, 0, 0.02); front.add(door);
for (const [w, h, x, y] of [[0.1, 2.15, -0.5, 1.075], [0.1, 2.15, 0.5, 1.075], [1.1, 0.1, 0, 2.15]]) mesh(new THREE.BoxGeometry(w, h, 0.06), M('#efe9dc', { roughness: 0.6 }), x, y, 0.03, door);
mesh(new THREE.BoxGeometry(0.9, 2.1, 0.01), M('#6f6a62'), 0, 1.05, -0.01, door);
const win = new THREE.Group(); win.position.set(0.3, 1.55, 0.02); left.add(win);
mesh(new THREE.PlaneGeometry(1.2, 1.1), new THREE.MeshBasicMaterial({ color: '#f6f1e2' }), 0, 0, 0.005, win);
for (const [w, h, x, y] of [[1.3, 0.07, 0, 0.58], [1.3, 0.1, 0, -0.58], [0.07, 1.2, -0.62, 0], [0.07, 1.2, 0.62, 0], [0.04, 1.1, 0, 0], [1.2, 0.04, 0, 0.1]]) mesh(new THREE.BoxGeometry(w, h, 0.06), M('#efe9dc'), x, y, 0.03, win);
const ch = new THREE.Group(); ch.position.set(0, RH - 0.02, -0.3); scene.add(ch);
mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.35, 8), M('#4a3a22', { metalness: 0.6 }), 0, -0.17, 0, ch);
mesh(new THREE.SphereGeometry(0.16, 32, 16, 0, Math.PI * 2, Math.PI * 0.45, Math.PI * 0.55), new THREE.MeshStandardMaterial({ color: '#fff6e6', emissive: '#ffe2b0', emissiveIntensity: 1.2, side: THREE.DoubleSide }), 0, -0.3, 0, ch);
wallPlates(back, -1.75, 1.85, 2, 3); wallPlates(back, 1.75, 1.9, 2, 3);
// кровать у правой стены
const bed = new THREE.Group(); bed.position.set(2.05, 0, 0.4); scene.add(bed);
mesh(roundBox(0.95, 0.32, 2.0, 0.03), woodM, 0, 0.2, 0, bed);
mesh(roundBox(0.9, 0.16, 1.9, 0.07), M('#3f5f8a', { roughness: 0.95 }), 0, 0.44, 0.03, bed);
mesh(roundBox(0.6, 0.12, 0.35, 0.06), M('#efe8da', { roughness: 0.95 }), 0, 0.56, -0.75, bed);
mesh(roundBox(0.95, 0.75, 0.06, 0.02), woodM, 0, 0.5, -1.0, bed);
// постер на правой стене
const poster = canvasTex(256, 384, (g, w, h) => { g.fillStyle = '#20314a'; g.fillRect(0, 0, w, h); g.fillStyle = '#f2c14e'; g.beginPath(); g.arc(128, 150, 80, 0, 7); g.fill(); g.fillStyle = '#e4572e'; g.fillRect(40, 270, 176, 26); g.fillStyle = '#9fd6c9'; g.fillRect(70, 310, 116, 16); });
mesh(new THREE.PlaneGeometry(0.5, 0.75), new THREE.MeshStandardMaterial({ map: poster, roughness: 0.8 }), -0.5, 1.65, 0.05, right);

// ---------- шкаф ----------
const WX = 0, WZ = -2.5, WW = 1.3, WH = 2.1, WD = 0.6, FZ = WZ + WD / 2;
const wardrobe = new THREE.Group(); wardrobe.position.set(WX, 0, WZ); scene.add(wardrobe);
const wM = new THREE.MeshStandardMaterial({ map: woodTex, roughness: 0.55, color: '#c7a184' });
const inM = M('#d9c8b0', { roughness: 0.9 });
mesh(new THREE.BoxGeometry(WW, WH, 0.03), inM, 0, WH / 2, -WD / 2 + 0.015, wardrobe);
for (const sx of [-1, 1]) mesh(new THREE.BoxGeometry(0.03, WH, WD), wM, sx * (WW / 2 - 0.015), WH / 2, 0, wardrobe);
mesh(new THREE.BoxGeometry(WW, 0.06, WD), wM, 0, 0.03, 0, wardrobe);
mesh(new THREE.BoxGeometry(WW + 0.06, 0.05, WD + 0.04), wM, 0, WH + 0.025, 0.01, wardrobe);
mesh(new THREE.BoxGeometry(0.025, WH, WD - 0.02), inM, 0, WH / 2, -0.01, wardrobe);
mesh(new THREE.BoxGeometry(WW - 0.06, 0.02, WD - 0.04), inM, 0, 1.55, -0.01, wardrobe);
mesh(new THREE.CylinderGeometry(0.01, 0.01, WW / 2 - 0.05, 8), M('#999', { metalness: 0.8, roughness: 0.3 }), -0.33, 1.45, 0, wardrobe).rotation.z = Math.PI / 2;
function makeDoor(sx) { // sx=-1 левая (петли слева), 1 правая
  const piv = new THREE.Group(); piv.position.set(sx * WW / 2, 0, WD / 2 + 0.012); wardrobe.add(piv);
  mesh(roundBox(WW / 2 - 0.01, WH - 0.04, 0.025, 0.008), wM, -sx * (WW / 4), WH / 2, 0, piv);
  for (const yy of [0.55, 1.5]) mesh(roundBox(WW / 2 - 0.16, 0.7, 0.012, 0.006), M('#b48d70', { roughness: 0.6 }), -sx * (WW / 4), yy, 0.016, piv);
  mesh(new THREE.SphereGeometry(0.022, 16, 12), M('#c9a24a', { metalness: 0.8, roughness: 0.3 }), -sx * (WW / 2 - 0.08), 1.05, 0.03, piv);
  return piv;
}
const doorL = makeDoor(-1), doorR = makeDoor(1);

// ---------- девять хобби (простые формы) ----------
const items = [];
function item(g, from, to, t0, dur, apex, spin, endRot, bounce = 0.06) { scene.add(g); items.push({ g, from, to, t0, dur, apex, spin, endRot, bounce }); return g; }
const G = () => new THREE.Group();
// 1 гитара
const guitar = G(); { const bodyM = M('#c8742e', { roughness: 0.35 }), dk = M('#3a2214', { roughness: 0.5 });
  const b1 = mesh(new THREE.CylinderGeometry(0.19, 0.19, 0.09, 40), bodyM, 0, 0, 0, guitar); b1.rotation.x = Math.PI / 2;
  const b2 = mesh(new THREE.CylinderGeometry(0.145, 0.145, 0.09, 40), bodyM, 0, 0.22, 0, guitar); b2.rotation.x = Math.PI / 2;
  const hole = mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.092, 24), dk, 0, 0.1, 0, guitar); hole.rotation.x = Math.PI / 2;
  mesh(new THREE.BoxGeometry(0.055, 0.5, 0.03), dk, 0, 0.6, 0.02, guitar); mesh(roundBox(0.08, 0.14, 0.03, 0.01), dk, 0, 0.9, 0.02, guitar);
  for (let k = 0; k < 4; k++) mesh(new THREE.CylinderGeometry(0.0016, 0.0016, 0.78, 4), M('#ddd', { metalness: 0.9 }), -0.012 + k * 0.008, 0.48, 0.047, guitar); }
// 2 гантели
const dumbbell = () => { const g = G(); const ir = M('#262626', { metalness: 0.5, roughness: 0.45 });
  const bar = mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.34, 12), M('#9a9a9a', { metalness: 0.9, roughness: 0.3 }), 0, 0, 0, g); bar.rotation.z = Math.PI / 2;
  for (const sx of [-1, 1]) for (const d of [0.1, 0.135]) { const p = mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.03, 8), ir, sx * d, 0, 0, g); p.rotation.z = Math.PI / 2; } return g; };
const db1 = dumbbell(), db2 = dumbbell();
// 3 мольберт
const easel = G(); { const lw = M('#b98a55', { roughness: 0.6 });
  for (const [x, rz, rx] of [[-0.2, -0.12, 0], [0.2, 0.12, 0], [0, 0, 0.35]]) { const l = mesh(new THREE.BoxGeometry(0.03, 1.2, 0.03), lw, x, 0.6, rx ? -0.2 : 0, easel); l.rotation.set(rx, 0, rz); }
  const cv = canvasTex(256, 200, (g, w, h) => { g.fillStyle = '#fbf8f0'; g.fillRect(0, 0, w, h); g.fillStyle = '#7fb0d6'; g.beginPath(); g.arc(70, 70, 40, 0, 7); g.fill(); g.strokeStyle = '#e07a3f'; g.lineWidth = 9; g.beginPath(); g.moveTo(20, 170); g.quadraticCurveTo(120, 90, 236, 160); g.stroke(); });
  mesh(new THREE.BoxGeometry(0.5, 0.4, 0.02), new THREE.MeshStandardMaterial({ map: cv, roughness: 0.9 }), 0, 0.85, 0.03, easel);
  mesh(new THREE.BoxGeometry(0.55, 0.03, 0.06), lw, 0, 0.63, 0.04, easel); }
// 4 скейт
const skate = G(); { const deck = mesh(roundBox(0.2, 0.02, 0.78, 0.01), M('#e4572e', { roughness: 0.5 }), 0, 0.07, 0, skate);
  mesh(new THREE.BoxGeometry(0.19, 0.002, 0.7), M('#1d1d1d', { roughness: 1 }), 0, 0.081, 0, skate);
  for (const z of [-0.26, 0.26]) for (const sx of [-1, 1]) { const w = mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.03, 16), M('#f2e9c9', { roughness: 0.4 }), sx * 0.085, 0.03, z, skate); w.rotation.z = Math.PI / 2; } }
// 5 кубик Рубика
const rubik = G(); { const C = ['#c0392b', '#e67e22', '#f1f1f1', '#f4d03f', '#27ae60', '#2471a3'], s = 0.035;
  for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) for (let k = -1; k <= 1; k++) {
    const mats = [i === 1 ? C[0] : '#111', i === -1 ? C[1] : '#111', j === 1 ? C[2] : '#111', j === -1 ? C[3] : '#111', k === 1 ? C[4] : '#111', k === -1 ? C[5] : '#111'].map((c) => M(c, { roughness: 0.3 }));
    mesh(roundBox(s * 0.94, s * 0.94, s * 0.94, 0.005), mats[0], i * s, j * s, k * s, rubik).material = mats; } }
// 6 ракетка
const racket = G(); { const rf = mesh(new THREE.TorusGeometry(0.13, 0.012, 10, 40), M('#2a7de1', { roughness: 0.4 }), 0, 0.42, 0, racket); rf.scale.set(0.8, 1, 1);
  const net = canvasTex(128, 128, (g) => { g.clearRect(0, 0, 128, 128); g.strokeStyle = 'rgba(240,240,240,0.9)'; g.lineWidth = 2; for (let k = 4; k < 128; k += 10) { g.beginPath(); g.moveTo(k, 0); g.lineTo(k, 128); g.stroke(); g.beginPath(); g.moveTo(0, k); g.lineTo(128, k); g.stroke(); } });
  const n = mesh(new THREE.CircleGeometry(0.125, 32), new THREE.MeshStandardMaterial({ map: net, transparent: true, side: THREE.DoubleSide, roughness: 0.6 }), 0, 0.42, 0, racket); n.scale.set(0.8, 1, 1);
  mesh(new THREE.CylinderGeometry(0.016, 0.018, 0.3, 12), M('#222', { roughness: 0.8 }), 0, 0.14, 0, racket); }
// 7 коробка с пазлом
const puzzle = G(); { const art = canvasTex(256, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#8ec5e8'); gr.addColorStop(1, '#f6d58e'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    g.fillStyle = '#4e8f4a'; g.beginPath(); g.moveTo(0, 200); g.lineTo(90, 110); g.lineTo(170, 190); g.lineTo(256, 120); g.lineTo(256, 256); g.lineTo(0, 256); g.fill(); g.strokeStyle = 'rgba(0,0,0,0.25)'; g.lineWidth = 2;
    for (let k = 1; k < 4; k++) { g.beginPath(); g.moveTo(k * 64, 0); g.lineTo(k * 64, 256); g.stroke(); g.beginPath(); g.moveTo(0, k * 64); g.lineTo(256, k * 64); g.stroke(); } g.fillStyle = '#fff'; g.font = '800 34px Onest'; g.fillText('1000', 14, 44); });
  const side = M('#3c6fb0', { roughness: 0.6 }); mesh(new THREE.BoxGeometry(0.42, 0.07, 0.3), [side, side, new THREE.MeshStandardMaterial({ map: art, roughness: 0.6 }), side, side, side], 0, 0.035, 0, puzzle); }
const pieces = []; for (let i = 0; i < 14; i++) { const p = mesh(new THREE.BoxGeometry(0.035, 0.006, 0.035), M(['#8ec5e8', '#4e8f4a', '#f6d58e'][i % 3], { roughness: 0.6 }), 0, -5, 0, scene); pieces.push({ m: p, a: rng() * 7, r: 0.12 + rng() * 0.3, h: 0.2 + rng() * 0.4, rot: rng() * 3 }); }
// 8 ролики
const roller = () => { const g = G(); mesh(roundBox(0.1, 0.18, 0.24, 0.04), M('#f2f2f2', { roughness: 0.5 }), 0, 0.17, 0, g); mesh(roundBox(0.1, 0.05, 0.27, 0.02), M('#6c3fa0', { roughness: 0.5 }), 0, 0.08, 0.01, g);
  for (let k = 0; k < 4; k++) { const w = mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.025, 16), M('#9be15d', { roughness: 0.4 }), 0, 0.03, -0.1 + k * 0.067, g); w.rotation.z = Math.PI / 2; } return g; };
const rl1 = roller(), rl2 = roller();
// 9 вязание
const knit = G(); { const yM = M('#d94f70', { roughness: 0.95 }); mesh(new THREE.SphereGeometry(0.09, 24, 18), yM, 0, 0.09, 0, knit);
  for (let k = 0; k < 6; k++) { const tr = mesh(new THREE.TorusGeometry(0.09, 0.006, 6, 30), M('#c23e5e', { roughness: 0.95 }), 0, 0.09, 0, knit); tr.rotation.set(rng() * 3, rng() * 3, 0); }
  for (const sx of [-1, 1]) { const nd = mesh(new THREE.CylinderGeometry(0.004, 0.004, 0.32, 8), M('#e8d9b0', { roughness: 0.4 }), sx * 0.02, 0.14, 0.02, knit); nd.rotation.set(0.9, 0, sx * 0.35); }
  const sc = mesh(roundBox(0.16, 0.012, 0.12, 0.005), yM, 0.13, 0.01, 0.08, knit); sc.rotation.y = 0.4; }
const D = (x, y, z) => [x, y, z];
//        объект    из шкафа (x,y,z)          куда (x,y,z)             старт  полёт  дуга  вращение          итоговый поворот
item(guitar, D(-0.3, 1.0, -2.5), D(0.45, 0.33, -0.78), -0.06, 0.62, 0.55, [4, 1.5, 3], [-Math.PI / 2, 0, 2.6]);
item(db1, D(0.3, 0.4, -2.5), D(0.24, 0.39, -0.22), 0.1, 0.62, 0.7, [5, 2, 6], [0, 0.6, 0], 0.03);
item(db2, D(0.35, 0.7, -2.5), D(0.5, 0.39, -0.02), 0.18, 0.6, 0.6, [-4, 3, 5], [0, -0.4, 0], 0.03);
item(easel, D(-0.35, 0.3, -2.5), D(-1.2, 0.04, -0.9), 0.02, 0.7, 0.5, [2, 0, 3], [-Math.PI / 2, 0.4, 0], 0.04);
item(skate, D(0.3, 1.2, -2.5), D(1.0, 0.0, 0.55), 0.06, 0.68, 0.6, [6, 3, 2], [0, 0.5, 0], 0.08);
item(rubik, D(0.2, 1.75, -2.5), D(-0.15, 0.053, 0.45), 0.0, 0.75, 0.9, [9, 7, 5], [0.3, 0.6, 0], 0.12);
item(racket, D(-0.25, 1.3, -2.5), D(-0.55, 0.02, -0.15), 0.12, 0.62, 0.6, [6, 2, 4], [-Math.PI / 2, 0, 0.8]);
item(puzzle, D(-0.25, 1.65, -2.5), D(-0.45, 0.0, -1.45), 0.08, 0.5, 0.35, [2, 4, 1], [0, 0.3, 0], 0.05);
item(rl1, D(0.25, 1.6, -2.5), D(-0.95, 0.0, 0.2), 0.04, 0.72, 0.7, [5, 5, 3], [0, -0.9, 0], 0.07);
item(rl2, D(-0.2, 0.7, -2.5), D(-0.7, 0.0, 0.45), 0.14, 0.7, 0.6, [-5, 4, 2], [0, 0.4, 1.4], 0.06);
item(knit, D(0.15, 0.25, -2.5), D(0.05, 0.0, 0.9), 0.2, 0.75, 0.45, [8, 0, 0], [0, 0.2, 0], 0.09);

// ---------- люди ----------
const standing = (p) => { for (const a of p.arms) { a.elbow.set(a.sx * 0.24, 0.22, 0.03); a.wrist.set(a.sx * 0.22, -0.02, 0.08); } };
const mom = makePerson({ cloth: '#2c6e6a', curly: true, glasses: true, earrings: true, watch: true, hair: '#1b1615', skin: '#dcb592', pants: '#33302e',
  face: { iris: '#6b8aa6', brow: '#151010', lashes: true, lid: 0.22 } });
mom.root.position.set(-1.05, 0, -1.6); scene.add(mom.root);
const dadHold = new THREE.Group(); dadHold.position.set(0.35, 0, -1.25); dadHold.rotation.y = Math.PI; scene.add(dadHold);
const dad = makePerson({ cloth: '#d99cbc', flatHair: true, hair: '#6b7562', collar: '#e8afc9', ring: true, skin: '#d9b08c', pants: '#4a4f5a',
  face: { iris: '#6a8a6a', brow: '#2a2420', mustache: true, lid: 0.3, browW: 13 } });
dadHold.add(dad.root);
const dima = makePerson({ cloth: '#c79a3b', hair: '#3a2618', pants: '#2c3a55', face: { iris: '#5a7a4a', lid: 0.24 } });
dima.root.position.set(1.35, 0, 0.35); scene.add(dima.root);
const PEOPLE = { dad, mom, dima };
for (const p of Object.values(PEOPLE)) { p.baseY = p.torso.position.y; standing(p); p.setArms(); }
const cat = makeCat(); scene.add(cat.g);

// ---------- поле комментария (3D) ----------
const cmCan = document.createElement('canvas'); cmCan.width = 1024; cmCan.height = 300; const cmTex = new THREE.CanvasTexture(cmCan); cmTex.colorSpace = THREE.SRGBColorSpace; cmTex.anisotropy = 8;
function rrect(g, x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
function drawComment(n, caret, sent) {
  const g = cmCan.getContext('2d'); g.clearRect(0, 0, 1024, 300);
  g.fillStyle = '#ffffff'; rrect(g, 6, 6, 1012, 288, 60); g.fill(); g.strokeStyle = sent ? '#4fae4e' : '#c9ced6'; g.lineWidth = 8; rrect(g, 10, 10, 1004, 280, 56); g.stroke();
  g.fillStyle = '#8a929c'; g.font = '600 34px Onest'; g.fillText('Комментарий', 70, 70);
  const word = 'ДОДЕЛАТЬ'.slice(0, n); g.fillStyle = '#16181c'; g.font = '900 132px Onest'; g.fillText(word, 62, 205);
  if (caret && !sent) { const w = g.measureText(word).width; g.fillStyle = '#2ea6ff'; g.fillRect(72 + w, 105, 9, 120); }
  g.fillStyle = sent ? '#4fae4e' : (n >= 8 ? '#2ea6ff' : '#b8d9f3'); g.beginPath(); g.arc(905, 160, 70, 0, 7); g.fill();
  g.fillStyle = '#fff'; g.beginPath(); if (sent) { g.lineWidth = 16; g.strokeStyle = '#fff'; g.moveTo(870, 160); g.lineTo(897, 188); g.lineTo(945, 130); g.stroke(); } else { g.moveTo(872, 115); g.lineTo(955, 160); g.lineTo(872, 205); g.lineTo(888, 160); g.closePath(); g.fill(); }
  cmTex.needsUpdate = true;
}
const cmt = new THREE.Group(); scene.add(cmt); cmt.visible = false;
mesh(roundBox(0.26, 0.076, 0.012, 0.012), M('#e9edf2', { roughness: 0.35 }), 0, 0, -0.008, cmt);
const cmFace = new THREE.Mesh(new THREE.PlaneGeometry(0.256, 0.075), new THREE.MeshBasicMaterial({ map: cmTex, transparent: true, toneMapped: false })); cmFace.position.z = 0.0002; cmt.add(cmFace);

// ---------- свет (превью three.js; в Blender свет ставится заново) ----------
scene.add(new THREE.HemisphereLight('#fff1d8', '#5b3e2a', 0.75));
const key = new THREE.DirectionalLight('#fff4e0', 2.4); key.position.set(-3.5, 3.2, 1.2); key.target.position.set(0, 0.8, -1); scene.add(key, key.target);
key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.camera.left = -3; key.shadow.camera.right = 3; key.shadow.camera.top = 3; key.shadow.camera.bottom = -3; key.shadow.bias = -0.0004; key.shadow.normalBias = 0.02;
const top = new THREE.PointLight('#ffe3b8', 3.0, 6, 2); top.position.set(0, RH - 0.45, -0.3); scene.add(top);
const fill = new THREE.PointLight('#fff2e2', 1.2, 4, 1.5); camera.add(fill); fill.position.set(0.15, 0.2, 0.1); scene.add(camera);
const composer = new EffectComposer(renderer); composer.addPass(new RenderPass(scene, camera)); composer.addPass(new OutputPass());

// ---------- анимация ----------
const V = window.VOICE; const FPS = 30;
const cl = (x) => Math.max(0, Math.min(1, x));
const ease = (x) => { x = cl(x); return x * x * (3 - 2 * x); };
const eout = (x) => { x = cl(x); return 1 - Math.pow(1 - x, 3); };
const back2 = (x) => { x = cl(x); const c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
const mouthOf = (sp, t) => { const m = V.mouth[sp], i = t * FPS, a = Math.floor(i); return (m[a] || 0) * (1 - (i - a)) + (m[a + 1] || 0) * (i - a); };
const blinkAt = (t, times) => { for (const b of times) { const d = (t - b) / 0.15; if (d >= 0 && d <= 1) return Math.sin(d * Math.PI); } return 0; };
const v3 = (a) => new THREE.Vector3(...a);
const L = V.lines; const W = (li, wi) => L[li].words[wi].start;   // время слова
const T_DIMA1 = L[1].start, T_DAD = L[2].start, T_MOM2 = L[3].start, T_DIMA2 = L[4].start, T_CTA = L[5].start, T_END = L[5].end;
const T_WORD = W(5, 1), T_WORD_END = L[5].words[1].end, T_SENT = W(5, 2) + 0.05;
const SHOTS = [
  { t0: 0, t1: T_DIMA1, p: [0.15, 1.3, 1.25], l: [0.0, 0.95, -1.7], fov: 40, hook: true, push: 0.06 },
  { t0: T_DIMA1, t1: W(1, 4) - 0.05, p: [0.62, 1.55, -0.3], l: [1.35, 1.48, 0.35], push: 0.1 },
  { t0: W(1, 4) - 0.05, t1: T_DAD, p: [1.05, 1.25, 1.1], l: [-0.1, 0.25, -0.75], fov: 40, push: 0.12 },
  { t0: T_DAD, t1: T_MOM2, p: [0.62, 1.0, 1.05], l: [0.35, 0.22, 0.12], push: 0.12, dad: true },
  { t0: T_MOM2, t1: T_DIMA2, p: [-0.35, 1.5, -0.75], l: [-1.05, 1.42, -1.6], push: 0.1 },
  { t0: T_DIMA2, t1: T_CTA, p: [0.3, 1.45, -0.55], l: [1.35, 1.3, 0.35], push: 0.08 },
  { t0: T_CTA, t1: T_END + 0.25, p: [0.95, 1.5, 1.95], l: [1.3, 1.36, 0.35], push: 0.12, cta: true },
  { t0: T_END + 0.25, t1: 99, p: [-0.15, 1.05, 0.35], l: [0.25, 0.55, -2.35], fov: 38, push: 0.07 },
];
const blinks = { dad: [2.4, 7.0, 9.9, 13.1, 17.0], mom: [2.9, 6.6, 11.2, 15.8], dima: [1.4, 4.9, 9.5, 12.7, 16.6, 18.2] };
function toLocal(obj, w) { return obj.worldToLocal(w.clone()); }
const faceTo = (p, x, z) => Math.atan2(x - p.root.position.x, z - p.root.position.z);
const angLerp = (a, b, k) => { let d = b - a; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; return a + d * k; };
window.duration = V.total;
window.renderFrame = (t) => {
  const si = SHOTS.findIndex((s) => t >= s.t0 && t < s.t1); const sh = SHOTS[si < 0 ? SHOTS.length - 1 : si];
  const u = (t - sh.t0) / Math.max(0.01, sh.t1 - sh.t0);
  // двери
  const aL = 0.45 + 1.5 * eout(t / 0.28); doorL.rotation.y = -(aL + (t > 0.28 ? Math.sin((t - 0.28) * 14) * Math.exp(-(t - 0.28) * 5) * 0.1 : 0));
  let aR = 0.1 + 1.65 * back2((t - 0.04) / 0.22);
  const tc = T_END + 0.25; const closeK = ease((t - (tc + 1.0)) / 0.7); aR *= 1 - closeK; if (closeK >= 1) aR = Math.sin((t - tc - 1.7) * 30) * Math.exp(-(t - tc - 1.7) * 9) * 0.03;
  doorR.rotation.y = aR;
  // предметы
  for (const it of items) { const k = (t - it.t0) / it.dur; const a = v3(it.from), b = v3(it.to);
    if (k <= 0) { it.g.position.copy(a); it.g.rotation.set(it.spin[0] * 0.05, it.spin[1] * 0.05, it.spin[2] * 0.05); continue; }
    const kk = cl(k); const p = a.clone().lerp(b, kk); p.y += it.apex * 4 * kk * (1 - kk); const lt = t - it.t0 - it.dur;
    if (lt > 0) p.y += it.bounce * Math.abs(Math.sin(lt / 0.2 * Math.PI)) * Math.exp(-lt * 7);
    it.g.position.copy(p); const r = 1 - eout(kk); it.g.rotation.set(it.endRot[0] - it.spin[0] * r, it.endRot[1] - it.spin[1] * r, it.endRot[2] - it.spin[2] * r); }
  { const lt = t - 0.08 - 0.5; const sk = lt > 0 ? Math.max(0, 0.5 - lt) * 1.4 : 0; skate.position.x += lt > 0 ? (1 - Math.exp(-lt * 2)) * 0.35 : 0; skate.position.z += lt > 0 ? (1 - Math.exp(-lt * 2)) * 0.12 : 0; skate.rotation.y += sk * 0.1; }
  { const lt = t - 0.2 - 0.75; if (lt > 0) { const d = (1 - Math.exp(-lt * 1.6)) * 0.5; knit.position.x -= d * 0.55; knit.position.z += d * 0.25; knit.rotation.x += d * 9; } }
  { const lt = t - 0.58; for (const pc of pieces) { if (lt < 0) { pc.m.position.set(0, -5, 0); continue; } const k = cl(lt / 0.45); pc.m.position.set(-0.45 + Math.cos(pc.a) * pc.r * k, 0.005 + pc.h * 4 * k * (1 - k), -1.45 + Math.sin(pc.a) * pc.r * k); pc.m.rotation.set(0, pc.rot + k * 4, 0); } }
  // камера
  const P = v3(sh.p), Lk = v3(sh.l); const dir = P.clone().sub(Lk);
  let k = 1 - (sh.push || 0) * u; let roll = 0;
  if (sh.hook) { const f = eout(t / 0.22); k *= 1.62 - 0.62 * f + (t > 0.22 && t < 0.45 ? -0.05 * Math.sin((t - 0.22) / 0.23 * Math.PI) : 0); roll = (1 - f) * 0.065;
    const hit = Math.max(0, 1 - Math.abs(t - 0.62) / 0.12); k *= 1 - 0.09 * hit; }
  camera.position.copy(Lk).addScaledVector(dir, k);
  const shake = (t0, a) => (t > t0 ? Math.exp(-(t - t0) * 9) * a : 0); const sa = shake(0.6, 0.03) + shake(0.75, 0.025) + shake(tc + 1.7, 0.012);
  camera.position.x += Math.sin(t * 1.3) * 0.004 + Math.sin(t * 61) * sa; camera.position.y += Math.sin(t * 1.7 + 1) * 0.003 + Math.cos(t * 53) * sa;
  camera.fov = sh.fov || 32; camera.updateProjectionMatrix(); camera.lookAt(Lk); camera.rotateZ(roll);
  fill.intensity = 1.0;

  // --- лица ---
  for (const [name, p] of Object.entries(PEOPLE)) {
    const m = mouthOf(name, t); const s = p.face.st; s.mouth = m; s.blink = blinkAt(t, blinks[name]);
    p.headPivot.rotation.set(Math.sin(t * 7.3) * 0.035 * m - 0.02, Math.sin(t * 0.9 + name.length) * 0.04, Math.sin(t * 1.3 + name.length) * 0.02);
    p.torso.position.y = p.baseY + Math.sin(t * 2.4 + name.length) * 0.004; p.torso.rotation.set(0, 0, Math.sin(t * 1.1 + name.length) * 0.012);
    s.look = [0, 0]; s.brow = 0; s.frown = 0; s.smile = 0.3; s.eyesWide = 0; s.round = 0; s.sleepy = 0; standing(p);
  }
  // мама: открывает шкаф, потом к Диме, потом вниз к папе
  { const s = mom.face.st; let ry = Math.atan2(-0.35 + 1.05, -2.2 + 1.6);
    if (t > 0.35) ry = angLerp(ry, faceTo(mom, 1.35, 0.35), ease((t - 0.35) / 0.3));
    if (t > T_DAD - 0.2) ry = angLerp(faceTo(mom, 1.35, 0.35), faceTo(mom, 0.35, 0.1), ease((t - T_DAD + 0.2) / 0.4));
    if (t > T_DIMA2) ry = angLerp(faceTo(mom, 0.35, 0.1), faceTo(mom, 1.35, 0.35), ease((t - T_DIMA2) / 0.4));
    mom.root.rotation.y = ry;
    if (t < 0.6) { s.eyesWide = 1; s.round = t > 0.15 ? 0.6 : 0; s.brow = 0.8; }
    else if (t < T_DIMA1) { s.frown = 0.7; s.smile = -0.3; s.brow = 0.2; s.look = [0, 0]; }
    else if (t < T_MOM2) { s.frown = 0.4; s.smile = 0; s.look = t > T_DAD ? [0.2, 0.7] : [0, 0]; }
    else if (t < T_DIMA2) { s.frown = 0.2; s.smile = 0.15; s.sleepy = 0.25; s.look = [0, 0.8]; mom.headPivot.rotation.x += 0.22; }
    else { s.frown = 0.3; s.look = [0, 0]; s.sleepy = 0.15; }
    // рука на ручке двери
    if (t < 0.55) { scene.updateMatrixWorld(true); const hw = doorL.localToWorld(new THREE.Vector3(WW / 2 - 0.08, 1.05, 0.04)); const loc = toLocal(mom.torso, hw);
      const a = mom.arms[1]; const sh0 = a.shoulder; const d = loc.clone().sub(sh0); if (d.length() > 0.52) loc.copy(sh0).addScaledVector(d.normalize(), 0.52);
      const kk = 1 - ease((t - 0.3) / 0.25); a.wrist.lerp(loc, kk); a.elbow.lerp(sh0.clone().lerp(loc, 0.5).add(new THREE.Vector3(0.06, -0.08, 0)), kk); }
    if (t > 0.3 && t < 2.0) { const k2 = ease((t - 0.3) / 0.2) * (1 - ease((t - 1.6) / 0.4)); for (const a of mom.arms) { a.wrist.lerp(new THREE.Vector3(a.sx * 0.16, 0.42, 0.2), k2); a.elbow.lerp(new THREE.Vector3(a.sx * 0.27, 0.22, 0.12), k2); } }
    if (t > T_MOM2 && t < T_DIMA2 + 0.3) { const k2 = ease((t - T_MOM2) / 0.25) * (1 - ease((t - T_DIMA2) / 0.3)); const a = mom.arms[1]; a.wrist.lerp(new THREE.Vector3(0.12, 0.12, 0.42), k2); a.elbow.lerp(new THREE.Vector3(0.25, 0.22, 0.18), k2); }
  }
  // папа: стоит у шкафа, падает на спину, гантели на груди
  { const s = dad.face.st; const f = cl((t - 0.42) / 0.3); const fall = f * f; const lt = t - 0.72;
    dad.root.rotation.x = -Math.PI / 2 * fall + (lt > 0 ? Math.sin(lt * 25) * Math.exp(-lt * 10) * 0.03 : 0);
    dad.root.position.y = 0.16 * fall; dad.root.position.z = 0;
    if (t < 0.45) { s.eyesWide = 1; s.round = 0.7; s.brow = 1; for (const a of dad.arms) { a.wrist.lerp(new THREE.Vector3(a.sx * 0.1, 0.62, 0.22), ease(t / 0.2)); a.elbow.lerp(new THREE.Vector3(a.sx * 0.3, 0.38, 0.15), ease(t / 0.2)); } }
    else { for (const a of dad.arms) { a.elbow.set(a.sx * 0.28, 0.25, 0.02); a.wrist.set(a.sx * 0.34, 0.06, 0.06); }
      if (t < T_DAD - 0.3) { s.sleepy = 0.55; s.smile = -0.1; s.look = [0, -0.3]; s.round = t < 1.4 ? 0.4 : 0; }
      else { s.sleepy = 0.15; s.frown = 0.35; s.smile = 0.05; s.brow = 0.3; s.look = [0, -0.4];
        // поднимает руку с пола: «верни»
        const k2 = ease((t - T_DAD - 0.1) / 0.3) * (1 - ease((t - T_MOM2 - 0.2) / 0.4)); const a = dad.arms[0]; a.wrist.lerp(new THREE.Vector3(-0.3, 0.42, 0.32), k2); a.elbow.lerp(new THREE.Vector3(-0.32, 0.3, 0.12), k2); }
      if (t > T_MOM2) { s.eyesWide = 0.5; s.look = [-0.5, -0.4]; s.round = t > T_MOM2 + 1.0 && t < T_DIMA2 ? 0.35 : 0; } }
    dad.headPivot.rotation.x += t > 0.45 ? 0.15 : 0;
  }
  // Дима
  { const s = dima.face.st; let ry = faceTo(dima, -1.05, -1.6);
    if (sh.cta) ry = angLerp(ry, Math.atan2(camera.position.x - dima.root.position.x, camera.position.z - dima.root.position.z), ease((t - T_CTA + 0.1) / 0.35));
    dima.root.rotation.y = ry;
    if (t < T_DIMA1) { s.eyesWide = 0.6; s.round = t > 0.4 && t < 1.6 ? 0.4 : 0; s.brow = 0.6; }
    else if (t < T_DAD) { s.smile = 0.45; s.brow = 0.5; s.look = [0.4, 0];
      const pt = [W(1, 0), W(1, 4), W(1, 7)]; const pk = Math.max(...pt.map((q) => Math.max(0, 1 - Math.abs(t - q - 0.35) / 0.55)));
      const a = dima.arms[1]; const k2 = ease(pk * 1.6); a.wrist.lerp(new THREE.Vector3(0.14, 0.42, 0.46), k2); a.elbow.lerp(new THREE.Vector3(0.25, 0.32, 0.2), k2); }
    else if (t < T_DIMA2) { s.look = [-0.3, 0.6]; s.smile = 0.2; s.brow = 0.3; }
    else if (t < T_CTA) { s.smile = 0.4; s.sleepy = 0.15; s.brow = 0.35; const k2 = ease((t - T_DIMA2 - 0.1) / 0.3) * (1 - ease((t - W(4, 3)) / 0.3));
      dima.torso.position.y += k2 * 0.02; for (const a of dima.arms) { a.wrist.lerp(new THREE.Vector3(a.sx * 0.4, 0.22, 0.24), k2); a.elbow.lerp(new THREE.Vector3(a.sx * 0.32, 0.2, 0.06), k2); } dima.headPivot.rotation.z += k2 * 0.12; }
    else { s.smile = 0.55; s.brow = 0.35; s.look = [0, 0];
      const k2 = ease((t - T_CTA) / 0.3) * (1 - ease((t - T_WORD_END - 0.6) / 0.35)); const a = dima.arms[1]; a.wrist.lerp(new THREE.Vector3(0.1, 0.4, 0.48), k2); a.elbow.lerp(new THREE.Vector3(0.24, 0.3, 0.2), k2);
      if (t > T_SENT) { s.smile = 0.8; } }
  }
  // кот: на полу у вязания, подпрыгивает от лавины; в финале залезает в шкаф и закрывает дверцу лапой
  const lids = (v) => { for (const e of cat.eyes) { e.lid.rotation.x = -1.4 + v; e.p.visible = e.hl.visible = v < 2.5; } };
  lids(blinkAt(t, [3.3, 8.0, 12.4, 16.9]) * 2.9); cat.setPaw(null); cat.g.scale.set(1, 1, 1);
  if (t < tc) { const hop = Math.max(0, Math.sin(cl((t - 0.15) / 0.4) * Math.PI)) * 0.22; cat.g.position.set(-0.32, hop, 1.0); cat.g.rotation.set(0, t < 1.2 ? Math.PI * 0.85 : angLerp(Math.PI * 0.85, 2.3, ease((t - 1.2) / 0.4)), 0);
    cat.headPivot.rotation.set(0.1 + Math.sin(t * 1.1) * 0.03, Math.sin(t * 0.7) * 0.15, 0); cat.earR.rotation.x = 0.5 + (t < 0.6 ? 0.4 : 0); }
  else { const j = cl((t - tc - 0.05) / 0.55); const from = v3([0.7, 0, -1.25]), to = v3([0.3, 0.06, -2.43]); const pos = from.clone().lerp(to, eout(j)); pos.y += Math.sin(j * Math.PI) * 0.38; cat.g.position.copy(pos);
    const land = (t - tc - 0.6) / 0.22; const sq = land > 0 && land < 1 ? Math.sin(land * Math.PI) * 0.16 : 0; cat.g.scale.set(1 + sq * 0.5, 1 - sq, 1 + sq * 0.5);
    cat.g.rotation.set(0, angLerp(Math.PI + 0.3, 0.15, ease((t - tc - 0.75) / 0.3)), 0);
    cat.headPivot.rotation.set(0.05, 0.25 * ease((t - tc - 1.0) / 0.3), 0);
    scene.updateMatrixWorld(true); const reach = ease((t - tc - 0.95) / 0.2) * (1 - ease((t - tc - 1.75) / 0.25));
    if (reach > 0.01) { const dw = doorR.localToWorld(new THREE.Vector3(-0.3, 0.3, -0.02)); const tg = toLocal(cat.g, dw); const restP = new THREE.Vector3(0.05, 0.03, 0.13); const d = tg.clone().sub(restP); if (d.length() > 0.24) tg.copy(restP).addScaledVector(d.normalize(), 0.24); cat.setPaw(restP.clone().lerp(tg, reach)); }
    if (t > tc + 1.6) lids(1.5); }
  cat.setTail(t);
  // поле комментария
  { const pop = back2((t - T_CTA - 0.05) / 0.35); cmt.visible = sh.cta && pop > 0.02;
    if (cmt.visible) { scene.updateMatrixWorld(true); cmt.position.copy(camera.localToWorld(new THREE.Vector3(-0.012, 0.135, -0.9))); cmt.quaternion.copy(camera.quaternion); cmt.rotateY(0.22); cmt.rotateX(-0.08);
      const wob = t > T_SENT ? Math.sin((t - T_SENT) * 22) * Math.exp(-(t - T_SENT) * 5) : 0; const sc = pop * (1 + wob * 0.06); cmt.scale.set(sc, sc, sc); cmt.rotateZ(wob * 0.05);
      const n = Math.round(8 * cl((t - T_WORD) / Math.max(0.2, T_WORD_END - T_WORD))); drawComment(n, Math.floor(t * 3) % 2 === 0, t > T_SENT); } }
  for (const p of Object.values(PEOPLE)) { p.setArms(); p.face.draw(); }
  composer.render();
  return { cut: SHOTS.map((s) => s.t0) };
};
window.debugView = (p, l, fov = 50, t = 1) => { window.renderFrame(t); camera.fov = fov; camera.updateProjectionMatrix(); camera.position.set(...p); camera.lookAt(...l); composer.render(); };
document.fonts.load('800 40px Onest').then(() => document.fonts.load('900 40px Onest')).then(() => { window.ready = true; });
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
window.exportGLB = (t) => new Promise((res, rej) => { window.renderFrame(t); scene.updateMatrixWorld(true);
  new GLTFExporter().parse([scene], (buf) => { const b = new Uint8Array(buf); let s = ''; for (let i = 0; i < b.length; i += 32768) s += String.fromCharCode.apply(null, b.subarray(i, i + 32768)); res({ glb: btoa(s), cam: { pos: camera.position.toArray(), quat: camera.quaternion.toArray(), fov: camera.fov } }); }, rej, { binary: true, onlyVisible: true, maxTextureSize: 1024 }); });
