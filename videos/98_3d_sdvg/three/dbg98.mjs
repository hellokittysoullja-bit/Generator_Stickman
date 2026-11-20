import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs'; import http from 'http'; import path from 'path';
const dir = process.cwd(); const views = JSON.parse(process.argv[2]);
const srv = http.createServer((q, s) => { const f = path.join(dir, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { s.writeHead(404); s.end(); return; } s.writeHead(200, { 'Content-Type': f.endsWith('.js') ? 'text/javascript' : f.endsWith('.html') ? 'text/html' : 'application/json' }); s.end(d); }); }).listen(8778);
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const p = await b.newPage(); p.on('pageerror', e => console.log('PAGEERR', e.message));
await p.goto('http://localhost:8778/index98.html'); await p.waitForFunction(() => window.ready, null, { timeout: 120000 });
let k = 0; for (const v of views) { const url = await p.evaluate((v) => { if (v.t !== undefined) window.renderFrame(v.t); else window.debugView(v.p, v.l, v.fov); return document.querySelector('canvas').toDataURL('image/jpeg', 0.9); }, v); fs.writeFileSync(`dbg${k++}.jpg`, Buffer.from(url.split(',')[1], 'base64')); }
await b.close(); srv.close();
