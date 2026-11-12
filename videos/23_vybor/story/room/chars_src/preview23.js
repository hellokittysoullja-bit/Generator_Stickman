// node preview23.js shot t out_dir [x y w h scale] — слои (RGBA) на момент t: L_*.png
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [shot, ts, out] = [process.argv[2], process.argv[3], process.argv[4]];
  const v = process.argv.slice(5).map(Number);
  const [x, y, w, h, sc] = v.length ? v : [0, 0, 1080, 1920, 1];
  const ow = Math.round(w * sc), oh = Math.round(h * sc);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: ow, height: oh } });
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.goto('file://' + path.join(__dirname, 'heroes23.html'));
  await p.waitForFunction(() => window.seek);
  await p.evaluate(([x, y, w, h, ow, oh]) => setView(x, y, w, h, ow, oh), [x, y, w, h, ow, oh]);
  await p.evaluate(([t, s]) => seek(t, s), [parseFloat(ts), shot]);
  for (const L of ['L_dima', 'L_plaid', 'L_cat', 'L_fx']) {
    await p.evaluate(L => only(L), L);
    await p.screenshot({ path: path.join(out, L + '.png'), omitBackground: true });
  }
  await b.close();
})();
