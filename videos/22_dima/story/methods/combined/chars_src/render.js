// Выгрузка слоёв героев: node render.js [N_PROC=4] [FRAMES=90] [OUT=../chars]
// N процессов-страниц Chromium, у каждой свой диапазон кадров; на кадр — seek(t) один раз, затем три снимка
// с прозрачным фоном (видимым оставляется один слой). Пишет OUT/L_dima|L_plaid|L_cat/NNNN.png, OUT/render_stats.json
// и пустой OUT/DONE, когда готовы все кадры.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const NP = parseInt(process.argv[2] || '4'), NF = parseInt(process.argv[3] || '90');
const OUT = path.resolve(__dirname, process.argv[4] || '../chars');
const LAYERS = ['L_dima', 'L_plaid', 'L_cat'];
const SEPARATE = process.env.SEPARATE !== '0';   // по умолчанию — отдельный Chromium на каждый процесс
(async () => {
  for (const L of LAYERS) fs.mkdirSync(path.join(OUT, L), { recursive: true });
  try { fs.unlinkSync(path.join(OUT, 'DONE')); } catch (e) { /* нет — и ладно */ }
  const t0 = Date.now();
  const browser = await chromium.launch();
  const per = Math.ceil(NF / NP);
  const jobs = [];
  for (let k = 0; k < NP; k++) {
    const a = k * per, b = Math.min(NF, a + per);
    jobs.push((async () => {
      const br = SEPARATE ? await chromium.launch() : browser;
      const ctx = await br.newContext({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
      const p = await ctx.newPage();
      await p.goto('file://' + path.join(__dirname, 'heroes.html'));
      await p.waitForFunction(() => window.seek);
      for (let f = a; f < b; f++) {
        await p.evaluate(t => seek(t), f / 30);
        for (const L of LAYERS) {
          await p.evaluate(L => only(L), L);
          await p.screenshot({ path: path.join(OUT, L, String(f).padStart(4, '0') + '.png'), omitBackground: true });
        }
      }
      await ctx.close();
      if (SEPARATE) await br.close();
    })());
  }
  await Promise.all(jobs);
  await browser.close();
  const sec = (Date.now() - t0) / 1000;
  const stats = { frames: NF, processes: NP, seconds: +sec.toFixed(1), sec_per_frame_wall: +(sec / NF).toFixed(3),
                  forecast_1200_frames_min: +((sec / NF) * 1200 / 60).toFixed(1) };
  fs.writeFileSync(path.join(OUT, 'render_stats.json'), JSON.stringify(stats, null, 1));
  console.log(JSON.stringify(stats));
  const missing = [];
  for (const L of LAYERS) for (let f = 0; f < NF; f++) {
    const fn = path.join(OUT, L, String(f).padStart(4, '0') + '.png');
    if (!fs.existsSync(fn) || fs.statSync(fn).size < 1000) missing.push(fn);
  }
  if (missing.length) { console.error('НЕ ХВАТАЕТ кадров:', missing.length, missing.slice(0, 3)); process.exit(1); }
  fs.writeFileSync(path.join(OUT, 'DONE'), '');
})();
