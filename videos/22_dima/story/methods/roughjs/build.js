// Собирает scene.html: SVG из ../../code/night.html (+ id для анимации, веки кота) + rough.js + roughify.js,
// рендерит still.png (заливка + штриховка), still_pure.png (только Rough), anim.mp4 (3 с, 30 к/с).
// node build.js [--no-anim]
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

const here = __dirname;
let html = fs.readFileSync(path.join(here, '../../code/night.html'), 'utf8');
const rep = (a, b) => { if (!html.includes(a)) throw new Error('нет в night.html: ' + a); html = html.replace(a, b); };
rep('<path d="M478 1052', '<path id="thumb" d="M478 1052');
rep('<ellipse class="glow" cx="455"', '<ellipse id="phoneGlowEl" class="glow" cx="455"');
// веки кота (для моргания), цветом шерсти, под клипом глаза
rep('<!-- нос, рот -->',
  '<g clip-path="url(#catEyeL)"><rect id="catLidL" x="760" y="1098" width="72" height="0" fill="#25232d"/></g>' +
  '<g clip-path="url(#catEyeR)"><rect id="catLidR" x="833" y="1098" width="72" height="0" fill="#25232d"/></g>\n    <!-- нос, рот -->');
html = html.replace('</body>',
  '<script src="rough.js"></script>\n<script src="roughify.js"></script>\n</body>');
const scenePath = path.join(here, 'scene.html');
fs.writeFileSync(scenePath, html);

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + scenePath);
  await p.waitForFunction(() => typeof window.render === 'function');
  const shot = async (t, mode, boil, out) => {
    const t0 = Date.now();
    await p.evaluate(([t, m, bo]) => window.render(t, m, bo), [t, mode, boil]);
    const buf = await p.locator('#scene').screenshot(out ? { path: out } : {});
    return [buf, Date.now() - t0];
  };
  let [, ms] = await shot(0, 'color', false, path.join(here, 'still.png'));
  console.log('still.png', ms, 'мс (rough + скриншот)');
  [, ms] = await shot(0, 'pure', false, path.join(here, 'still_pure.png'));
  console.log('still_pure.png', ms, 'мс');
  // чистое время rough-перерисовки без скриншота
  const tr = await p.evaluate(() => { const a = performance.now(); for (let i = 0; i < 10; i++) window.render(i / 10); return (performance.now() - a) / 10; });
  console.log('roughify один кадр', tr.toFixed(1), 'мс');
  if (!process.argv.includes('--no-anim')) {
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-i', '-',
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', path.join(here, 'anim.mp4')], { stdio: ['pipe', 'inherit', 'inherit'] });
    const a = Date.now();
    for (let f = 0; f < 90; f++) {
      const [buf] = await shot(f / 30, 'color', true);
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    }
    ff.stdin.end();
    await new Promise((r) => ff.on('close', r));
    console.log('anim.mp4 90 кадров за', ((Date.now() - a) / 1000).toFixed(1), 'с');
  }
  await b.close();
})();
