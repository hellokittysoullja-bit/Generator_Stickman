// Рендер сцены headless-Chromium'ом (WebGL программно, SwiftShader).
//   node render.js still [t]            -> still.png
//   node render.js anim  [frames_dir]   -> anim.mp4 (3 с, 30 к/с)
const http = require('http'), fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const { chromium } = require(process.env.PLAYWRIGHT || '/opt/node-tools/node_modules/playwright');
const ROOT = __dirname, MIME = { '.html': 'text/html', '.js': 'text/javascript' };
const mode = process.argv[2] || 'still';

const server = http.createServer((req, res) => {
  const f = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(res);
});

(async () => {
  await new Promise(r => server.listen(0, r)); const port = server.address().port;
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('console', m => console.log('[page]', m.text())); page.on('pageerror', e => console.log('[err]', e.message));
  const tl = Date.now();
  await page.goto(`http://localhost:${port}/index.html`); await page.waitForFunction(() => window.sceneReady, null, { timeout: 120000 });
  console.log('scene build', Date.now() - tl, 'ms');
  const shot = async (t, file) => {
    const ms = await page.evaluate(t => window.renderAt(t), t);
    const t1 = Date.now(); await page.locator('canvas').screenshot({ path: file }); return [ms, Date.now() - t1];
  };
  if (mode === 'still') {
    const t = parseFloat(process.argv[3] || '1.3'), out = process.argv[4] || path.join(ROOT, 'still.png');
    await shot(t, out);                       // первый — с компиляцией шейдеров
    const [ms, sms] = await shot(t, out);
    console.log(`frame render ${ms.toFixed(0)} ms, screenshot ${sms} ms -> ${out}`);
  } else {
    const dir = process.argv[3]; fs.mkdirSync(dir, { recursive: true }); const times = [];
    for (let i = 0; i < 90; i++) { const [ms] = await shot(i / 30, path.join(dir, `f${String(i).padStart(3, '0')}.png`)); times.push(ms); }
    times.sort((a, b) => a - b); console.log(`90 frames, render median ${times[45].toFixed(0)} ms, max ${times[89].toFixed(0)} ms`);
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', '30', '-i', path.join(dir, 'f%03d.png'), '-c:v', 'libx264', '-preset', 'slow', '-crf', '17',
      '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path.join(ROOT, 'anim.mp4')]);
    console.log('anim.mp4 done');
  }
  await browser.close(); server.close();
})().catch(e => { console.error(e); process.exit(1); });
