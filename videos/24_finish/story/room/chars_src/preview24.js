// node preview24.js OUT_CHARS_DIR shot:t [shot:t ...] — слои кадра в OUT/<shot>_<t>/<L>/0000.png (окно и масштаб — cfg.json)
// + layout.json рядом; дальше: python3 ../assemble.py frame --id <shot> --t <t> --chars OUT/<shot>_<t>/.. (см. prev.py)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const out = process.argv[2];
const cfg = Object.fromEntries(JSON.parse(fs.readFileSync(path.join(__dirname, 'cfg.json'))).map(c => [c.id, c]));
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  p.on('console', m => console.log('CONSOLE', m.text()));
  await p.goto('file://' + path.join(__dirname, 'heroes24.html'));
  await p.waitForFunction(() => window.seek);
  for (const spec of process.argv.slice(3)) {
    const [shot, ts] = spec.split(':');
    const c = cfg[shot];
    await p.setViewportSize({ width: c.ow, height: c.oh });
    await p.evaluate(a => setView(...a), [...c.region, c.ow, c.oh]);
    await p.evaluate(([t, s]) => { only(null); seek(t, s); }, [parseFloat(ts), shot]);
    const d = path.join(out, `${shot}_${ts}`, shot);
    for (const L of ['L_dima', 'L_plaid', 'L_cat', 'L_fx']) {
      fs.mkdirSync(path.join(d, L), { recursive: true });
      await p.evaluate(L => only(L), L);
      await p.screenshot({ path: path.join(d, L, '0000.png'), omitBackground: true });
    }
    fs.copyFileSync(path.join(__dirname, '..', 'chars', shot, 'layout.json'), path.join(d, 'layout.json'));
  }
  await b.close();
})();
