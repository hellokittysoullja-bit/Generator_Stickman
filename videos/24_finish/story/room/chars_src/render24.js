// Выгрузка слоёв героев по планам room: node render23.js [N_PROC=4] [id,id...]
// Задания (план, кадр) делятся между N отдельными Chromium; на кадр — seek(t, план) один раз, затем 4 снимка с прозрачным фоном.
// В конце по каждому плану — проверка наличия всех кадров и файл <id>/DONE.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const NP = parseInt(process.argv[2] || '4');
const only = process.argv[3] ? process.argv[3].split(',') : null;
const LAYERS = ['L_dima', 'L_plaid', 'L_cat', 'L_fx'];
const cfg = JSON.parse(fs.readFileSync(path.join(__dirname, 'cfg.json'))).filter(c => !only || only.includes(c.id));
(async () => {
  const jobs = [];
  for (const c of cfg) {
    try { fs.unlinkSync(path.join(c.out, 'DONE')); } catch (e) { /* нет */ }
    for (const L of LAYERS) fs.mkdirSync(path.join(c.out, L), { recursive: true });
    for (let k = 0; k < c.n; k++) jobs.push([c, k]);
  }
  const t0 = Date.now();
  let next = 0;
  await Promise.all(Array.from({ length: NP }, async () => {
    const b = await chromium.launch();
    const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
    p.on('pageerror', e => console.log('PAGEERR', e.message));
    await p.goto('file://' + path.join(__dirname, 'heroes24.html'));
    await p.waitForFunction(() => window.seek);
    let cur = null;
    while (next < jobs.length) {
      const [c, k] = jobs[next++];
      if (cur !== c.id) {
        await p.setViewportSize({ width: c.ow, height: c.oh });
        await p.evaluate(a => setView(...a), [...c.region, c.ow, c.oh]);
        cur = c.id;
      }
      await p.evaluate(([t, s]) => { only(null); seek(t, s); }, [c.start + k / 30, c.id]);
      for (const L of LAYERS) {
        await p.evaluate(L => only(L), L);
        await p.screenshot({ path: path.join(c.out, L, String(k).padStart(4, '0') + '.png'), omitBackground: true });
      }
    }
    await b.close();
  }));
  const sec = (Date.now() - t0) / 1000;
  for (const c of cfg) {
    let miss = 0;
    for (const L of LAYERS) for (let k = 0; k < c.n; k++) if (!fs.existsSync(path.join(c.out, L, String(k).padStart(4, '0') + '.png'))) miss++;
    if (miss) console.error(c.id, 'НЕ ХВАТАЕТ', miss); else fs.writeFileSync(path.join(c.out, 'DONE'), '');
  }
  console.log(JSON.stringify({ frames: jobs.length, seconds: +sec.toFixed(1), sec_per_frame: +(sec / jobs.length).toFixed(3) }));
})();
