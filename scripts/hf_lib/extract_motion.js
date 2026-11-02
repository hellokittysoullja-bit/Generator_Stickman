// Мировая матрица родителя элемента композиции HyperFrames по времени: как тело несёт часть (хвост, ухо).
// node extract_motion.js <index.html> <id элемента> <out.json> <Гц> <длительность, с>  (scripts/tail_rig.py)
const { chromium } = require('playwright'); const fs = require('fs');
const [SRC, ID, OUT, HZ, DUR] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage();
  await pg.goto('file://' + SRC);
  await pg.waitForFunction(() => window.__timelines && window.__timelines.main && [...document.images].every(i => i.complete));
  const n = Math.round(parseFloat(DUR) * parseFloat(HZ)), out = [];
  for (let i = 0; i <= n; i++) {
    out.push(await pg.evaluate(([t, id]) => {
      const tl = window.__timelines.main; tl.seek(t > 0.5 ? 0 : 1.0, false); tl.seek(t, false);   // свежее состояние
      const root = document.getElementById('root');
      const local = (el) => { const cs = getComputedStyle(el); const m = cs.transform === 'none' ? new DOMMatrix() : new DOMMatrix(cs.transform);
        const [ox, oy] = cs.transformOrigin.split(' ').map(parseFloat);
        return new DOMMatrix().translate(el.offsetLeft, el.offsetTop).translate(ox, oy).multiply(m).translate(-ox, -oy); };
      let M = new DOMMatrix();
      for (let e = document.getElementById(id).parentElement; e && e !== root; e = e.parentElement) M = local(e).multiply(M);
      return [M.a, M.b, M.c, M.d, M.e, M.f];
    }, [i / parseFloat(HZ), ID]));
  }
  await b.close(); fs.writeFileSync(OUT, JSON.stringify(out));
})();
