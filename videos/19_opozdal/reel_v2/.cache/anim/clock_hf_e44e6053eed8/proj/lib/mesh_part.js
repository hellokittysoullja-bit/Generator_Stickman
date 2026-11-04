// Гибкая часть персонажа на холсте композиции HyperFrames (scripts/tail_rig.py, владелец 02.11).
// meshPart({canvas, marg, img, flame, mesh, angles, fps, shutter, n}): по событию hf-seek рисует часть сеткой
// (каждый треугольник — аффинная копия своего куска картинки, раздут на 1 px от центра: без швов), кости — цепочка
// с углами суставов из физики; огонёк — на своей точке, с лёгким дрожанием. Размытие движения своё: HyperFrames
// содержимое холста не размывает — n подкадров в пределах затвора назад от t, сумма премультиплицированных с весом 1/n.
window.meshPart = function (o) {
  const cv = o.canvas, ctx = cv.getContext("2d");
  const off = document.createElement("canvas"); off.width = cv.width; off.height = cv.height;
  const octx = off.getContext("2d");
  const FPS = o.fps || 30, SHUTTER = o.shutter === undefined ? 0.5 : o.shutter, N = o.n || 16, MARG = o.marg;
  let img, flame, mesh, ang, acc;
  const lerp = (t) => {
    const f = Math.max(0, Math.min(ang.angles.length - 1.001, t * ang.hz)), i = Math.floor(f), u = f - i;
    return ang.angles[i].map((v, k) => v * (1 - u) + ang.angles[i + 1][k] * u);
  };
  const mats = (t) => {
    const A = lerp(t), out = []; let m = [1, 0, 0, 1, 0, 0];
    for (let k = 0; k < mesh.bones.length; k++) {
      const [px, py] = mesh.bones[k], c = Math.cos(A[k]), s = Math.sin(A[k]);
      const r = [c, s, -s, c, px - c * px + s * py, py - s * px - c * py];
      m = [m[0]*r[0] + m[2]*r[1], m[1]*r[0] + m[3]*r[1], m[0]*r[2] + m[2]*r[3], m[1]*r[2] + m[3]*r[3],
           m[0]*r[4] + m[2]*r[5] + m[4], m[1]*r[4] + m[3]*r[5] + m[5]];
      out.push(m);
    }
    return out;
  };
  const blend = (M, b0, b1, w0, w1) => { const a = M[b0], b = M[b1], r = []; for (let q = 0; q < 6; q++) r.push(w0 * a[q] + w1 * b[q]); return r; };
  function draw(c, t) {
    const M = mats(t), V = mesh.verts, P = new Float32Array(V.length * 2);
    for (let i = 0; i < V.length; i++) {
      const [x, y, b0, b1, w0, w1] = V[i], m = blend(M, b0, b1, w0, w1);
      P[2*i] = m[0]*x + m[2]*y + m[4] + MARG; P[2*i+1] = m[1]*x + m[3]*y + m[5] + MARG;
    }
    const I = mesh.idx;
    for (let k = 0; k < I.length; k += 3) {
      const a = I[k], b = I[k+1], d = I[k+2];
      const sx0 = V[a][0], sy0 = V[a][1], sx1 = V[b][0], sy1 = V[b][1], sx2 = V[d][0], sy2 = V[d][1];
      let x0 = P[2*a], y0 = P[2*a+1], x1 = P[2*b], y1 = P[2*b+1], x2 = P[2*d], y2 = P[2*d+1];
      const det = (sx1 - sx0) * (sy2 - sy0) - (sx2 - sx0) * (sy1 - sy0);
      if (Math.abs(det) < 1e-6) continue;
      const ma = ((x1 - x0) * (sy2 - sy0) - (x2 - x0) * (sy1 - sy0)) / det, mb = ((y1 - y0) * (sy2 - sy0) - (y2 - y0) * (sy1 - sy0)) / det;
      const mc = ((x2 - x0) * (sx1 - sx0) - (x1 - x0) * (sx2 - sx0)) / det, md = ((y2 - y0) * (sx1 - sx0) - (y1 - y0) * (sx2 - sx0)) / det;
      const me = x0 - ma * sx0 - mc * sy0, mf = y0 - mb * sx0 - md * sy0;
      const cx = (x0 + x1 + x2) / 3, cy = (y0 + y1 + y2) / 3;
      const grow = (x, y) => { const dx = x - cx, dy = y - cy, l = Math.hypot(dx, dy) || 1; return [x + dx / l, y + dy / l]; };
      [x0, y0] = grow(x0, y0); [x1, y1] = grow(x1, y1); [x2, y2] = grow(x2, y2);
      c.save(); c.beginPath(); c.moveTo(x0, y0); c.lineTo(x1, y1); c.lineTo(x2, y2); c.closePath(); c.clip();
      c.setTransform(ma, mb, mc, md, me, mf); c.drawImage(img, 0, 0); c.restore();
    }
    if (flame && mesh.flame) {
      const [fx, fy] = mesh.flame.base; let best = 0, bd = 1e18;
      for (let i = 0; i < V.length; i++) { const d2 = (V[i][0] - fx) ** 2 + (V[i][1] - fy) ** 2; if (d2 < bd) { bd = d2; best = i; } }
      const [, , b0, b1, w0, w1] = V[best], m = blend(M, b0, b1, w0, w1);
      const fk = 1 + 0.06 * Math.sin(t * 2 * Math.PI * 3.1) + 0.03 * Math.sin(t * 2 * Math.PI * 7.3);
      c.save(); c.setTransform(m[0], m[1], m[2], m[3], m[4] + MARG, m[5] + MARG);
      c.translate(fx, fy); c.scale(1 / Math.sqrt(fk), fk); c.translate(-fx, -fy);
      c.drawImage(flame, mesh.flame.xy[0], mesh.flame.xy[1]); c.restore();
    }
  }
  function renderAt(t) {
    const W = cv.width, H = cv.height;
    if (!acc) acc = new Float32Array(W * H * 4);
    acc.fill(0);
    for (let i = 0; i < N; i++) {
      octx.setTransform(1, 0, 0, 1, 0, 0); octx.clearRect(0, 0, W, H);
      draw(octx, t - (SHUTTER / FPS) * (i / Math.max(N - 1, 1)));
      const d = octx.getImageData(0, 0, W, H).data;
      for (let q = 0; q < d.length; q += 4) { const a = d[q + 3] / 255; acc[q] += d[q] * a; acc[q+1] += d[q+1] * a; acc[q+2] += d[q+2] * a; acc[q+3] += d[q+3]; }
    }
    const outD = ctx.createImageData(W, H), od = outD.data;
    for (let q = 0; q < od.length; q += 4) {
      const a = acc[q + 3] / N;
      if (a > 0.5) { const k = 255 / a / N; od[q] = acc[q] * k; od[q+1] = acc[q+1] * k; od[q+2] = acc[q+2] * k; }
      od[q + 3] = a;
    }
    ctx.putImageData(outD, 0, 0);
  }
  const load = (src) => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = src; });
  let now = 0;
  const ready = Promise.all([load(o.img), o.flame ? load(o.flame) : Promise.resolve(null),
    fetch(o.mesh).then(r => r.json()), fetch(o.angles).then(r => r.json())])
    .then(([a, b, c, d]) => { img = a; flame = b; mesh = c; ang = d; renderAt(now); });
  window.addEventListener("hf-seek", e => { now = e.detail.time; if (mesh) renderAt(now); else e.detail.waitUntil(ready.then(() => renderAt(now))); });
};
