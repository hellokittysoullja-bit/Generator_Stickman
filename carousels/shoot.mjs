// Снимает HTML-слайды в PNG 1080×1350 и отдаёт рамки строк текста (для замера контраста по пикселям).
// node carousels/shoot.mjs slide_01.html slide_02.html ...
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch { pw = require('/opt/node22/lib/node_modules/playwright'); }
const exe = process.env.CHROMIUM || '/opt/pw-browsers/chromium';
const browser = await pw.chromium.launch({ executablePath: exe });
const page = await browser.newPage({ viewport: { width: 1080, height: +(process.env.SHOT_H || 1350) }, deviceScaleFactor: 1 });
const out = {};
for (const file of process.argv.slice(2)) {
  await page.goto('file://' + file);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => window.__laid === true);
  const ok = await page.evaluate(() => document.fonts.check('900 100px Onest'));
  if (!ok) throw new Error('Onest не загрузился: ' + file);
  const rects = await page.evaluate(() => {
    const res = [];
    const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = walk.nextNode())) {
      const t = n.textContent.trim();
      if (!t) continue;
      const r = document.createRange();
      r.selectNodeContents(n);
      for (const b of r.getClientRects()) {
        if (b.width < 4 || b.height < 4) continue;
        res.push({ text: t, box: [b.left, b.top, b.right, b.bottom],
          fs: parseFloat(getComputedStyle(n.parentElement).fontSize), head: !!n.parentElement.closest('.h') });
      }
    }
    const imgs = [...document.images].map((i) => {
      const b = i.getBoundingClientRect();
      return { src: decodeURIComponent(i.src), box: [b.left, b.top, b.right, b.bottom] };
    });
    const keys = [...document.querySelectorAll('.key-t')].map((k) => {
      const r = document.createRange(); r.selectNodeContents(k);
      const tops = new Set([...r.getClientRects()].map((b) => Math.round(b.top)));
      const kb = k.getBoundingClientRect();
      return { text: k.textContent, lines: tops.size, right: kb.right };
    });
    return { text: res, imgs, keys };
  });
  const png = file.replace(/\.html$/, '.png');
  await page.screenshot({ path: png });
  await page.evaluate(() => document.querySelectorAll('img.st').forEach((i) => (i.style.visibility = 'hidden')));
  await page.screenshot({ path: png.replace(/\.png$/, '.noimg.png') });
  out[png.split('/').pop()] = rects;
}
await browser.close();
process.stdout.write(JSON.stringify(out));
