import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs'; import http from 'http'; import path from 'path';
const dir = process.cwd(); const [,, from = '0', to = '9999', step = '1'] = process.argv;
const types = { '.js': 'text/javascript', '.html': 'text/html', '.json': 'application/json' };
const srv = http.createServer((q, s) => { const f = path.join(dir, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { s.writeHead(404); s.end(); return; } s.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); s.end(d); }); }).listen(8777);
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: 540, height: 960 } });
p.on('console', m => { if (m.type() === 'error') console.log('ERR', m.text()); }); p.on('pageerror', e => console.log('PAGEERR', e.message));
await p.goto('http://localhost:8777/index.html'); await p.waitForFunction(() => window.ready, null, { timeout: 120000 });
fs.mkdirSync('frames', { recursive: true });
const N = Math.round(await p.evaluate(() => window.duration) * 30);
for (let i = +from; i < Math.min(N, +to); i += +step) {
  const t0 = Date.now();
  const url = await p.evaluate((t) => { window.renderFrame(t); return document.querySelector('canvas').toDataURL('image/jpeg', 0.93); }, i / 30);
  fs.writeFileSync(`frames/f${String(i).padStart(4, '0')}.jpg`, Buffer.from(url.split(',')[1], 'base64'));
  if (i % 15 === 0) console.log(i, Date.now() - t0, 'ms');
}
await b.close(); srv.close();
