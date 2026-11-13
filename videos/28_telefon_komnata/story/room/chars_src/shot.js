// node shot.js html out.png t shot [x y w h scale] — быстрый снимок всех слоёв (без комнаты) на сером фоне
const { chromium } = require('playwright');
const path = require('path');
const [html, out, t, shot, x, y, w, h, sc] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch();
  const X = +(x || 0), Y = +(y || 0), Wd = +(w || 1080), Hd = +(h || 1920), S = +(sc || 0.5);
  const p = await b.newPage({ viewport: { width: Math.round(Wd * S), height: Math.round(Hd * S) } });
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.goto('file://' + path.resolve(html));
  await p.waitForFunction(() => window.seek);
  await p.evaluate(a => setView(...a), [X, Y, Wd, Hd, Math.round(Wd * S), Math.round(Hd * S)]);
  await p.evaluate(([t, s]) => { only(null); seek(t, s); }, [parseFloat(t), shot]);
  await p.evaluate(() => document.body.style.background = '#556');
  await p.screenshot({ path: out });
  await b.close();
})();
