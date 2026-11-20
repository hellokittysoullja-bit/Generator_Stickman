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
      const cx = 512 + sx * eyeDX;
      const open = 1 - s.blink;
      g.save(); g.beginPath(); g.ellipse(cx, eyeY, ew, Math.max(1, eh * open), 0, 0, 7); g.clip();
      g.fillStyle = '#f7f4ee'; g.fillRect(cx - ew, eyeY - eh, ew * 2, eh * 2);
      const ix = cx + s.look[0] * 14, iy = eyeY + s.look[1] * 8;
      g.fillStyle = o.iris; g.beginPath(); g.arc(ix, iy, 33, 0, 7); g.fill();
      g.fillStyle = '#141414'; g.beginPath(); g.arc(ix, iy, 17, 0, 7); g.fill();
      g.fillStyle = 'rgba(255,255,255,0.95)'; g.beginPath(); g.arc(ix - 9, iy - 10, 6, 0, 7); g.fill();
      g.fillStyle = 'rgba(80,50,40,0.18)'; g.fillRect(cx - ew, eyeY - eh, ew * 2, eh * 0.35);
      g.restore();
      // верхнее веко
      g.strokeStyle = '#2b1d18'; g.lineWidth = 7; g.lineCap = 'round';
      g.beginPath(); g.ellipse(cx, eyeY, ew + 2, Math.max(2, eh * open) + 2, 0, Math.PI * 1.08, Math.PI * 1.92); g.stroke();
      if (s.blink > 0.85) { g.beginPath(); g.moveTo(cx - ew, eyeY); g.quadraticCurveTo(cx, eyeY + 10, cx + ew, eyeY); g.stroke(); }
      // бровь
      g.strokeStyle = o.brow; g.lineWidth = 11;
      g.beginPath(); const by = eyeY - eh - 34 - s.brow * 22 - s.eyesWide * 10;
      g.moveTo(cx - 48, by + 8 - sx * s.brow * 0); g.quadraticCurveTo(cx, by - 10, cx + 48, by + 6 + sx * 2); g.stroke();
    }
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
  const face = new Face(faceHolder, r, o.face || {});
  // волосы
  const hairM = M(o.hair || '#2b1d16', { roughness: 0.85 });
  if (o.curly) {
    for (let i = 0; i < 70; i++) { const a = rng() * Math.PI * 2, y = hh * (0.7 + rng() * 0.45); const back = Math.cos(a) < 0.25 || y > hh * 0.95;
      if (!back) continue; const rr = r + 0.03 + rng() * 0.02; mesh(new THREE.IcosahedronGeometry(0.05 + rng() * 0.02, 2), hairM, Math.sin(a) * rr, y, Math.cos(a) * rr * 0.95, headPivot); }
    for (let i = 0; i < 14; i++) { const x = (i / 13 - 0.5) * 0.3; mesh(new THREE.IcosahedronGeometry(0.045, 2), hairM, x, hh + 0.02 - Math.abs(x) * 0.4, 0.09 - Math.abs(x) * 0.3, headPivot); }
    for (let i = 0; i < 22; i++) { const sx = i % 2 ? 1 : -1; mesh(new THREE.IcosahedronGeometry(0.045 + rng() * 0.015, 2), hairM, sx * (r + 0.02 + rng() * 0.03), hh * (0.3 + rng() * 0.6), -0.02 - rng() * 0.12, headPivot); }
  } else {
    const cap = new THREE.SphereGeometry(r * 1.06, 64, 32, 0, Math.PI * 2, 0, Math.PI * 0.5);
    const h = mesh(cap, hairM, 0, hh * 0.78, -0.012, headPivot); h.scale.set(1.0, 0.75, 1.02);
    for (let i = 0; i < 90; i++) { const a = rng() * Math.PI * 2, el = rng() * 1.2; const front = Math.cos(a) > 0.55;
      const y = hh * (front ? 0.93 + el * 0.06 : 0.62 + el * 0.32); const rr = (r + 0.008) * (front ? 0.92 : 1.0) * (0.9 + 0.1 * Math.cos(el));
      const b2 = mesh(new THREE.IcosahedronGeometry(0.03 + rng() * 0.012, 2), hairM, Math.sin(a) * rr, y + (front ? 0.0 : 0), Math.cos(a) * rr * 0.95, headPivot); b2.scale.set(1.2, 0.8, 1.0); }
    for (let i = 0; i < 9; i++) { const x = (i / 8 - 0.5) * 0.25; mesh(new THREE.IcosahedronGeometry(0.035, 2), hairM, x, hh * 0.95 - Math.abs(x) * 0.2 - (i % 2) * 0.012, r * 0.82, headPivot).scale.set(1.3, 0.7, 0.9); }
  }
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
    const hand = mesh(new THREE.SphereGeometry(0.045, 24, 16), skin, 0, 0, 0, torso); hand.scale.set(0.8, 1.05, 0.65);
    const cuff = mesh(new THREE.TorusGeometry(0.038, 0.012, 10, 24), cloth, 0, 0, 0, torso);
    arms.push({ sx, shoulder, tube, hand, cuff, elbow: new THREE.Vector3(sx * 0.27, tH - 0.3, 0.05), wrist: new THREE.Vector3(sx * 0.24, tH - 0.5, 0.1) });
  }
  const setArms = () => { for (const a of arms) {
    const c = new THREE.CatmullRomCurve3([a.shoulder, a.shoulder.clone().lerp(a.elbow, 0.5).add(new THREE.Vector3(a.sx * 0.02, 0, 0)), a.elbow, a.wrist]);
    a.tube.geometry.dispose(); a.tube.geometry = new THREE.TubeGeometry(c, 40, 0.042, 14, false);
    const tg = c.getTangent(1); a.hand.position.copy(a.wrist).addScaledVector(tg, 0.045); a.hand.lookAt(a.hand.position.clone().add(tg)); a.hand.rotateX(Math.PI / 2);
    a.cuff.position.copy(a.wrist); a.cuff.lookAt(a.wrist.clone().add(tg));
  } };
  return { root, torso, headPivot, face, arms, setArms, tH };
}

// ---------- кот ----------
function makeCat() {
  const g = new THREE.Group(); const fur = M('#1d1b1f', { roughness: 0.95 });
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
    eyes.push({ ew, lid });
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
  return { g, headPivot, eyes, earR, setTail };
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
wallPlates(back, -1.75, 1.85, 2, 4); wallPlates(back, 1.75, 1.85, 2, 4);
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
chair(0, -0.8, 0); chair(-0.55, 0.8, Math.PI);

// ---------- люди ----------
const dima = makePerson({ cloth: '#c79a3b', pants: '#2c3a55', hair: '#3a2618', fringe: true, face: { iris: '#5a7a4a' } });
dima.root.position.set(0.35, 0, 1.25); dima.root.rotation.y = Math.PI + 0.25; scene.add(dima.root);
const mom = makePerson({ cloth: '#ece3d0', seated: true, curly: true, glasses: true, necklace: true, hair: '#1b1615', face: { iris: '#6b8aa6', brow: '#151010' } });
mom.root.position.set(0, 0.0, -0.78); scene.add(mom.root);
const cat = makeCat();
dima.torso.add(cat.g); cat.g.position.set(0.0, 0.08, 0.17); cat.g.rotation.y = 0.0;
// поза рук Димы: держит кота
dima.arms[0].elbow.set(-0.25, 0.15, 0.1); dima.arms[0].wrist.set(-0.1, 0.14, 0.27);
dima.arms[1].elbow.set(0.26, 0.13, 0.12); dima.arms[1].wrist.set(0.09, 0.08, 0.28); dima.setArms();
mom.arms[0].elbow.set(-0.27, 0.12, 0.15); mom.arms[0].wrist.set(-0.16, 0.2, 0.33);
mom.arms[1].elbow.set(0.27, 0.12, 0.15); mom.arms[1].wrist.set(0.16, 0.18, 0.34); mom.setArms();

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

// ---------- анимация ----------
const V = window.VOICE; const FPS = 30;
const ease = (x) => x < 0 ? 0 : x > 1 ? 1 : x * x * (3 - 2 * x);
const mouthAt = (t) => { const i = t * FPS, a = Math.floor(i); const m = V.mouth; return (m[a] || 0) * (1 - (i - a)) + (m[a + 1] || 0) * (i - a); };
const blinkAt = (t, times) => { for (const b of times) { const d = (t - b) / 0.16; if (d >= 0 && d <= 1) return Math.sin(d * Math.PI); } return 0; };
const SHOTS = [
  { t0: 0.0, t1: 1.96, cam: (u) => ({ p: [0.1 - u * 0.04, 1.5, -0.2 + u * 0.15], l: [0.32, 1.42, 1.25], f: 1.35 }) },
  { t0: 1.96, t1: 3.0, cam: (u) => ({ p: [0.22, 1.2, 0.05 + u * 0.08], l: [0.33, 1.06, 1.02], f: 0.95 }) },
  { t0: 3.0, t1: 5.4, cam: (u) => ({ p: [0.05, 1.3, 0.62 - u * 0.14], l: [0.0, 1.16, -0.78], f: 1.35 }) },
];
window.duration = 5.4;
window.renderFrame = (t) => {
  const sh = SHOTS.find((s) => t >= s.t0 && t < s.t1) || SHOTS[SHOTS.length - 1];
  const u = (t - sh.t0) / (sh.t1 - sh.t0), c = sh.cam(u);
  const hand = [Math.sin(t * 1.3) * 0.004, Math.sin(t * 1.7 + 1) * 0.003];
  camera.position.set(c.p[0] + hand[0], c.p[1] + hand[1], c.p[2]); camera.lookAt(...c.l);
  bokeh.uniforms.focus.value = c.f;
  // Дима говорит
  const m = mouthAt(t);
  dima.face.st.mouth = m; dima.face.st.smile = 0.55; dima.face.st.blink = blinkAt(t, [0.75, 2.6, 4.4]);
  dima.face.st.brow = ease((t - 0.9) / 0.2) * (1 - ease((t - 1.7) / 0.3)) * 0.8 + ease((t - 3.9) / 0.15) * 0.6;
  dima.face.st.look = [-0.3, 0.1];
  dima.headPivot.rotation.set(Math.sin(t * 7) * 0.03 * m - 0.05, -0.12 + Math.sin(t * 1.3) * 0.04, Math.sin(t * 2.1) * 0.03);
  dima.torso.rotation.z = Math.sin(t * 1.6) * 0.015; dima.torso.position.y = 0.80 + Math.sin(t * 2.5) * 0.004;
  dima.face.draw();
  // кот
  const cb = blinkAt(t, [2.25]) ; for (const e of cat.eyes) e.lid.rotation.x = -1.4 + cb * 1.25 + (t > 2.5 && t < 3 ? 0.35 : 0);
  cat.headPivot.rotation.set(0.05 + Math.sin(t * 1.1) * 0.03, Math.sin(t * 0.9) * 0.08 + (t > 2.0 ? 0.15 : 0), (t > 2.1 && t < 3 ? -0.18 * ease((t - 2.1) / 0.3) : 0));
  cat.earR.rotation.x = 0.5 + (Math.abs(t - 2.4) < 0.08 ? 0.4 : 0);
  cat.setTail(t);
  // мама: слушает, на «начальник» — шок, рука ко рту
  const shock = ease((t - 4.0) / 0.25);
  mom.face.st.mouth = 0; mom.face.st.round = shock; mom.face.st.smile = 0.5 - shock * 0.7;
  mom.face.st.eyesWide = shock; mom.face.st.brow = ease((t - 3.2) / 0.2) * 0.3 + shock * 0.9; mom.face.st.blink = blinkAt(t, [3.45]);
  mom.face.st.look = [0.1, 0.05];
  mom.headPivot.rotation.set(-shock * 0.12 + Math.sin(t * 1.4) * 0.02, Math.sin(t * 0.8) * 0.05, ease((t - 3.1) / 0.4) * 0.08 * (1 - shock));
  mom.arms[1].wrist.set(0.16 - shock * 0.14, 0.18 + shock * 0.4, 0.34 - shock * 0.06 + shock * 0.04); mom.arms[1].elbow.set(0.27, 0.12 + shock * 0.12, 0.15 + shock * 0.12); mom.setArms();
  mom.face.draw();
  composer.render();
};
window.ready = true;
window.debugView = (p, l, fov = 50) => { window.renderFrame(0.5); camera.fov = fov; camera.updateProjectionMatrix(); camera.position.set(...p); camera.lookAt(...l); bokeh.uniforms.aperture.value = 0; composer.render(); camera.fov = 32; camera.updateProjectionMatrix(); bokeh.uniforms.aperture.value = 0.0012; };
