// Выгрузка кадров сцены в .glb по порядку в папку-очередь, не больше 4 .glb на диске (рендерит blender_loop99.py).
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs'; import http from 'http'; import path from 'path';
const dir = process.cwd(); const [,, Q, from = '0', to = '99999', list = ''] = process.argv;
const srv = http.createServer((q, s) => { const f = path.join(dir, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { s.writeHead(404); s.end(); return; } s.writeHead(200, { 'Content-Type': f.endsWith('.js') ? 'text/javascript' : f.endsWith('.html') ? 'text/html' : 'application/octet-stream' }); s.end(d); }); }).listen(8791);
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: 540, height: 960 } }); p.on('pageerror', e => console.log('PAGEERR', e.message));
await p.goto('http://localhost:8791/index99.html'); await p.waitForFunction(() => window.ready, null, { timeout: 120000 });
fs.mkdirSync(Q, { recursive: true });
const N = Math.round(await p.evaluate(() => window.duration) * 30);
const frames = list ? list.split(',').map(Number) : [...Array(N).keys()].filter((i) => i >= +from && i < +to);
for (const i of frames) {
  while (fs.readdirSync(Q).filter((f) => f.endsWith('.glb')).length >= 4) await new Promise((r) => setTimeout(r, 300));
  const r = await p.evaluate((t) => window.exportGLB(t), i / 30);
  const n = `${Q}/f${String(i).padStart(4, '0')}`;
  fs.writeFileSync(n + '.json', JSON.stringify({ ...r.cam, flame: r.flame }));
  fs.writeFileSync(n + '.tmp', Buffer.from(r.glb, 'base64')); fs.renameSync(n + '.tmp', n + '.glb');
}
console.log('export done', frames.length); await b.close(); srv.close();
