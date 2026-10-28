// Снимает с композиции HyperFrames точное движение каждого слоя и штриха на каждом кадре (см. extract.py — та же логика).
const { chromium } = require('playwright');
const fs = require('fs');
const [SRC, OUT, SUBA] = process.argv.slice(2); const SUB = parseInt(SUBA || '1'); const N = 45 * SUB, FPS = 30 * SUB;
const FN = `
(t) => {
  const tl = window.__timelines.main; tl.seek(t > 0.5 ? 0 : 1.0, false); tl.seek(t, false);
  const root = document.getElementById('root');
  function local(el) {
    const cs = getComputedStyle(el);
    const m = cs.transform === 'none' ? new DOMMatrix() : new DOMMatrix(cs.transform);
    const [ox, oy] = cs.transformOrigin.split(' ').map(parseFloat);
    return new DOMMatrix().translate(el.offsetLeft, el.offsetTop).translate(ox, oy).multiply(m).translate(-ox, -oy);
  }
  function world(el) {
    let M = new DOMMatrix(), o = 1;
    for (let e = el; e && e !== root; e = e.parentElement) { M = local(e).multiply(M); o *= parseFloat(getComputedStyle(e).opacity); }
    return [M, o];
  }
  function opac(el) { let o = 1; for (let e = el; e && e.tagName !== 'svg'; e = e.parentNode) o *= parseFloat(getComputedStyle(e).opacity); return o; }
  const layers = ['bg', 'tail', 'body', 'cloud', 'pencil', 'b1', 'b2'].map(id => {
    const el = document.getElementById(id); const [M, o] = world(el);
    return { id, m: [M.a, M.b, M.c, M.d, M.e, M.f], o };
  });
  const strokes = [], dots = [];
  function sample(el, len) {
    const C = el.getCTM(); const pts = []; const n = Math.max(2, Math.ceil(len / 3));
    for (let i = 0; i <= n; i++) { const p = el.getPointAtLength(len * i / n); pts.push([C.a * p.x + C.c * p.y + C.e, C.b * p.x + C.d * p.y + C.f]); }
    return [pts, Math.sqrt(Math.abs(C.a * C.d - C.b * C.c))];
  }
  document.querySelectorAll('#fx path, #fx line').forEach(el => {
    const o = opac(el); if (o < 0.004) return;
    let L = el.getTotalLength(); const cs = getComputedStyle(el);
    if (cs.strokeDasharray && cs.strokeDasharray !== 'none') L = Math.max(0, Math.min(L, parseFloat(cs.strokeDasharray) - parseFloat(cs.strokeDashoffset)));
    if (L < 0.5) return;
    const [pts, s] = sample(el, L); strokes.push({ pts, w: parseFloat(cs.strokeWidth) * s, o });
  });
  document.querySelectorAll('#fx circle').forEach(el => {
    const C = el.getCTM(); const r = el.r.baseVal.value * Math.sqrt(Math.abs(C.a * C.d - C.b * C.c));
    const x = el.cx.baseVal.value, y = el.cy.baseVal.value, o = opac(el);
    if (r > 0.3 && o > 0.004) dots.push({ x: C.a * x + C.c * y + C.e, y: C.b * x + C.d * y + C.f, r, o });
  });
  return { t, layers, strokes, dots };
}
`;
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1440, height: 1920 } });
  await pg.goto('file://' + SRC);
  await pg.waitForFunction(() => window.__timelines && window.__timelines.main && [...document.images].every(i => i.complete));
  const f = eval(FN); const frames = [];
  for (let i = 0; i < N; i++) frames.push(await pg.evaluate(f, i / FPS));
  await b.close();
  fs.writeFileSync(OUT, JSON.stringify({ fps: FPS, sub: SUB, size: [1440, 1920], frames }));
  console.log('моментов', frames.length);
})();
