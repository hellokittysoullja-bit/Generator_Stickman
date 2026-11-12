// Ночная комната Димы — three.js r160, toon-рендер: MeshToonMaterial (3 ступени света) +
// чёрный контур пост-обработкой по глубине и нормалям, лица и мелочи — плоские «наклейки» на 3D-формах.
// window.renderAt(t) рисует кадр на момент t (0..3 с); render.js снимает его Playwright'ом.
import * as THREE from 'three';

const W = 1080, H = 1920, SS = 2;             // выход и суперсэмплинг (рисуем 2160×3840, сжимаем 2×2)
const INK = new THREE.Color(0x0b0c16);

// ---------- утилиты ----------
let _seed = 7;
const rnd = () => { _seed |= 0; _seed = (_seed + 0x6D2B79F5) | 0; let t = Math.imul(_seed ^ (_seed >>> 15), 1 | _seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const rr = (a, b) => a + (b - a) * rnd();
const lerp = (a, b, k) => a + (b - a) * k;
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const sstep = (a, b, x) => { const k = clamp((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k); };
function hash3(x, y, z) { const h = Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453; return h - Math.floor(h); }
function vnoise(x, y, z) {
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  const xf = x - xi, yf = y - yi, zf = z - zi;
  const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf), w = zf * zf * (3 - 2 * zf);
  const c = (a, b, d) => hash3(xi + a, yi + b, zi + d);
  return lerp(lerp(lerp(c(0, 0, 0), c(1, 0, 0), u), lerp(c(0, 1, 0), c(1, 1, 0), u), v),
              lerp(lerp(c(0, 0, 1), c(1, 0, 1), u), lerp(c(0, 1, 1), c(1, 1, 1), u), v), w);
}

// 3 ступени света: тень / полутон / свет
const GRAD = (() => { const t = new THREE.DataTexture(new Uint8Array([0, 135, 255]), 3, 1, THREE.RedFormat);
  t.minFilter = t.magFilter = THREE.NearestFilter; t.generateMipmaps = false; t.needsUpdate = true; return t; })();

function toon(color, o = {}) {
  const m = new THREE.MeshToonMaterial({ color, gradientMap: GRAD, ...o });
  return m;
}
// toon + ступенчатый ободок (для чёрного кота, иначе он сливается с ночью)
function toonRim(color, rim, o = {}) {
  const m = toon(color, o);
  m.onBeforeCompile = sh => {
    sh.uniforms.rimColor = { value: new THREE.Color(rim) };
    sh.fragmentShader = sh.fragmentShader
      .replace('void main() {', 'uniform vec3 rimColor;\nvoid main() {')
      .replace('#include <dithering_fragment>', `#include <dithering_fragment>
        float rimF = 1.0 - max(dot(normalize(vNormal), normalize(vViewPosition)), 0.0);
        gl_FragColor.rgb += rimColor * step(0.74, rimF);`);
  };
  m.customProgramCacheKey = () => 'rim';
  return m;
}
function canvasTex(w, h, draw, o = {}) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d'); draw(g, w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = o.linear ? THREE.NoColorSpace : THREE.SRGBColorSpace; t.anisotropy = 8;
  if (o.repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; }
  t.userData.g = g; t.userData.c = c; return t;
}
// скруглённый ящик: сетка с сгущением у краёв, вершины прижимаются к внутреннему ящику + r
function rbox(w, h, d, r, k = 5) {
  const ext = [w / 2, h / 2, d / 2]; r = Math.min(r, ...ext.map(e => e * 0.999));
  const axes = ext.map(E => { const c = []; for (let i = 0; i <= k; i++) c.push(-E + r * i / k); for (let i = 0; i <= k; i++) c.push(E - r + r * i / k); return c; });
  const n = 2 * k + 1, g = new THREE.BoxGeometry(2, 2, 2, n, n, n);
  const p = g.attributes.position, nm = g.attributes.normal, q = [0, 0, 0], inn = [0, 0, 0];
  for (let i = 0; i < p.count; i++) {
    for (let a = 0; a < 3; a++) { const v = p.getComponent(i, a); q[a] = axes[a][Math.round((v + 1) / 2 * n)]; inn[a] = clamp(q[a], -(ext[a] - r), ext[a] - r); }
    const dx = q[0] - inn[0], dy = q[1] - inn[1], dz = q[2] - inn[2], L = Math.hypot(dx, dy, dz) || 1;
    p.setXYZ(i, inn[0] + dx / L * r, inn[1] + dy / L * r, inn[2] + dz / L * r); nm.setXYZ(i, dx / L, dy / L, dz / L);
  }
  return g;
}
// пушистая сфера: шум выталкивает пучки шерсти — силуэт рваный, контур рисует «шерсть»
function fluffy(r, amp, freq, seed, wseg = 96, hseg = 64, view = V(0, 0.15, 1).normalize()) {
  const g = new THREE.SphereGeometry(r, wseg, hseg), p = g.attributes.position, v = new THREE.Vector3();
  for (let i = 0; i < p.count; i++) {
    v.fromBufferAttribute(p, i); const n = v.clone().normalize();
    const s = vnoise(n.x * freq + seed, n.y * freq * 1.7 + seed * 2, n.z * freq + seed * 3);
    const edge = 1 - sstep(0.3, 0.75, Math.abs(n.dot(view)));            // пучки — только по контуру
    const tuft = Math.pow(clamp((s - 0.45) / 0.55, 0, 1), 1.6) * (0.25 + 0.75 * edge);
    v.copy(n.multiplyScalar(r * (1 + amp * tuft))); p.setXYZ(i, v.x, v.y, v.z);
  }
  g.computeVertexNormals(); return g;
}
// трубка переменной толщины вдоль кривой
function tube(curve, n, radial, rFn, cap = true) {
  const fr = curve.computeFrenetFrames(n, false), pos = [], nor = [], uv = [], idx = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n, P = curve.getPointAt(t), N = fr.normals[i], B = fr.binormals[i], R = rFn(t);
    for (let j = 0; j <= radial; j++) {
      const a = j / radial * Math.PI * 2, d = N.clone().multiplyScalar(Math.cos(a)).add(B.clone().multiplyScalar(Math.sin(a)));
      const rj = typeof R === 'function' ? R(a) : R;
      pos.push(P.x + d.x * rj, P.y + d.y * rj, P.z + d.z * rj); nor.push(d.x, d.y, d.z); uv.push(t, j / radial);
    }
  }
  for (let i = 0; i < n; i++) for (let j = 0; j < radial; j++) {
    const a = i * (radial + 1) + j, b = a + radial + 1; idx.push(a, a + 1, b, b, a + 1, b + 1);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx); return g;
}
const mesh = (g, m, x = 0, y = 0, z = 0, parent) => { const o = new THREE.Mesh(g, m); o.position.set(x, y, z); (parent || scene).add(o); return o; };
const V = (x, y, z) => new THREE.Vector3(x, y, z);

// ---------- рендер, камера, свет ----------
const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H); document.body.appendChild(renderer.domElement);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFShadowMap; renderer.shadowMap.autoUpdate = false;
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x1b2350, 11, 42);
const camera = new THREE.PerspectiveCamera(34, W / H, 0.1, 80);
const CAM0 = V(0.1, 1.4, 3.45), CAM1 = V(0.08, 1.36, 3.05), LOOK = V(0.08, 1.04, -1.0);

scene.add(new THREE.AmbientLight(0x4d5a95, 1.25));
const hemi = new THREE.HemisphereLight(0x6070b8, 0x1a1830, 0.9); scene.add(hemi);
const moon = new THREE.DirectionalLight(0xa9bcff, 2.6);
{ const tgt = V(0.25, 0.55, -0.75), dir = V(-0.55, -1.15, 1.05).normalize();
  moon.position.copy(tgt.clone().addScaledVector(dir, -6)); moon.target.position.copy(tgt); scene.add(moon, moon.target);
  moon.castShadow = true; moon.shadow.mapSize.set(2048, 2048); moon.shadow.bias = -0.0008; moon.shadow.normalBias = 0.01;
  Object.assign(moon.shadow.camera, { left: -2.6, right: 2.6, top: 2.6, bottom: -2.6, near: 0.5, far: 14 }); }
const fill = new THREE.DirectionalLight(0x7c80c8, 1.05); fill.position.set(-2.5, 3.2, 5); scene.add(fill);

// ---------- небо, луна, дома напротив ----------
const sky = new THREE.ShaderMaterial({ uniforms: { t: { value: 0 } }, depthWrite: true, fog: false,
  vertexShader: 'varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }',
  fragmentShader: `varying vec2 vUv; uniform float t;
    float h(vec2 p){return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453);}
    void main(){ vec3 top=vec3(0.010,0.016,0.060), bot=vec3(0.075,0.095,0.230);
      vec3 c=mix(bot,top,smoothstep(0.28,0.95,vUv.y));
      vec2 g=floor(vUv*vec2(220.,140.)); float r=h(g);
      if(r>0.982 && vUv.y>0.42){ vec2 f=fract(vUv*vec2(220.,140.))-.5; c+=vec3(0.9,0.9,1.0)*smoothstep(0.32,0.,length(f))*(0.55+0.45*sin(t*2.7+r*60.)); }
      gl_FragColor=vec4(c,1.); }` });
mesh(new THREE.PlaneGeometry(90, 55), sky, 0, 14, -40);
// луна — наклейка с контуром и ореол
const moonTex = canvasTex(512, 512, (g) => {
  g.fillStyle = '#f2ecc8'; g.beginPath(); g.arc(256, 256, 200, 0, 7); g.fill();
  g.fillStyle = 'rgba(190,180,140,0.55)'; [[200, 210, 38], [300, 300, 28], [250, 330, 18], [320, 190, 22]].forEach(([x, y, r]) => { g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); });
  g.lineWidth = 12; g.strokeStyle = '#151524'; g.beginPath(); g.arc(256, 256, 200, 0, 7); g.stroke(); });
const glowTex = canvasTex(256, 256, (g) => { const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.25, 'rgba(255,255,255,0.45)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 256, 256); });
function sprite(tex, color, sx, sy, x, y, z, additive = false, opacity = 1, parent) {
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, color, transparent: true, depthWrite: false, opacity, fog: false,
    blending: additive ? THREE.AdditiveBlending : THREE.NormalBlending }));
  s.scale.set(sx, sy, 1); s.position.set(x, y, z); s.layers.set(1); (parent || scene).add(s); return s;
}
sprite(glowTex, 0x8090d0, 9, 9, 4.0, 7.7, -35, true, 0.65);
sprite(moonTex, 0xffffff, 2.5, 2.5, 4.0, 7.7, -34.9);
// дома напротив: тёмные коробки, сетка окон, часть горит тёплым
function buildingTex(cols, rows, seed) {
  _seed = seed;
  return canvasTex(cols * 32, rows * 40, (g, w, h) => {
    g.fillStyle = '#20263f'; g.fillRect(0, 0, w, h);
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      const lit = rnd() < 0.34, warm = rnd();
      g.fillStyle = lit ? (warm < 0.75 ? '#ffc56a' : '#ffe3a8') : '#141a2e';
      g.fillRect(c * 32 + 8, r * 40 + 9, 16, 22);
      if (lit && rnd() < 0.5) { g.fillStyle = 'rgba(120,70,40,0.6)'; g.fillRect(c * 32 + 8, r * 40 + 9, 7, 22); }
    }
  });
}
function building(x, z, w, h, d, seed) {
  const tex = buildingTex(Math.round(w / 0.5), Math.round(h / 0.55), seed);
  const m = new THREE.MeshBasicMaterial({ map: tex, color: 0xffffff });
  const side = new THREE.MeshBasicMaterial({ color: 0x151a2c });
  const b = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), [side, side, side, side, m, side]);
  b.position.set(x, h / 2 - 3, z); scene.add(b); return b;
}
building(4.0, -16, 6, 6.4, 3, 11);
building(-0.5, -23, 5, 7.6, 3, 23);
building(6.0, -30, 3, 8.8, 3, 5);

// ---------- комната ----------
const ROOM = { wallZ: -1.6, winX0: 0.32, winX1: 1.32, winY0: 1.22, winY1: 2.45, h: 2.8 };
const wallTex = canvasTex(256, 512, (g, w, h) => {
  g.fillStyle = '#9a8fae'; g.fillRect(0, 0, w, h);
  g.fillStyle = 'rgba(70,60,95,0.16)'; for (let x = 0; x < w; x += 64) g.fillRect(x, 0, 22, h);
  g.strokeStyle = 'rgba(60,50,85,0.42)'; g.lineWidth = 4; g.fillStyle = 'rgba(60,50,85,0.38)';
  const motif = (x, y) => { g.beginPath(); g.ellipse(x, y, 9, 15, 0, 0, 7); g.stroke(); g.beginPath(); g.moveTo(x, y + 15); g.quadraticCurveTo(x + 14, y + 34, x + 3, y + 52); g.stroke();
    g.beginPath(); g.arc(x - 12, y + 34, 5, 0, 7); g.fill(); g.beginPath(); g.arc(x + 16, y - 4, 4, 0, 7); g.fill(); };
  for (let y = 0; y < h; y += 128) { motif(64, y + 30); motif(192, y + 94); }
}, { repeat: true });
const wallMat = toon(0xffffff, { map: wallTex });
function wallPiece(x0, x1, y0, y1) {
  const g = new THREE.PlaneGeometry(x1 - x0, y1 - y0); const uv = g.attributes.uv, p = g.attributes.position;
  for (let i = 0; i < p.count; i++) uv.setXY(i, (p.getX(i) + (x0 + x1) / 2) / 0.42, (p.getY(i) + (y0 + y1) / 2) / 0.84);
  return mesh(g, wallMat, (x0 + x1) / 2, (y0 + y1) / 2, ROOM.wallZ);
}
wallPiece(-3, ROOM.winX0, 0, ROOM.h); wallPiece(ROOM.winX1, 3.5, 0, ROOM.h);
wallPiece(ROOM.winX0, ROOM.winX1, 0, ROOM.winY0); wallPiece(ROOM.winX0, ROOM.winX1, ROOM.winY1, ROOM.h);
// откосы окна
const revealM = toon(0x8e86a4);
{ const d = 0.28, z = ROOM.wallZ - d / 2;
  mesh(new THREE.BoxGeometry(0.02, ROOM.winY1 - ROOM.winY0, d), revealM, ROOM.winX0 - 0.01, (ROOM.winY0 + ROOM.winY1) / 2, z);
  mesh(new THREE.BoxGeometry(0.02, ROOM.winY1 - ROOM.winY0, d), revealM, ROOM.winX1 + 0.01, (ROOM.winY0 + ROOM.winY1) / 2, z);
  mesh(new THREE.BoxGeometry(ROOM.winX1 - ROOM.winX0, 0.02, d), revealM, (ROOM.winX0 + ROOM.winX1) / 2, ROOM.winY1 + 0.01, z); }
// рама с форточкой и подоконник
const frameM = toon(0xd9d6e2);
{ const z = ROOM.wallZ - 0.24, x0 = ROOM.winX0, x1 = ROOM.winX1, y0 = ROOM.winY0, y1 = ROOM.winY1, t = 0.055, xm = (x0 + x1) / 2;
  const bar = (cx, cy, w, h) => mesh(rbox(w, h, 0.06, 0.008, 2), frameM, cx, cy, z);
  bar(xm, y0 + t / 2, x1 - x0, t); bar(xm, y1 - t / 2, x1 - x0, t); bar(x0 + t / 2, (y0 + y1) / 2, t, y1 - y0); bar(x1 - t / 2, (y0 + y1) / 2, t, y1 - y0);
  bar(xm, (y0 + y1) / 2, 0.045, y1 - y0); bar(xm, y1 - 0.42, x1 - x0, 0.04);              // импост и форточка
  bar(xm + 0.25, y1 - 0.21, 0.035, 0.42);
  mesh(rbox(x1 - x0 + 0.16, 0.04, 0.36, 0.012, 2), frameM, xm, y0 - 0.02, ROOM.wallZ - 0.06);   // подоконник
  // кактус в горшке на подоконнике
  mesh(new THREE.CylinderGeometry(0.045, 0.035, 0.07, 24), toon(0xb0664a), x1 - 0.15, y0 + 0.035, ROOM.wallZ - 0.1);
  mesh(new THREE.CapsuleGeometry(0.026, 0.07, 6, 16), toon(0x4f8a5a), x1 - 0.15, y0 + 0.12, ROOM.wallZ - 0.1); }
// стекло — лёгкий холодный блик
{ const gm = new THREE.MeshBasicMaterial({ color: 0x8aa0ff, transparent: true, opacity: 0.07, depthWrite: false, blending: THREE.AdditiveBlending });
  const gl = mesh(new THREE.PlaneGeometry(ROOM.winX1 - ROOM.winX0, ROOM.winY1 - ROOM.winY0), gm, (ROOM.winX0 + ROOM.winX1) / 2, (ROOM.winY0 + ROOM.winY1) / 2, ROOM.wallZ - 0.235); gl.layers.set(1); }
// потолок и плинтус
mesh(new THREE.BoxGeometry(7, 0.08, 0.025), toon(0x6f6684), 0, 0.04, ROOM.wallZ + 0.013);
{ const c = mesh(new THREE.PlaneGeometry(8, 6), toon(0x4c4868), 0, ROOM.h, 1); c.rotation.x = Math.PI / 2; }
// шторы со складками
const curtainTex = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#b89aa6'; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(120,80,100,0.45)';
  for (let y = 0; y < h; y += 32) for (let x = (y / 32 % 2) * 16; x < w; x += 32) { g.beginPath(); g.arc(x + 8, y + 8, 4, 0, 7); g.fill(); } }, { repeat: true });
function curtain(x0, x1, y0, y1, z, folds, gather) {
  const w = x1 - x0, h = y1 - y0, g = new THREE.PlaneGeometry(w, h, 80, 40), p = g.attributes.position, uv = g.attributes.uv;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), y = p.getY(i), u = (x + w / 2) / w, v = (y + h / 2) / h;
    const k = lerp(1, gather, sstep(0.0, 0.55, 1 - v));                     // внизу подхвачено
    const nx = lerp(gather < 1 ? 0.5 : u, u, 1) ;
    p.setX(i, (u - 0.5) * w * k + (1 - k) * (gather < 1 ? -w * 0.18 : 0));
    p.setZ(i, 0.028 * Math.sin(u * folds * Math.PI * 2 + v * 0.8) * (0.7 + 0.3 * (1 - v)));
    uv.setXY(i, u * w / 0.3, v * h / 0.3); void nx;
  }
  g.computeVertexNormals();
  const m = mesh(g, toon(0xffffff, { map: curtainTex, side: THREE.DoubleSide }), (x0 + x1) / 2, (y0 + y1) / 2, z); return m;
}
curtain(0.06, 0.5, 0.95, 2.62, ROOM.wallZ + 0.07, 4.5, 0.75);
curtain(1.18, 1.62, 0.95, 2.62, ROOM.wallZ + 0.07, 4.5, 1);
mesh(new THREE.CylinderGeometry(0.012, 0.012, 1.9, 12), toon(0x5a4a40), 0.85, 2.64, ROOM.wallZ + 0.07).rotation.z = Math.PI / 2;
// пол: доски
const floorTex = canvasTex(512, 512, (g, w, h) => {
  _seed = 41; for (let r = 0; r < 4; r++) { const y = r * 128;
    let x = -rr(0, 300); while (x < w) { const L = rr(260, 420); g.fillStyle = `hsl(${rr(22, 30)},${rr(28, 36)}%,${rr(27, 33)}%)`; g.fillRect(x, y, L, 128);
      g.strokeStyle = 'rgba(25,15,10,0.85)'; g.lineWidth = 5; g.strokeRect(x, y, L, 128);
      g.strokeStyle = 'rgba(60,35,20,0.35)'; g.lineWidth = 2; for (let k = 0; k < 3; k++) { g.beginPath(); g.moveTo(x + 10, y + rr(20, 108)); g.bezierCurveTo(x + L * 0.3, y + rr(10, 118), x + L * 0.6, y + rr(10, 118), x + L - 10, y + rr(20, 108)); g.stroke(); }
      x += L; } }
}, { repeat: true });
floorTex.repeat.set(3, 6);
{ const f = mesh(new THREE.PlaneGeometry(8, 8), toon(0xffffff, { map: floorTex }), 0, 0, 2.4); f.rotation.x = -Math.PI / 2; f.rotation.z = Math.PI / 2; }
// коврик
const rugTex = canvasTex(512, 320, (g, w, h) => { g.fillStyle = '#6a2d36'; g.fillRect(0, 0, w, h); g.strokeStyle = '#c99a5a'; g.lineWidth = 10; g.strokeRect(26, 26, w - 52, h - 52);
  g.strokeStyle = '#2d3a5e'; g.lineWidth = 16; g.strokeRect(52, 52, w - 104, h - 104); g.fillStyle = '#c99a5a';
  for (let i = 0; i < 5; i++) { const x = 120 + i * 68; g.beginPath(); g.moveTo(x, 160 - 34); g.lineTo(x + 26, 160); g.lineTo(x, 160 + 34); g.lineTo(x - 26, 160); g.closePath(); g.fill(); }
  g.fillStyle = '#e7d3b0'; for (let x = 0; x < w; x += 14) { g.fillRect(x, 0, 5, 12); g.fillRect(x, h - 12, 5, 12); } });
mesh(rbox(1.5, 0.014, 0.95, 0.006, 2), toon(0xffffff, { map: rugTex }), -0.05, 0.007, -0.12);
// тапки
function slipper(x, z, ry) {
  const g = new THREE.Group(); g.position.set(x, 0.014, z); g.rotation.y = ry; scene.add(g);
  mesh(rbox(0.105, 0.024, 0.26, 0.04, 4), toon(0xa9a3b8), 0, 0.012, 0, g);
  const up = mesh(new THREE.CylinderGeometry(0.052, 0.052, 0.12, 28, 1, false, -Math.PI / 2, Math.PI), toon(0x5d6a9a), 0, 0.022, 0.055, g);
  up.rotation.x = Math.PI / 2; up.rotation.z = Math.PI / 2; up.scale.set(0.78, 1, 1);
  const toe = mesh(new THREE.SphereGeometry(0.052, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2), toon(0x5d6a9a), 0, 0.022, 0.115, g); toe.scale.set(1, 0.78, 0.5);
}
slipper(-0.32, -0.36, 0.3); slipper(-0.1, -0.3, -0.1);
// банка на полу у дивана
mesh(new THREE.CylinderGeometry(0.033, 0.033, 0.12, 24), toon(0x2f7a8a), 0.42, 0.06, -0.45);
mesh(new THREE.CylinderGeometry(0.028, 0.033, 0.012, 24), toon(0xb8bcc8), 0.42, 0.126, -0.45);

// ---------- полки, книги, растение, часы, картина ----------
const shelfM = toon(0x6a4a3a);
function shelf(y) { mesh(rbox(0.82, 0.03, 0.22, 0.008, 2), shelfM, -0.32, y, ROOM.wallZ + 0.11);
  [-0.64, 0.0].forEach(x => mesh(new THREE.BoxGeometry(0.02, 0.07, 0.15), toon(0x3a3438), x, y - 0.05, ROOM.wallZ + 0.08)); }
shelf(2.22); shelf(1.8);
const bookCols = [0x3a4a7a, 0x7a3434, 0xb08a3c, 0x3d6a52, 0x5a3a6e, 0x2f5d78, 0x8c5a3a];
function books(x0, y, n, seed) { _seed = seed; let x = x0;
  for (let i = 0; i < n; i++) { const w = rr(0.028, 0.05), h = rr(0.17, 0.25), d = rr(0.13, 0.17);
    const b = mesh(rbox(w, h, d, 0.004, 1), toon(bookCols[Math.floor(rnd() * bookCols.length)]), x + w / 2, y + h / 2 + 0.015, ROOM.wallZ + 0.11); x += w + 0.004;
    mesh(new THREE.BoxGeometry(w * 1.02, 0.012, d * 1.01), toon(0xd8cfa8), 0, h * 0.28, 0, b); } return x; }
{ const x = books(-0.7, 2.235, 6, 3); const lean = mesh(rbox(0.035, 0.22, 0.15, 0.004, 1), toon(0x2f5d78), x + 0.06, 2.235 + 0.105, ROOM.wallZ + 0.11); lean.rotation.z = -0.42; }
books(-0.7, 1.815, 3, 9);
// стопка лежащих книг
[0, 1, 2].forEach(i => mesh(rbox(0.2 - i * 0.02, 0.035, 0.15, 0.004, 1), toon(bookCols[(i * 3 + 1) % 7]), -0.11, 1.833 + i * 0.036, ROOM.wallZ + 0.11));
// горшок с плющом
{ const px = -0.08, py = 2.235, pz = ROOM.wallZ + 0.11;
  mesh(new THREE.CylinderGeometry(0.06, 0.045, 0.1, 24), toon(0xb5694a), px, py + 0.065, pz);
  const leafM = toon(0x4f8f5c), leafG = new THREE.SphereGeometry(0.03, 16, 10);
  [[0, 0.13, 0.02], [0.04, 0.14, -0.02], [-0.04, 0.135, 0.0]].forEach(([a, b, c]) => { const l = mesh(leafG, leafM, px + a, py + b, pz + c); l.scale.set(1, 0.55, 1.4); });
  const vine = new THREE.CatmullRomCurve3([V(px + 0.05, py + 0.1, pz + 0.04), V(px + 0.09, py - 0.05, pz + 0.07), V(px + 0.06, py - 0.25, pz + 0.08), V(px + 0.1, py - 0.42, pz + 0.07)]);
  mesh(tube(vine, 40, 6, () => 0.004), toon(0x3d6e48));
  for (let i = 1; i < 9; i++) { const P = vine.getPointAt(i / 9); const l = mesh(leafG, leafM, P.x + (i % 2 ? 0.022 : -0.02), P.y, P.z + 0.01); l.scale.set(0.8, 0.45, 1.1); l.rotation.z = i % 2 ? -0.6 : 0.6; } }
// цифровые часы 01:47 — сегменты рисует код
const SEG = { 0: 'abcdef', 1: 'bc', 4: 'bcfg', 7: 'abc' };
const clockTex = canvasTex(512, 200, (g, w, h) => {
  g.fillStyle = '#0d0b10'; g.fillRect(0, 0, w, h);
  const digit = (x, d) => { const on = SEG[d], s = 'abcdefg', L = 62, T = 13;
    const segs = { a: [x, 40, L, T, 0], b: [x + L, 40, T, L, 1], c: [x + L, 40 + L + T, T, L, 1], d: [x, 40 + 2 * L + T, L, T, 0], e: [x - T, 40 + L + T, T, L, 1], f: [x - T, 40, T, L, 1], g: [x, 40 + L, L, T, 0] };
    for (const k of s) { const [sx, sy, sw, sh] = segs[k]; g.fillStyle = on.includes(k) ? '#ff5a3a' : 'rgba(255,90,58,0.08)';
      g.beginPath(); g.roundRect(sx + 3, sy + 3, sw - 2, sh - 2, 5); g.fill(); } };
  digit(40, 0); digit(150, 1); digit(290, 4); digit(400, 7);
  g.fillStyle = '#ff5a3a'; g.beginPath(); g.arc(250, 82, 9, 0, 7); g.fill(); g.beginPath(); g.arc(250, 132, 9, 0, 7); g.fill(); });
{ const cx = -0.45, cy = 1.815, cz = ROOM.wallZ + 0.12;
  mesh(rbox(0.2, 0.085, 0.07, 0.012, 3), toon(0x24222c), cx, cy + 0.0425, cz);
  const face = mesh(new THREE.PlaneGeometry(0.17, 0.066), new THREE.MeshBasicMaterial({ map: clockTex, fog: false }), cx, cy + 0.0425, cz + 0.0355); face.layers.set(1);
  sprite(glowTex, 0xff4a2a, 0.36, 0.2, cx, cy + 0.045, cz + 0.05, true, 0.32);
  const cl = new THREE.PointLight(0xff5030, 0.05, 0.7, 2); cl.position.set(cx, cy + 0.05, cz + 0.08); scene.add(cl);
  // кружка рядом
  mesh(new THREE.CylinderGeometry(0.035, 0.032, 0.08, 24), toon(0xdedbe6), cx + 0.2, cy + 0.055, cz);
  mesh(new THREE.TorusGeometry(0.022, 0.007, 8, 16), toon(0xdedbe6), cx + 0.24, cy + 0.058, cz); }
// картина над диваном (горы, без надписей)
{ const art = canvasTex(256, 192, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#e6b38a'); gr.addColorStop(1, '#f2d7b0'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    g.fillStyle = '#f7efd6'; g.beginPath(); g.arc(180, 60, 22, 0, 7); g.fill();
    g.fillStyle = '#6a7fa8'; g.beginPath(); g.moveTo(0, 150); g.lineTo(70, 70); g.lineTo(130, 130); g.lineTo(190, 80); g.lineTo(256, 140); g.lineTo(256, 192); g.lineTo(0, 192); g.fill();
    g.fillStyle = '#3e5070'; g.beginPath(); g.moveTo(0, 175); g.lineTo(90, 120); g.lineTo(256, 180); g.lineTo(256, 192); g.lineTo(0, 192); g.fill(); });
  mesh(rbox(0.42, 0.32, 0.025, 0.006, 2), toon(0x2e2a30), -0.42, 1.36, ROOM.wallZ + 0.013);
  mesh(new THREE.PlaneGeometry(0.37, 0.27), toon(0xffffff, { map: art }), -0.42, 1.36, ROOM.wallZ + 0.027); }

// ---------- диван ----------
const sofaM = toon(0x7d4d52), sofaD = toon(0x6a3f45);
mesh(rbox(2.9, 0.3, 0.86, 0.05), sofaD, 0, 0.27, -1.07);
mesh(rbox(2.86, 0.025, 0.02, 0.008, 2), toon(0x5a343a), 0, 0.2, -0.635);
mesh(rbox(2.9, 0.62, 0.2, 0.06), sofaD, 0, 0.66, -1.48);
[-0.6, 0.6].forEach(x => { mesh(rbox(1.2, 0.15, 0.8, 0.06), sofaM, x, 0.485, -1.04);
  const b = mesh(rbox(1.18, 0.5, 0.22, 0.1), sofaM, x, 0.8, -1.32); b.rotation.x = -0.13; });
[-1.36, 1.36].forEach(x => mesh(rbox(0.22, 0.42, 0.9, 0.09), sofaM, x, 0.56, -1.06));
[[-1.3, -0.68], [1.3, -0.68]].forEach(([x, z]) => mesh(new THREE.CylinderGeometry(0.025, 0.018, 0.12, 12), toon(0x2a2026), x, 0.06, z));
// подушка за спиной Димы
{ const pt = canvasTex(128, 128, (g) => { g.fillStyle = '#c8c2d8'; g.fillRect(0, 0, 128, 128); g.strokeStyle = 'rgba(110,95,140,0.5)'; g.lineWidth = 6;
    for (let i = -128; i < 128; i += 32) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i + 128, 128); g.stroke(); } }, { repeat: true });
  const p = mesh(rbox(0.5, 0.42, 0.16, 0.08), toon(0xffffff, { map: pt }), -0.62, 0.86, -1.2); p.rotation.set(-0.2, 0.25, 0.18); }

// ---------- плед в зелёную клетку ----------
const plaidTex = canvasTex(256, 256, (g, w, h) => {
  g.fillStyle = '#3f6d4c'; g.fillRect(0, 0, w, h);
  g.fillStyle = 'rgba(25,55,35,0.55)'; g.fillRect(0, 0, 112, h); g.fillRect(0, 0, w, 112);
  g.fillStyle = 'rgba(20,40,28,0.45)'; g.fillRect(0, 0, 112, 112);
  g.fillStyle = 'rgba(210,200,120,0.55)'; g.fillRect(150, 0, 6, h); g.fillRect(0, 150, w, 6);
  g.fillStyle = 'rgba(120,40,40,0.5)'; g.fillRect(200, 0, 4, h); g.fillRect(0, 200, w, 4);
}, { repeat: true });
const LEGS = [ // капсулы ног под пледом: (a, b, радиус)
  [V(-0.40, 0.62, -0.98), V(-0.02, 0.73, -0.90), 0.085], [V(-0.02, 0.73, -0.90), V(0.30, 0.63, -0.86), 0.07],
  [V(-0.40, 0.62, -1.10), V(-0.04, 0.70, -1.06), 0.085], [V(-0.04, 0.70, -1.06), V(0.27, 0.62, -1.04), 0.07],
  [V(0.30, 0.63, -0.86), V(0.33, 0.72, -0.84), 0.045], [V(0.27, 0.62, -1.04), V(0.30, 0.71, -1.03), 0.045], // ступни
  [V(-0.55, 0.62, -1.05), V(-0.40, 0.66, -1.04), 0.13]];                                                    // таз
function plaidHeight(x, z) {
  let y = 0.565, best = -1;
  for (const [a, b, R] of LEGS) {
    const ab = b.clone().sub(a), ap = V(x - a.x, 0, z - a.z), L2 = ab.x * ab.x + ab.z * ab.z;
    const t = clamp((ap.x * ab.x + ap.z * ab.z) / L2, 0, 1), px = a.x + ab.x * t, pz = a.z + ab.z * t, d = Math.hypot(x - px, z - pz);
    const R2 = R + 0.07, yc = a.y + ab.y * t; if (d < R2) { const top = yc + Math.sqrt(R2 * R2 - d * d) * (R / R2) * 1.05; best = Math.max(best, top); }
  }
  // мягкий максимум: ткань перекидывается между буграми
  if (best > y) y = y + (best - y);
  return y + 0.012 * (vnoise(x * 9, 0, z * 9) - 0.5);
}
{
  const nu = 160, nv = 90, X0 = -0.95, X1 = 1.05, pos = [], uv = [], idx = [];
  for (let j = 0; j <= nv; j++) for (let i = 0; i <= nu; i++) {
    const u = i / nu, v = j / nv, x = lerp(X0, X1, u); let y, z;
    if (v < 0.72) { z = lerp(-1.33, -0.66, v / 0.72); y = plaidHeight(x, z); }
    else { const s = (v - 0.72) / 0.28, a = s * Math.PI / 2, y0 = plaidHeight(x, -0.66);
      z = -0.66 + 0.06 * Math.sin(a) + 0.018 * Math.sin(x * 24 + 1.3) * s; y = y0 - 0.06 * (1 - Math.cos(a)) - s * s * 0.22; }
    const hang = (X1 - x) < 0.2 ? 0 : 0; void hang;
    pos.push(x, y, z); uv.push(u * 2.0 / 0.32, v * 1.25 / 0.32);
  }
  for (let j = 0; j < nv; j++) for (let i = 0; i < nu; i++) { const a = j * (nu + 1) + i, b = a + nu + 1; idx.push(a, a + 1, b, b, a + 1, b + 1); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx); g.computeVertexNormals();
  mesh(g, toon(0xffffff, { map: plaidTex, side: THREE.DoubleSide }));
}

// ---------- Дима ----------
const SKIN = 0xe9c29f, HOOD = 0xc9a03a, HAIR = 0x4a2b1d;
const skinM = toon(SKIN), hoodM = toon(HOOD), hairM = toon(HAIR);
const dima = new THREE.Group(); dima.position.set(-0.3, 0, -0.95); scene.add(dima);
{ const t = mesh(new THREE.CapsuleGeometry(0.165, 0.28, 10, 32), hoodM, 0, 0.84, -0.09, dima); t.scale.set(1.18, 1, 0.78); t.rotation.set(-0.3, 0, 0.06);
  // капюшон за шеей и шнурки
  const hood = mesh(new THREE.TorusGeometry(0.105, 0.05, 14, 40), hoodM, 0.0, 1.13, -0.2, dima); hood.rotation.set(1.25, 0, 0); hood.scale.set(1.15, 1, 1);
  [-0.04, 0.045].forEach((x, i) => { const s = mesh(new THREE.CylinderGeometry(0.006, 0.006, 0.17, 8), toon(0xe8e2d0), x, 1.0, 0.03 + i * 0.005, dima); s.rotation.set(-0.3, 0, i ? -0.08 : 0.1); });
  // карман-кенгуру
  const pk = mesh(rbox(0.26, 0.12, 0.03, 0.02, 2), toon(0xb48d30), 0.0, 0.74, 0.07, dima); pk.rotation.x = -0.3; }
mesh(new THREE.CylinderGeometry(0.05, 0.055, 0.12, 20), skinM, 0.02, 1.17, -0.14, dima);
const head = new THREE.Group(); head.position.set(0.04, 1.35, -0.1); head.rotation.set(0.16, 0.34, -0.1); dima.add(head);
const HEAD_R = 0.14, HEAD_S = [1, 1.13, 0.98];
// форма головы: овал, книзу сужается к подбородку и чуть выдаётся вперёд
function headShape(g) { const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) { let x = p.getX(i), y = p.getY(i), z = p.getZ(i); const r = Math.hypot(x, y, z), ny = y / r;
    const low = clamp(-ny, 0, 1), squeeze = 1 - 0.2 * low * low;
    x *= squeeze * HEAD_S[0]; z = z * HEAD_S[2] * (1 - 0.1 * low * low) + (z > 0 ? 0.018 * low : 0); y *= HEAD_S[1] * (1 + 0.06 * low);
    p.setXYZ(i, x, y, z); }
  g.computeVertexNormals(); return g; }
{ const h = mesh(headShape(new THREE.SphereGeometry(HEAD_R, 72, 48)), skinM, 0, 0, 0, head);
  [-1, 1].forEach(s => { const e = mesh(new THREE.SphereGeometry(0.034, 24, 16), skinM, s * 0.137, -0.005, -0.01, head); e.scale.set(0.5, 1, 0.8); });
  const nose = mesh(new THREE.SphereGeometry(0.013, 24, 16), skinM, 0.004, -0.03, 0.138, head); nose.scale.set(0.85, 1.2, 1.0);
  // волосы: шапка + торчащие пряди (сзади — вверх и назад)
  const cap = mesh(new THREE.SphereGeometry(HEAD_R * 1.05, 64, 32, 0, Math.PI * 2, 0, 1.3), hairM, 0, 0.02, -0.018, head); cap.scale.set(1.04, 1.12, 1.03); cap.rotation.x = -0.42;
  // пряди: изогнутые рожки по поверхности шапки; сзади и на макушке торчат наружу и назад
  const onHead = (th, ph, k = 1.02) => V(Math.sin(th) * Math.sin(ph) * HEAD_R * k, Math.cos(th) * HEAD_R * 1.13 * k + 0.012, Math.sin(th) * Math.cos(ph) * HEAD_R * k);
  const clump = (th, ph, len, r, up, bend, twist = 0) => {
    const base = onHead(th, ph, 0.92), n = base.clone().normalize();
    const dir = up < -0.5 ? n.clone().add(V(0, up, 0.25)).normalize()
      : n.clone().multiplyScalar(0.6).add(V(0, up * 0.4, -0.8)).add(V(Math.sin(ph + twist), 0, 0).multiplyScalar(0.3)).normalize();
    const side = V(0, 1, 0).cross(dir).normalize().multiplyScalar(bend);
    const c = new THREE.CatmullRomCurve3([base, base.clone().addScaledVector(dir, len * 0.45).addScaledVector(side, len * 0.12),
      base.clone().addScaledVector(dir, len).addScaledVector(side, len * 0.4).add(V(0, -len * 0.12 * (up < 0 ? 1 : 0), 0))]);
    mesh(tube(c, 24, 12, t => r * Math.pow(1 - t, 0.85) + 0.0015), hairM, 0, 0, 0, head);
  };
  _seed = 5;
  for (let i = 0; i < 14; i++) { const ph = Math.PI + rr(-1.5, 1.5), th = rr(0.5, 1.35);                   // затылок — торчит назад
    clump(th, ph, rr(0.07, 0.12), rr(0.03, 0.042), rr(0.0, 0.5), rr(-0.7, 0.7), rr(-0.5, 0.5)); }
  for (let i = 0; i < 7; i++) clump(rr(0.15, 0.6), rr(-1.6, 1.6), rr(0.07, 0.11), rr(0.032, 0.042), rr(0.3, 0.7), rr(-0.6, 0.6));   // макушка — назад
  [[0.62, -0.7], [0.55, -0.25], [0.6, 0.2], [0.66, 0.6], [0.75, 0.95]].forEach(([th, ph], i) =>                         // чёлка на лоб
    clump(th, ph, 0.075 + 0.015 * (i % 2), 0.032, -0.9, i % 2 ? 0.5 : -0.4));
  [-1, 1].forEach(s => clump(1.2, s * 1.55, 0.05, 0.03, -1.2, 0.2 * s));                                               // виски
}
// лицо — наклейка на сферу головы: глаза, мешки, брови, рот, щетина (перерисовывается для моргания)
const FACE = { phi0: Math.PI / 2 - 1.15, phiL: 2.3, th0: 0.75, thL: 1.6 };
const faceTex = canvasTex(1024, Math.round(1024 * FACE.thL * HEAD_S[1] / FACE.phiL), () => {});
function drawDimaFace(lid, look) {
  const g = faceTex.userData.g, w = 1024, h = faceTex.userData.c.height; g.clearRect(0, 0, w, h);
  const ink = '#14111c', ex = [512 - 132, 512 + 132], ey = 330, rx = 128, ry = 138;
  // щетина: точки по нижней части лица
  g.fillStyle = 'rgba(80,60,90,0.16)'; g.beginPath(); g.ellipse(512, 610, 230, 150, 0, 0.12, Math.PI - 0.12); g.fill();
  _seed = 77; g.fillStyle = 'rgba(60,40,50,0.32)';
  for (let i = 0; i < 520; i++) { const a = rr(0.05, Math.PI - 0.05), r = Math.sqrt(rr(0.15, 1)); const x = 512 + Math.cos(a) * 230 * r, y = 585 + Math.sin(a) * 175 * r;
    if (Math.abs(x - 512) < 80 && y < 625) continue; g.beginPath(); g.arc(x, y, rr(2, 3.5), 0, 7); g.fill(); }
  for (const [k, cx] of ex.entries()) {
    // мешки под глазами
    g.fillStyle = 'rgba(85,50,100,0.7)'; g.beginPath(); g.ellipse(cx, ey + 70, rx * 0.98, 84, 0, 0.0, Math.PI); g.fill();
    g.strokeStyle = ink; g.lineWidth = 7; g.beginPath(); g.ellipse(cx, ey + 92, rx * 0.74, 62, 0, 0.3, Math.PI - 0.3); g.stroke();
    g.lineWidth = 5; g.beginPath(); g.ellipse(cx, ey + 112, rx * 0.55, 50, 0, 0.6, Math.PI - 0.6); g.stroke();
    // белок
    g.save(); g.beginPath(); g.ellipse(cx, ey, rx, ry, 0, 0, 7); g.clip();
    g.fillStyle = '#f3f0ea'; g.fillRect(cx - rx, ey - ry, rx * 2, ry * 2);
    g.fillStyle = ink; g.beginPath(); g.arc(cx + look[0], ey + look[1], 19, 0, 7); g.fill();
    // верхнее веко (усталость) — цвет кожи сверху до линии
    const ly = ey - ry + lid * ry * 2;
    g.fillStyle = '#d9ad8c'; g.beginPath(); g.moveTo(cx - rx - 5, ey - ry - 5); g.lineTo(cx + rx + 5, ey - ry - 5); g.lineTo(cx + rx + 5, ly + (k ? 6 : -6));
    g.quadraticCurveTo(cx, ly + 22, cx - rx - 5, ly + (k ? -6 : 6)); g.closePath(); g.fill();
    g.restore();
    g.strokeStyle = ink; g.lineWidth = 9; g.beginPath(); g.ellipse(cx, ey, rx, ry, 0, 0, 7); g.stroke();
    g.lineWidth = 11; g.beginPath(); g.moveTo(cx - rx + 4, ly + (k ? -6 : 6)); g.quadraticCurveTo(cx, ly + 22, cx + rx - 4, ly + (k ? 6 : -6)); g.stroke();
    // бровь
    g.lineWidth = 9; g.beginPath(); g.moveTo(cx - 95, ey - ry - 32 + (k ? 6 : -8)); g.quadraticCurveTo(cx, ey - ry - 58, cx + 95, ey - ry - 34 + (k ? -8 : 6)); g.stroke();
  }
  // рот: короткая усталая линия
  g.strokeStyle = ink; g.lineWidth = 8; g.beginPath(); g.moveTo(470, 596); g.quadraticCurveTo(515, 586, 560, 600); g.stroke();
  faceTex.needsUpdate = true;
}
{ const g = new THREE.SphereGeometry(HEAD_R * 1.006, 96, 64, FACE.phi0, FACE.phiL, FACE.th0, FACE.thL);
  headShape(g); const f = mesh(g, toon(0xffffff, { map: faceTex, transparent: true, alphaTest: 0.02, depthWrite: false }), 0, 0, 0, head);
  f.layers.set(1); f.renderOrder = 2; }
// ---------- телефон (iPhone 14 Pro, спиной к зрителю) в правой руке + свет экрана ----------
const phone = new THREE.Group(); scene.add(phone);
const PHONE_POS = V(-0.05, 1.17, -0.7);
const PW = 0.1, PH = 0.205, PD = 0.013;
{ phone.position.copy(PHONE_POS);
  const eyeW = head.localToWorld(V(0, 0.01, 0.12));
  phone.lookAt(PHONE_POS.clone().multiplyScalar(2).sub(eyeW));         // +z (спинка) — от лица Димы
  phone.rotateZ(0.12); phone.rotateY(0.35);
  const black = toon(0x16171d);
  mesh(rbox(PW, PH, PD, 0.014, 4), black, 0, 0, 0, phone);
  mesh(rbox(PW * 1.004, PH * 1.002, PD * 0.55, 0.014, 3), toon(0x6a6c78), 0, 0, 0, phone);  // стальная рамка
  const bx = -PW / 2 + 0.029, by = PH / 2 - 0.03;                                         // блок камер: верхний угол (слева со спины)
  mesh(rbox(0.046, 0.048, 0.004, 0.011, 3), toon(0x24252c), bx, by, PD / 2 + 0.0015, phone);
  [[-0.0095, 0.0105], [-0.0095, -0.0105], [0.011, 0.0]].forEach(([x, y]) => {
    mesh(new THREE.CylinderGeometry(0.009, 0.009, 0.005, 28), toon(0x4a4c58), bx + x, by + y, PD / 2 + 0.005, phone).rotation.x = Math.PI / 2;
    mesh(new THREE.CylinderGeometry(0.006, 0.006, 0.002, 28), toon(0x07070b), bx + x, by + y, PD / 2 + 0.0078, phone).rotation.x = Math.PI / 2; });
  mesh(new THREE.SphereGeometry(0.003, 10, 8), toon(0xf0e6c0), bx + 0.011, by + 0.0145, PD / 2 + 0.004, phone);
  // экран (к Диме): светящаяся плоскость
  const scr = mesh(new THREE.PlaneGeometry(PW * 0.9, PH * 0.94), new THREE.MeshBasicMaterial({ color: 0xd2e4ff, fog: false }), 0, 0, -PD / 2 - 0.0006, phone);
  scr.rotation.y = Math.PI; scr.layers.set(1);
  // кисть: ладонь у левого ребра, пальцы поперёк спинки, кончики за правым ребром
  const palm = mesh(new THREE.SphereGeometry(0.046, 28, 20), skinM, -PW / 2 - 0.004, -0.058, 0.004, phone); palm.scale.set(0.62, 1.25, 1.05);
  [-0.012, -0.038, -0.064, -0.088].forEach((y, i) => {
    const c = new THREE.CatmullRomCurve3([V(-PW / 2 + 0.01, y - 0.004, PD / 2 + 0.004), V(0, y, PD / 2 + 0.009), V(PW / 2 - 0.004, y + 0.002, PD / 2 + 0.006),
      V(PW / 2 + 0.008, y + 0.003, -0.001), V(PW / 2 + 0.002, y + 0.004, -PD / 2 - 0.004)]);
    mesh(tube(c, 30, 14, t => 0.0115 - 0.0025 * t - i * 0.0006), skinM, 0, 0, 0, phone); });
  // большой палец — на шарнире у левого ребра, над экраном; листает
  const th = new THREE.Group(); th.position.set(-PW / 2 - 0.004, -0.04, -PD / 2 - 0.008); phone.add(th);
  const tm = mesh(new THREE.CapsuleGeometry(0.0135, 0.066, 6, 14), skinM, 0.0, 0.04, -0.003, th); tm.rotation.z = -0.62;
  const tn = mesh(new THREE.SphereGeometry(0.0085, 12, 8), toon(0xf2d2c0), 0.024, 0.07, -0.012, th); tn.scale.set(1, 1.3, 0.5); tn.rotation.z = -0.62;
  phone.userData.thumb = th;
}
// руки: правая (слева от зрителя) — через грудь к телефону; левая лежит на пледе
function sleeve(pts, r, parent) { const c = new THREE.CatmullRomCurve3(pts); mesh(tube(c, 48, 18, t => r * (1 - 0.15 * t)), hoodM, 0, 0, 0, parent);
  const e = pts[pts.length - 1]; mesh(new THREE.SphereGeometry(r * 0.9, 20, 14), hoodM, e.x, e.y, e.z, parent); return c; }
{ const palmW = phone.localToWorld(V(-PW / 2 - 0.004, -0.085, 0.004)); dima.updateMatrixWorld(); const pl = dima.worldToLocal(palmW.clone());
  const cuff = V(pl.x - 0.035, pl.y - 0.06, pl.z - 0.02);
  sleeve([V(-0.17, 1.08, -0.15), V(-0.2, 0.9, -0.02), V(-0.06, 0.86, 0.12), cuff], 0.056, dima);
  mesh(tube(new THREE.CatmullRomCurve3([cuff, cuff.clone().lerp(pl, 0.5).add(V(0, 0, 0.004)), pl]), 12, 14, () => 0.026), skinM, 0, 0, 0, dima); }
sleeve([V(0.17, 1.08, -0.15), V(0.26, 0.9, -0.04), V(0.25, 0.8, 0.1), V(0.14, 0.77, 0.17)], 0.056, dima);
{ const h = new THREE.Group(); h.position.set(0.09, 0.765, 0.2); h.rotation.set(0.2, 0.5, 0.1); dima.add(h);
  const p = mesh(new THREE.SphereGeometry(0.042, 24, 16), skinM, 0, 0, 0, h); p.scale.set(1.15, 0.6, 1.0);
  [-0.028, -0.009, 0.01, 0.028].forEach((x, i) => { const f = mesh(new THREE.CapsuleGeometry(0.011, 0.028, 6, 10), skinM, x, -0.006, 0.042 - Math.abs(i - 1.5) * 0.004, h); f.rotation.x = 1.3; });
  const t = mesh(new THREE.CapsuleGeometry(0.012, 0.03, 6, 10), skinM, -0.045, 0.004, 0.012, h); t.rotation.set(1.2, 0, 0.6); }

// свет экрана на лицо (холодный) и ореол
const screenN = V(0, 0, -1).applyQuaternion(phone.quaternion);
const phoneLight = new THREE.PointLight(0xa9c8ff, 0.15, 1.8, 2); phoneLight.position.copy(PHONE_POS).addScaledVector(screenN, 0.13); scene.add(phoneLight);
const phoneGlow = sprite(glowTex, 0x9fc2ff, 0.55, 0.55, 0, 0, 0, true, 0.38); phoneGlow.position.copy(PHONE_POS).addScaledVector(screenN, 0.03);

// ---------- кот ----------
const CAT = 0x24242f, catM = toonRim(CAT, 0x4c5a9a), catIn = toon(0x7a4f48);
const cat = new THREE.Group(); scene.add(cat);
const CAT_POS = V(0.47, plaidHeight(0.47, -0.8) - 0.01, -0.78); cat.position.copy(CAT_POS); cat.rotation.y = -0.08;
{ const body = mesh(fluffy(0.15, 0.03, 4, 1.3), catM, 0, 0.15, -0.01, cat); body.scale.set(1.0, 1.05, 0.9);
  const chest = mesh(fluffy(0.1, 0.04, 4, 4.1), catM, 0, 0.2, 0.07, cat); chest.scale.set(1, 1.1, 0.8);
  // задние лапы подошвами к зрителю, передние столбиками
  [-1, 1].forEach(s => { const f = mesh(fluffy(0.055, 0.02, 4, 2 + s), catM, s * 0.105, 0.04, 0.085, cat); f.scale.set(0.95, 0.85, 0.7);
    const fl = mesh(new THREE.CapsuleGeometry(0.036, 0.055, 6, 16), catM, s * 0.045, 0.06, 0.115, cat); fl.scale.set(1, 1, 0.9); });
}
const catHead = new THREE.Group(); catHead.position.set(0, 0.4, 0.02); cat.add(catHead);
const CH_R = 0.13, CH_S = [1.14, 1, 1];
{ const h = mesh(fluffy(CH_R, 0.03, 4, 7.7), catM, 0, 0, 0, catHead); h.scale.set(...CH_S);
  [-1, 1].forEach(s => { const c = mesh(fluffy(0.06, 0.22, 5, 3 + s * 2), catM, s * 0.115, -0.045, -0.005, catHead); c.scale.set(1, 0.75, 0.75); });
  // правое ухо (от зрителя) стоит
  const er = mesh(new THREE.ConeGeometry(0.055, 0.115, 24), catM, 0.083, 0.115, -0.01, catHead); er.rotation.set(-0.1, 0, -0.36);
  const eri = mesh(new THREE.ConeGeometry(0.033, 0.075, 20), catIn, 0.08, 0.108, 0.012, catHead); eri.rotation.set(-0.1, 0, -0.36); eri.scale.set(1, 1, 0.4);
  // левое ухо загнуто вниз: основание + сложенный кончик
  const el = mesh(new THREE.CylinderGeometry(0.03, 0.056, 0.06, 24), catM, -0.083, 0.1, -0.01, catHead); el.rotation.set(-0.1, 0, 0.36);
  const eli = mesh(new THREE.CylinderGeometry(0.018, 0.034, 0.045, 20), catIn, -0.08, 0.098, 0.014, catHead); eli.rotation.set(-0.1, 0, 0.36); eli.scale.set(1, 1, 0.4);
  const tip = new THREE.Group(); tip.position.set(-0.097, 0.127, 0.0); catHead.add(tip);
  tip.quaternion.setFromUnitVectors(V(0, 1, 0), V(-0.45, -0.55, 0.7).normalize());
  const tc = mesh(new THREE.ConeGeometry(0.031, 0.058, 20), catM, 0, 0.027, 0, tip); tc.scale.set(1, 1, 0.55);
}
// пучки шерсти: щёки, грудка, макушка, бока
{ const tuft = (par, x, y, z, rz, rx = 0, sc = 1) => { const L = 0.055 * sc, d = V(-Math.sin(rz), Math.cos(rz), 0).applyAxisAngle(V(1, 0, 0), rx);
    const b = V(x, y, z).addScaledVector(d, -0.012), side = V(0, 0, 1).cross(d).multiplyScalar(Math.sign(-rz) * 0.35);
    const c = new THREE.CatmullRomCurve3([b, b.clone().addScaledVector(d, L * 0.5).addScaledVector(side, L * 0.15), b.clone().addScaledVector(d, L).addScaledVector(side, L * 0.55)]);
    mesh(tube(c, 16, 10, t => 0.02 * sc * Math.pow(1 - t, 0.9) + 0.001), catM, 0, 0, 0, par); };
  [-1, 1].forEach(s => { tuft(catHead, s * 0.155, -0.04, 0.0, s * -2.0, 0, 1.1); tuft(catHead, s * 0.15, -0.08, 0.0, s * -2.4, 0, 0.9); tuft(catHead, s * 0.16, -0.0, -0.01, s * -1.7, 0, 0.8);
  });
  [-0.04, 0, 0.04].forEach((x, i) => tuft(cat, x, 0.255 - (i % 2) * 0.01, 0.15, Math.PI + x * 3, -0.5, 0.8));
}
// лицо кота — наклейка: зелёные глаза с бликом, по 2 оранжевые полоски, нос, рот
const CFACE = { phi0: Math.PI / 2 - 1.2, phiL: 2.4, th0: 0.7, thL: 1.7 };
const catFaceH = Math.round(1024 * CFACE.thL / (CFACE.phiL * CH_S[0]));
const catFaceTex = canvasTex(1024, catFaceH, () => {}), catGlowTex = canvasTex(1024, catFaceH, () => {});
function drawCatFace(lid) {
  const g = catFaceTex.userData.g, e = catGlowTex.userData.g, w = 1024, h = catFaceH; g.clearRect(0, 0, w, h); e.fillStyle = '#000'; e.fillRect(0, 0, w, h);
  const ink = '#0a0a10', ey = 300, rx = 112, ry = 122;
  for (const cx of [512 - 178, 512 + 178]) {
    g.save(); g.beginPath(); g.ellipse(cx, ey, rx, ry, 0, 0, 7); g.clip();
    g.fillStyle = '#a8da3c'; g.fillRect(cx - rx, ey - ry, 2 * rx, 2 * ry);
    g.fillStyle = 'rgba(60,110,20,0.55)'; g.beginPath(); g.ellipse(cx, ey + 70, rx, 60, 0, 0, 7); g.fill();
    g.fillStyle = ink; g.beginPath(); g.ellipse(cx + (cx < 512 ? 8 : -8), ey + 4, 40, 74, 0, 0, 7); g.fill();
    g.fillStyle = '#ffffff'; g.beginPath(); g.arc(cx + 22, ey - 34, 15, 0, 7); g.fill();
    if (lid > 0.01) { const ly = ey - ry + lid * ry * 2.05; g.fillStyle = '#26262f'; g.fillRect(cx - rx - 4, ey - ry - 4, 2 * rx + 8, ly - (ey - ry) + 4); }
    g.restore();
    e.save(); e.beginPath(); e.ellipse(cx, ey, rx, ry, 0, 0, 7); e.clip(); e.fillStyle = '#7fb02a'; e.fillRect(cx - rx, ey - ry, 2 * rx, 2 * ry);
    e.fillStyle = '#000'; e.beginPath(); e.ellipse(cx + (cx < 512 ? 8 : -8), ey + 4, 40, 74, 0, 0, 7); e.fill();
    if (lid > 0.01) { const ly = ey - ry + lid * ry * 2.05; e.fillRect(cx - rx - 4, ey - ry - 4, 2 * rx + 8, ly - (ey - ry) + 4); }
    e.restore();
    g.strokeStyle = ink; g.lineWidth = 10;
    if (lid > 0.97) { g.beginPath(); g.moveTo(cx - rx, ey + 10); g.quadraticCurveTo(cx, ey + 60, cx + rx, ey + 10); g.stroke(); }
    else { g.beginPath(); g.ellipse(cx, ey, rx, ry, 0, 0, 7); g.stroke(); }
  }
  // полоски на щеках: по 2 с каждой стороны
  g.strokeStyle = '#ff8a2a'; g.lineWidth = 20; g.lineCap = 'round';
  [[-1, 0], [-1, 1], [1, 0], [1, 1]].forEach(([s, k]) => { const x0 = 512 + s * 270, y0 = 430 + k * 44; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x0 + s * 120, y0 - 16 + k * 10); g.stroke(); });
  e.strokeStyle = '#a04a10'; e.lineWidth = 20; e.lineCap = 'round';
  [[-1, 0], [-1, 1], [1, 0], [1, 1]].forEach(([s, k]) => { const x0 = 512 + s * 270, y0 = 430 + k * 44; e.beginPath(); e.moveTo(x0, y0); e.lineTo(x0 + s * 120, y0 - 16 + k * 10); e.stroke(); });
  // нос и рот
  g.fillStyle = '#d68a8a'; g.beginPath(); g.moveTo(490, 425); g.lineTo(534, 425); g.lineTo(512, 452); g.closePath(); g.fill();
  g.strokeStyle = ink; g.lineWidth = 6; g.stroke();
  g.lineWidth = 7; g.beginPath(); g.moveTo(512, 452); g.lineTo(512, 470); g.moveTo(470, 470); g.quadraticCurveTo(491, 495, 512, 470); g.quadraticCurveTo(533, 495, 554, 470); g.stroke();
  catFaceTex.needsUpdate = true; catGlowTex.needsUpdate = true;
}
{ const g = new THREE.SphereGeometry(CH_R * 1.13, 96, 64, CFACE.phi0, CFACE.phiL, CFACE.th0, CFACE.thL);
  const f = mesh(g, toon(0xffffff, { map: catFaceTex, emissive: 0xffffff, emissiveMap: catGlowTex, emissiveIntensity: 0.55, transparent: true, alphaTest: 0.02, depthWrite: false }), 0, 0, 0, catHead);
  f.scale.set(...CH_S); f.layers.set(1); f.renderOrder = 2;
  // усы
  const wm = new THREE.MeshBasicMaterial({ color: 0x9aa0bc, fog: false });
  [-1, 1].forEach(s => [-0.05, 0, 0.05].forEach(a => { const g = new THREE.CylinderGeometry(0.0012, 0.0018, 0.16, 6); g.translate(0, 0.08, 0);
    const wsk = mesh(g, wm, s * 0.1, -0.055, 0.1, catHead); wsk.rotation.set(0, 0, -s * (Math.PI / 2 - 0.1 + a * 3)); wsk.rotation.y = s * -0.35; wsk.layers.set(1); })); }
// подушечки задних лап — оранжевые наклейки
{ const padTex = canvasTex(128, 128, (g) => { g.fillStyle = '#e8782a'; g.beginPath(); g.ellipse(64, 80, 30, 24, 0, 0, 7); g.fill();
    [[30, 40], [54, 28], [78, 28], [100, 40]].forEach(([x, y]) => { g.beginPath(); g.ellipse(x, y, 11, 13, 0, 0, 7); g.fill(); }); });
  [-1, 1].forEach(s => { const p = mesh(new THREE.PlaneGeometry(0.06, 0.06), toon(0xffffff, { map: padTex, transparent: true, alphaTest: 0.1, depthWrite: false }), s * 0.105, 0.04, 0.128, cat); p.layers.set(1); p.renderOrder = 3; }); }
// хвост: выходит справа, поднимается и закручивается спиралью, на кончике огонёк
const tailCurve = new THREE.CatmullRomCurve3([V(0.08, 0.06, -0.08), V(0.2, 0.04, -0.04), V(0.29, 0.1, 0.0), V(0.32, 0.22, 0.01), V(0.29, 0.33, 0.02),
  V(0.22, 0.36, 0.025), V(0.18, 0.31, 0.03), V(0.205, 0.27, 0.035), V(0.245, 0.29, 0.035)]);
mesh(tube(tailCurve, 140, 28, t => a => (0.042 * (1 - 0.55 * t) + 0.004) * (1 + 0.16 * Math.max(0, vnoise(t * 22, Math.cos(a) * 2, Math.sin(a) * 2) - 0.45))), catM, 0, 0, 0, cat);
const TAIL_TIP = tailCurve.getPointAt(1);
// огонёк: наклейка, перерисовывается каждый кадр (языки пламени колышутся)
const flameTex = canvasTex(256, 384, () => {});
function drawFlame(t) {
  const g = flameTex.userData.g, w = 256, h = 384; g.clearRect(0, 0, w, h);
  const sw = Math.sin(t * 6.3) * 16 + Math.sin(t * 11.7 + 1) * 6, l1 = Math.sin(t * 8.1) * 10, l2 = Math.sin(t * 9.4 + 2) * 10, hh = 1 + 0.06 * Math.sin(t * 13);
  const shape = (k, col, stroke) => {           // k — масштаб слоя к основанию (128, 330)
    const P = (x, y) => [128 + (x - 128) * k, 330 + (y - 330) * k * hh];
    g.beginPath(); g.moveTo(...P(128, 352));
    g.bezierCurveTo(...P(62, 352), ...P(44, 286), ...P(64, 236));                   // левый бок
    g.bezierCurveTo(...P(70, 210), ...P(78, 196 + l1), ...P(80, 168 + l1));           // левый язычок
    g.bezierCurveTo(...P(98, 200), ...P(104, 214), ...P(110, 222));
    g.bezierCurveTo(...P(104, 160), ...P(122 + sw * 0.5, 110), ...P(150 + sw, 52));  // главный кончик
    g.bezierCurveTo(...P(150 + sw * 0.6, 112), ...P(176, 150), ...P(170, 196));
    g.bezierCurveTo(...P(180, 186 + l2), ...P(186, 172 + l2), ...P(184, 158 + l2));   // правый язычок
    g.bezierCurveTo(...P(214, 214), ...P(214, 300), ...P(186, 334));
    g.bezierCurveTo(...P(170, 350), ...P(150, 352), ...P(128, 352)); g.closePath();
    g.fillStyle = col; g.fill(); if (stroke) { g.lineWidth = 9; g.lineJoin = 'round'; g.strokeStyle = '#1a0d06'; g.stroke(); } };
  shape(1, '#ff7a1a', true); shape(0.66, '#ffaa2e'); shape(0.36, '#fff0a8');
  flameTex.needsUpdate = true;
}
const FLAME_AT = V(0.24, 0.385, 0.06);
const flame = sprite(flameTex, 0xffffff, 0.11, 0.165, 0, 0, 0, false, 1, cat); flame.position.copy(FLAME_AT); flame.center.set(0.5, 0.22);
const flameGlow = sprite(glowTex, 0xff8a2a, 0.26, 0.26, 0, 0, 0, true, 0.32, cat); flameGlow.position.copy(FLAME_AT).add(V(0, 0.05, -0.01));
const flameLight = new THREE.PointLight(0xff8a30, 0.007, 0.8, 2); flameLight.position.copy(FLAME_AT).add(V(0.02, 0.1, 0.12)); cat.add(flameLight);

// тени: всё твёрдое отбрасывает и принимает
scene.traverse(o => { if (o.isMesh && o.layers.mask === 1) { o.castShadow = true; o.receiveShadow = true; } });

// ---------- пост-обработка: контур по глубине и нормалям ----------
const RW = W * SS, RH = H * SS;
const rtColor = new THREE.WebGLRenderTarget(RW, RH, { type: THREE.HalfFloatType });
const rtNorm = new THREE.WebGLRenderTarget(RW, RH, { type: THREE.UnsignedByteType });
rtNorm.depthTexture = new THREE.DepthTexture(RW, RH); rtNorm.depthTexture.type = THREE.UnsignedIntType;
const rtComp = new THREE.WebGLRenderTarget(RW, RH, { type: THREE.HalfFloatType, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter });
const normalMat = new THREE.MeshNormalMaterial({ side: THREE.DoubleSide });
const quadCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1), quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2));
const quadScene = new THREE.Scene(); quadScene.add(quad);
const VS = 'varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy,0.,1.); }';
const compMat = new THREE.ShaderMaterial({ uniforms: { tColor: { value: rtColor.texture }, tNorm: { value: rtNorm.texture }, tDepth: { value: rtNorm.depthTexture },
  res: { value: new THREE.Vector2(RW, RH) }, cn: { value: camera.near }, cf: { value: camera.far }, ink: { value: INK } }, vertexShader: VS,
  fragmentShader: `varying vec2 vUv; uniform sampler2D tColor, tNorm, tDepth; uniform vec2 res; uniform float cn, cf; uniform vec3 ink;
    float lin(float d){ float z=d*2.-1.; return 2.*cn*cf/(cf+cn-z*(cf-cn)); }
    void main(){
      vec3 col = texture2D(tColor, vUv).rgb;
      float dC = lin(texture2D(tDepth, vUv).x); vec3 nC = texture2D(tNorm, vUv).xyz*2.-1.;
      float wpx = mix(4.2, 2.4, smoothstep(3.6, 6.5, dC));             // ближе — толще линия
      float de = 0., ne = 0.;
      for (int i = 0; i < 12; i++) { float a = float(i)*0.5235988; vec2 o = vec2(cos(a), sin(a))*wpx/res;
        float d = lin(texture2D(tDepth, vUv+o).x); de = max(de, abs(d-dC)/min(d,dC));
        vec3 n = texture2D(tNorm, vUv+o).xyz*2.-1.; ne = max(ne, 1.-dot(nC, n)); }
      float slope = clamp(abs(nC.z), 0.15, 1.);                         // скользящие поверхности (пол) не чертим
      float e = max(smoothstep(0.045, 0.09, de*slope), smoothstep(0.32, 0.55, ne));
      gl_FragColor = vec4(mix(col, ink, e), 1.);
    }` });
const outMat = new THREE.ShaderMaterial({ uniforms: { t: { value: rtComp.texture }, res: { value: new THREE.Vector2(W, H) } }, vertexShader: VS,
  fragmentShader: `varying vec2 vUv; uniform sampler2D t; uniform vec2 res;
    void main(){ vec3 c = texture2D(t, vUv).rgb;
      vec2 q = vUv-0.5; c *= 1.0 - 0.32*dot(q*vec2(1.2,0.85), q*vec2(1.2,0.85))*2.2;   // мягкая виньетка
      gl_FragColor = vec4(c, 1.);
      #include <colorspace_fragment>
    }` });

// ---------- анимация ----------
const easeIO = k => k * k * (3 - 2 * k);
function blinkAt(t, t0, dur = 0.16) { const k = (t - t0) / dur; if (k < 0 || k > 1) return 0; return Math.sin(k * Math.PI); }
function update(t) {
  // камера: лёгкий наезд
  const k = easeIO(clamp(t / 3, 0, 1)); camera.position.lerpVectors(CAM0, CAM1, k); camera.lookAt(LOOK); camera.fov = 34;
  if (window.dbg) { camera.position.set(...window.dbg.pos); camera.lookAt(V(...window.dbg.look)); camera.fov = window.dbg.fov; }
  camera.updateProjectionMatrix(); camera.updateMatrixWorld();
  // Дима: усталое веко 0.42, моргания
  const b = Math.max(blinkAt(t, 0.85, 0.2), blinkAt(t, 2.45, 0.2));
  drawDimaFace(lerp(0.42, 1.0, b), [58, 52]);
  // большой палец листает: быстрый мазок вверх и возврат
  const sw = (t0) => { const q = (t - t0) / 0.42; return q < 0 || q > 1 ? 0 : Math.sin(q * Math.PI) * (q < 0.5 ? 1 : 0.6); };
  const s = Math.max(sw(0.35), sw(1.45), sw(2.3));
  phone.userData.thumb.rotation.set(0, 0, 0.5 * s); phone.userData.thumb.position.y = -0.052 + 0.032 * s;
  // экран мигает: новый ролик после свайпа + мелкая дрожь
  const flick = 1 + 0.06 * Math.sin(t * 23) * Math.sin(t * 7.1) + 0.35 * Math.max(sw(0.55), sw(1.65), sw(2.5)) * 0.6;
  phoneLight.intensity = 0.15 * flick; phoneGlow.material.opacity = 0.38 * flick;
  // кот моргает, огонёк колышется
  drawCatFace(Math.max(blinkAt(t, 1.75, 0.22), blinkAt(t, 1.98, 0.18) * 0.0));
  drawFlame(t);
  flameLight.intensity = 0.007 * (1 + 0.15 * Math.sin(t * 11) + 0.1 * Math.sin(t * 17.3));
  flameGlow.material.opacity = 0.32 * (1 + 0.12 * Math.sin(t * 9.2));
  sky.uniforms.t.value = t;
}
function renderAt(t) {
  const t0 = performance.now();
  update(t);
  renderer.shadowMap.needsUpdate = true;
  camera.layers.enableAll(); renderer.setRenderTarget(rtColor); renderer.setClearColor(0x05060c, 1); renderer.clear(); renderer.render(scene, camera);
  camera.layers.set(0); scene.overrideMaterial = normalMat; const fog = scene.fog; scene.fog = null;
  renderer.setRenderTarget(rtNorm); renderer.setClearColor(0x8080ff, 1); renderer.clear(); renderer.render(scene, camera);
  scene.overrideMaterial = null; scene.fog = fog; camera.layers.enableAll();
  quad.material = compMat; renderer.setRenderTarget(rtComp); renderer.render(quadScene, quadCam);
  quad.material = outMat; renderer.setRenderTarget(null); renderer.render(quadScene, quadCam);
  const gl = renderer.getContext(); const px = new Uint8Array(4); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);   // дождаться GPU
  return performance.now() - t0;
}
window.renderAt = renderAt;
window.sceneReady = true;
