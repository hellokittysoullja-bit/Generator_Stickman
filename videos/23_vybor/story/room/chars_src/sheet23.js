// node sheet23.js out_dir shot:t[:x,y,w,h,scale] ... — для каждого пункта четыре слоя в out_dir/<shot>_<t>/
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const out = process.argv[2];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.goto('file://' + path.join(__dirname, 'heroes23.html'));
  await p.waitForFunction(() => window.seek);
  for (const spec of process.argv.slice(3)) {
    const [shot, ts, win] = spec.split(':');
    const [x, y, w, h, sc] = win ? win.split(',').map(Number) : [0, 0, 1080, 1920, 1];
    const ow = Math.round(w * sc), oh = Math.round(h * sc);
    await p.setViewportSize({ width: ow, height: oh });
    await p.evaluate(a => setView(...a), [x, y, w, h, ow, oh]);
    await p.evaluate(([t, s]) => { only(null); seek(t, s); }, [parseFloat(ts), shot]);
    const d = path.join(out, `${shot}_${ts}`); fs.mkdirSync(d, { recursive: true });
    for (const L of ['L_dima', 'L_plaid', 'L_cat', 'L_fx']) {
      await p.evaluate(L => only(L), L);
      await p.screenshot({ path: path.join(d, L + '.png'), omitBackground: true });
    }
  }
  await b.close();
})();
