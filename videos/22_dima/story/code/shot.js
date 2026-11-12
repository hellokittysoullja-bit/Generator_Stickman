const { chromium } = require('playwright');
(async () => {
  const [,, src, out] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + require('path').resolve(src));
  await p.waitForTimeout(300);
  await p.locator('#scene').screenshot({ path: out });
  await b.close();
})();
