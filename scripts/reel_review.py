"""Просмотрщик рилса с кнопкой «Отметить» (25.10, идея — Yusuke710/manim-skill, кнопка Capture).

    python scripts/reel_review.py videos/NN/reel [--video reel.mp4] [-o review.html]

Делает одну HTML-страницу с видео внутри (сжатая копия 540 px, ~5 МБ — страница открывается и на телефоне, без
сервера). Владелец смотрит, жмёт «Отметить» (или T) на моменте, пишет, что не так, и копирует все заметки одной кнопкой:
«[0:07.3] план 3: подпись налезла». Агент по времени вынимает ровно этот кадр (ffmpeg -ss) и смотрит его до правки
кода — вместо скриншота и «где-то в начале». Стрелки — кадр назад/вперёд, пробел — пауза, S — скорость 0.5.
Заметки живут в браузере (localStorage), страница без них тоже работает.
"""
import argparse
import base64
import html
import json
import os
import subprocess
import tempfile

PAGE = """<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Просмотр рилса</title>
<style>
:root{--bg:#faf7f0;--ink:#1d1b18;--mut:#6b655c;--line:#e3ddd1;--acc:#d9631e;--card:#fff}
@media (prefers-color-scheme:dark){:root{--bg:#1b1a18;--ink:#f1ede5;--mut:#a59e92;--line:#34312c;--acc:#f08a43;--card:#24221f}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.4 system-ui,sans-serif}
main{max-width:980px;margin:0 auto;padding:16px;display:grid;gap:16px;grid-template-columns:minmax(0,420px) minmax(0,1fr)}
@media (max-width:760px){main{grid-template-columns:1fr}}
h1{font-size:18px;margin:0 0 4px}p.m{color:var(--mut);margin:0;font-size:14px}
video{width:100%;border-radius:10px;background:#000;display:block}
.bar{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;align-items:center}
button{font:inherit;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:8px;padding:8px 12px;cursor:pointer}
button.main{background:var(--acc);border-color:var(--acc);color:#fff;font-weight:600}
#t{font-variant-numeric:tabular-nums;color:var(--mut);margin-left:auto}
.note{display:flex;gap:8px;margin-top:10px}.note input{flex:1;font:inherit;padding:8px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink)}
ol{padding-left:20px;margin:8px 0}li{margin:6px 0}li b{font-variant-numeric:tabular-nums;cursor:pointer;color:var(--acc)}
li button{padding:0 6px;margin-left:6px;font-size:13px}
.k{font-size:13px;color:var(--mut)}
</style></head><body><main>
<section><h1>__TITLE__</h1><p class="m">Смотрите, на нужном моменте — «Отметить», пишите, что не так.</p>
<video id="v" controls playsinline preload="auto">__SRC__</video>
<div class="bar"><button class="main" id="mark">Отметить</button><button id="back">◀ кадр</button><button id="fwd">кадр ▶</button>
<button id="slow">×0.5</button><span id="t">0:00.0</span></div>
<div class="note" id="nb" hidden><input id="txt" placeholder="Что не так в этот момент?"><button class="main" id="save">Ок</button></div>
<p class="k">Клавиши: T — отметить, пробел — пауза, ← → — кадр, S — скорость.</p></section>
<section><h1>Заметки</h1><ol id="list"></ol>
<div class="bar"><button class="main" id="copy">Скопировать все</button><button id="clear">Очистить</button></div>
<p class="k" id="ok"></p></section></main>
<script>
const v=document.getElementById('v'),KEY='reel-notes:__KEY__',FPS=30;let notes=[],at=0;
try{notes=JSON.parse(localStorage.getItem(KEY)||'[]')}catch(e){notes=[]}
const fmt=s=>{const m=Math.floor(s/60);return m+':'+(s-m*60).toFixed(1).padStart(4,'0')};
const keep=()=>{try{localStorage.setItem(KEY,JSON.stringify(notes))}catch(e){}};
function draw(){const L=document.getElementById('list');L.innerHTML='';notes.sort((a,b)=>a.t-b.t).forEach((n,i)=>{
 const li=document.createElement('li');const b=document.createElement('b');b.textContent='['+fmt(n.t)+']';b.onclick=()=>{v.currentTime=n.t;v.pause()};
 li.append(b,' '+n.text);const x=document.createElement('button');x.textContent='×';x.onclick=()=>{notes.splice(i,1);keep();draw()};li.append(x);L.append(li)})}
function mark(){v.pause();at=v.currentTime;document.getElementById('nb').hidden=false;const t=document.getElementById('txt');t.value='';t.focus()}
function save(){const t=document.getElementById('txt').value.trim();if(t){notes.push({t:+at.toFixed(2),text:t});keep();draw()}document.getElementById('nb').hidden=true}
document.getElementById('mark').onclick=mark;document.getElementById('save').onclick=save;
document.getElementById('txt').addEventListener('keydown',e=>{if(e.key==='Enter')save();e.stopPropagation()});
document.getElementById('back').onclick=()=>{v.pause();v.currentTime=Math.max(0,v.currentTime-1/FPS)};
document.getElementById('fwd').onclick=()=>{v.pause();v.currentTime=v.currentTime+1/FPS};
document.getElementById('slow').onclick=e=>{v.playbackRate=v.playbackRate===1?0.5:1;e.target.textContent=v.playbackRate===1?'×0.5':'×1'};
document.getElementById('copy').onclick=async()=>{const s='__TITLE__\\n'+notes.map(n=>'['+fmt(n.t)+'] '+n.text).join('\\n');
 try{await navigator.clipboard.writeText(s);document.getElementById('ok').textContent='Скопировано — вставьте в чат.'}catch(e){prompt('Скопируйте:',s)}};
document.getElementById('clear').onclick=()=>{if(confirm('Удалить все заметки?')){notes=[];keep();draw()}};
v.addEventListener('timeupdate',()=>{document.getElementById('t').textContent=fmt(v.currentTime)});
document.addEventListener('keydown',e=>{if(e.key==='t'||e.key==='е'||e.key==='T'){e.preventDefault();mark()}
 else if(e.key===' '){e.preventDefault();v.paused?v.play():v.pause()}else if(e.key==='ArrowLeft'){v.pause();v.currentTime=Math.max(0,v.currentTime-1/FPS)}
 else if(e.key==='ArrowRight'){v.pause();v.currentTime+=1/FPS}else if(e.key==='s'||e.key==='ы'){document.getElementById('slow').click()}});
draw();
</script></body></html>"""


def build(reel_dir, video=None, out=None, width=540, vbit="900k", webm=False):
    video = video or os.path.join(reel_dir, "reel.mp4")
    out = out or os.path.join(reel_dir, "review.html")
    with tempfile.TemporaryDirectory() as d:
        small = os.path.join(d, "s.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf", f"scale={width}:-2", "-c:v", "libx264",
                        "-b:v", vbit, "-preset", "medium", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", small],
                       check=True)
        src = f'<source type="video/mp4" src="data:video/mp4;base64,{base64.b64encode(open(small, "rb").read()).decode()}">'
        if webm:                                      # открытый Chromium без H.264 — только для проверки страницы
            w = os.path.join(d, "s.webm")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf", f"scale={width}:-2", "-c:v", "libvpx-vp9",
                            "-b:v", vbit, "-deadline", "realtime", "-c:a", "libopus", w], check=True)
            src = f'<source type="video/webm" src="data:video/webm;base64,{base64.b64encode(open(w, "rb").read()).decode()}">' + src
    name = os.path.basename(os.path.dirname(os.path.abspath(reel_dir).rstrip("/"))) or "рилс"
    title = f"Рилс {name}"
    page = (PAGE.replace("__TITLE__", html.escape(title)).replace("__KEY__", json.dumps(name)[1:-1])
            .replace("__SRC__", src))
    open(out, "w", encoding="utf8").write(page)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("reel_dir")
    ap.add_argument("--video")
    ap.add_argument("-o", "--out")
    ap.add_argument("--webm", action="store_true", help="добавить WebM (для проверки в браузере без H.264)")
    a = ap.parse_args()
    p = build(a.reel_dir, a.video, a.out, webm=a.webm)
    print(p, f"{os.path.getsize(p) / 1e6:.1f} МБ")
