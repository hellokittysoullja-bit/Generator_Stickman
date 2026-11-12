// node preview.js t out_dir — три слоя (RGBA) на момент t для проверки глазами
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const t = parseFloat(process.argv[2] || '1.3'), out = process.argv[3] || '.';
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'heroes.html'));
  await p.waitForFunction(() => window.seek);
  await p.evaluate(t => seek(t), t);
  for (const L of ['L_dima', 'L_plaid', 'L_cat']) {
    await p.evaluate(L => only(L), L);
    const t0 = Date.now();
    await p.screenshot({ path: path.join(out, L + '.png'), omitBackground: true });
    console.log(L, Date.now() - t0, 'ms');
  }
  await b.close();
})();
