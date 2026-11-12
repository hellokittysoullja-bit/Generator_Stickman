// node render.js still [t]  → still.png ;  node render.js anim → anim.mp4 (3 с, 30 к/с, кадры трубой в ffmpeg, без PNG на диске)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
(async () => {
  const mode = process.argv[2] || 'still';
  const here = __dirname;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(here, 'scene.html'));
  await p.waitForFunction(() => window.seek);
  if (mode === 'still') {
    const t = parseFloat(process.argv[3] || '0.6');
    const t0 = Date.now();
    await p.evaluate(t => seek(t), t);
    await p.screenshot({ path: path.join(here, process.argv[4] || 'still.png') });
    console.log('still', Date.now() - t0, 'ms');
  } else {
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'png', '-i', '-',
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-movflags', '+faststart', path.join(here, 'anim.mp4')],
      { stdio: ['pipe', 'inherit', 'inherit'] });
    const t0 = Date.now();
    for (let i = 0; i < 90; i++) {
      await p.evaluate(t => seek(t), i / 30);
      const buf = await p.screenshot({ type: 'png' });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
    console.log('anim 90 frames', ((Date.now() - t0) / 1000).toFixed(1), 's');
  }
  await b.close();
})();
