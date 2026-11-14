// node render.js list.txt mode(mp4|png) NPROC OUTPREFIX
// list.txt: по строке на кадр — путь к SVG [\t путь PNG для mode=png]. mp4: каждый процесс гонит свой отрезок в ffmpeg
// (image2pipe, PNG потоком), сегменты OUTPREFIX_<i>.mp4 склеивает make.py.
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const fs = require('fs'), path = require('path'), { spawn } = require('child_process');
const [list, mode, np_, pre] = process.argv.slice(2);
const NP = parseInt(np_ || '4');
const items = fs.readFileSync(list, 'utf8').trim().split('\n').map(l => l.split('\t'));
const base = 'file://' + '/home/user/Generator_Stickman/videos/44_mechty/story/ext_b/base.html';
(async () => {
  const per = Math.ceil(items.length / NP);
  const jobs = [];
  for (let k = 0; k < NP; k++) {
    const a = k * per, b = Math.min(items.length, a + per);
    if (a >= b) continue;
    jobs.push((async () => {
      const br = await chromium.launch();
      const p = await (await br.newContext({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 })).newPage();
      await p.goto(base);
      await p.evaluate(() => document.fonts.ready);
      let ff = null, done = null;
      if (mode === 'mp4') {
        ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'png', '-i', '-',
          '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', '30', `${pre}_${k}.mp4`],
          { stdio: ['pipe', 'inherit', 'inherit'] });
        done = new Promise(r => ff.on('close', r));
      }
      for (let i = a; i < b; i++) {
        const s = fs.readFileSync(items[i][0], 'utf8');
        await p.evaluate(s => { document.getElementById('c').innerHTML = s; }, s);
        await p.evaluate(() => document.fonts.ready);
        const buf = await p.screenshot({ type: 'png' });
        if (mode === 'mp4') { if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); }
        else fs.writeFileSync(items[i][1], buf);
      }
      if (ff) { ff.stdin.end(); await done; }
      await br.close();
    })());
  }
  await Promise.all(jobs);
})();
