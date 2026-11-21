"""Карусели Instagram канала «СДВГ | Напарник»: HTML на слайд → PNG 1080×1350 через headless Chromium.

    python carousels/stickers.py          # один раз: наклейки из готовых рисунков в carousels/_img/
    python carousels/build.py [A|B|V]     # слайды, preview.jpg, проверка контраста по пикселям

Правила владельца (образец «слабая vs вирусная»): одна главная мысль крупно, остальное мельче; важное в центре,
по бокам ≥ 35 px запаса под обрезку сетки 3:4 (текст держим в 72 px); белое на тёмном, один акцент — лаймовый
цвет глаз кота; контраст текста ≥ 4,5:1 — меряется по готовым пикселям (`contrast_report`); рисунок — наклейка
без фона, заходит на заголовок, под ней тень.
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CAR = ROOT / "carousels"
IMG = CAR / "_img"
FONT = ROOT / "assets/fonts/reels/Onest[wght].ttf"
BRAND = "СДВГ | Напарник"
W, H = 1080, 1350

BG_TOP, BG_MID = "#12131a", "#1d2031"
INK, MUTED, LIME = "#F6F1E7", "#B4B1C2", "#C6F05A"

CSS = """
@font-face { font-family: Onest; src: url('FONT') format('truetype'); font-weight: 100 900; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 1080px; height: 1350px; overflow: hidden; }
body { font-family: Onest, sans-serif; color: INK; position: relative;
  background: radial-gradient(ellipse 90% 70% at 50% 45%, BG_MID 0%, BG_TOP 75%); }
.top { position: absolute; top: 52px; left: 72px; right: 72px; display: flex; justify-content: space-between;
  font-size: 32px; font-weight: 600; color: MUTED; letter-spacing: .02em; }
.bot { position: absolute; bottom: 48px; left: 72px; right: 72px; display: flex; justify-content: space-between;
  font-size: 32px; font-weight: 600; color: MUTED; }
.bot .next { color: LIME; font-weight: 700; }
.label { font-size: 34px; font-weight: 800; color: LIME; letter-spacing: .08em; text-transform: uppercase; }
.h { font-weight: 900; text-transform: uppercase; line-height: .98; letter-spacing: -.01em; }
.lime { color: LIME; }
.muted { color: MUTED; }
.st { position: absolute; z-index: 3; filter: drop-shadow(0 26px 26px rgba(0,0,0,.62)) drop-shadow(0 6px 8px rgba(0,0,0,.45)); }
.txt { position: relative; z-index: 2; }
.col { position: absolute; left: 72px; right: 72px; }
.row-l { font-size: 30px; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; margin-bottom: 8px; }
.row-t { font-size: 40px; font-weight: 600; line-height: 1.22; }
.card { border: 3px solid LIME; border-radius: 28px; padding: 26px 32px 30px; background: rgba(198,240,90,.06); }
.src { font-size: 24px; color: MUTED; line-height: 1.3; margin-top: 18px; }
ul.sum { list-style: none; }
ul.sum li { font-size: 46px; font-weight: 600; line-height: 1.2; padding: 26px 0 26px 66px; position: relative;
  border-bottom: 2px solid rgba(246,241,231,.12); }
ul.sum li:last-child { border-bottom: 0; }
ul.sum li b { color: LIME; font-weight: 800; }
ul.sum li::before { content: attr(data-n); position: absolute; left: 0; top: 24px; color: LIME; font-weight: 900; font-size: 46px; }
"""


def css() -> str:
    font = FONT.as_uri().replace("[", "%5B").replace("]", "%5D")
    s = CSS.replace("FONT", font)
    for k, v in (("BG_TOP", BG_TOP), ("BG_MID", BG_MID), ("INK", INK), ("MUTED", MUTED), ("LIME", LIME)):
        s = s.replace(k, v)
    return s


def e(t: str) -> str:
    """Текст с разметкой *лайм*."""
    out, on = [], False
    t = re.sub(r"(?<![\w])(\w{1,2}) ", "\\1\u00a0", t)  # предлог и короткое слово не висят в конце строки
    for i, part in enumerate(html.escape(t).split("*")):
        if i:
            on = not on
            out.append('<span class="lime">' if on else "</span>")
        out.append(part)
    s = "".join(out)
    s = re.sub(r"(\w+-\w+)", r'<span style="white-space:nowrap">\1</span>', s)  # «что-то» не рвётся
    for tag in ("br", "b", "/b"):
        s = s.replace(f"&lt;{tag}&gt;", f"<{tag}>")
    return s


def auto_sticker(name, cx=540, max_h=560, dip=14):
    """Наклейка, которую раскладывает страница: заходит в зону последней строки заголовка справа от неё
    (не на буквы), растёт до текста снизу; места справа нет — встаёт сразу под заголовок."""
    return (f'<img class="st" data-auto="1" data-cx="{cx}" data-max="{max_h}" data-dip="{dip}" '
            f'src="{(IMG / (name + ".png")).as_uri()}" style="height:10px;left:0;top:0">')


LAYOUT_JS = """
function layout(){
 for (const img of document.querySelectorAll('img.st[data-auto]')){
  const hd=document.querySelector('.hdr .h'), body=document.querySelector('.body');
  const r=document.createRange(); r.selectNodeContents(hd);
  const rects=[...r.getClientRects()].filter(b=>b.width>4);
  const maxB=Math.max(...rects.map(b=>b.bottom));
  const last=rects.filter(b=>b.bottom>maxB-20);
  const lastTop=Math.min(...last.map(b=>b.top)), lastRight=Math.max(...last.map(b=>b.right));
  const bt=body.getBoundingClientRect().top;
  const ar=img.naturalWidth/img.naturalHeight, cx=+img.dataset.cx, maxh=+img.dataset.max;
  const fitH=(t)=>Math.min(maxh, bt-28-t, 960/ar);
  let top=lastTop+(+img.dataset.dip), h=fitH(top), w=h*ar, left=cx-w/2;
  if(left<lastRight+14){
    left=lastRight+14;
    if(left+w>1080-40){ top=maxB-14; h=fitH(top); w=h*ar; left=Math.min(Math.max(cx-w/2,40),1040-w);
      top+=Math.max(0,(bt-28-top-h)/2); }  // упёрлась в ширину: по центру свободного места
  }
  img.style.top=top+'px'; img.style.height=h+'px'; img.style.left=left+'px';
 }
 window.__laid=true;
}
document.fonts.ready.then(()=>Promise.all([...document.images].map(i=>i.decode()))).then(layout);
"""


def sticker(name, h, left=None, right=None, top=None, bottom=None, rot=0, cx=None):
    if cx is not None:  # центр наклейки по горизонтали
        w0, h0 = Image.open(IMG / (name + ".png")).size
        left = round(cx - h * w0 / h0 / 2)
    pos = ";".join(f"{k}:{v}px" for k, v in (("left", left), ("right", right), ("top", top), ("bottom", bottom))
                   if v is not None)
    return (f'<img class="st" src="{(IMG / (name + ".png")).as_uri()}" '
            f'style="height:{h}px;{pos};transform:rotate({rot}deg)">')


def frame(body: str, n: int, total: int) -> str:
    nxt = '<span class="next">листай →</span>' if n < total else "<span></span>"
    return (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>{css()}</style></head><body>'
            f'<div class="top"><span>{BRAND}</span><span>{n}/{total}</span></div>{body}'
            f'<div class="bot"><span>{"сохрани, пригодится" if n == total - 1 else ""}</span>{nxt}</div>'
            f'<script>{LAYOUT_JS}</script></body></html>')


# ---------- шаблоны ----------

def cover_vs(s):
    return (f'<div class="col txt" style="top:150px;text-align:center"><div class="label">{e(s["label"])}</div></div>'
            f'<div class="col txt h" style="top:215px;text-align:center;font-size:230px">ЛЕНЬ</div>'
            f'<div class="col txt" style="top:452px;text-align:center"><span style="display:inline-block;'
            f'font-size:58px;font-weight:900;color:{BG_TOP};background:{LIME};border-radius:50px;padding:6px 34px 10px">vs</span></div>'
            f'<div class="col txt h lime" style="top:560px;text-align:center;font-size:230px">СДВГ</div>'
            + sticker(s["img"], s.get("h", 330), left=s.get("x", 60), top=s.get("y", 740))
            + f'<div class="col txt" style="bottom:140px;text-align:center;font-size:46px;font-weight:600;line-height:1.25">{e(s["sub"])}</div>')


def cover(s):
    return (f'<div class="col txt hdr" style="top:140px"><div class="label">{e(s["label"])}</div>'
            f'<div class="h" style="margin-top:18px;font-size:{s.get("fs", 124)}px">{e(s["head"])}</div></div>'
            + auto_sticker(s["img"], **s.get("auto", {"max_h": 640}))
            + f'<div class="col txt body" style="bottom:130px;font-size:48px;font-weight:600;line-height:1.25;text-align:center">{e(s["sub"])}</div>')


def head_block(s):
    return (f'<div class="col txt hdr" style="top:128px"><div class="label">{e(s["label"])}</div>'
            f'<div class="h" style="margin-top:16px;font-size:{s.get("fs", 92)}px">{e(s["head"])}</div></div>')


def point_ab(s):  # А: так кажется / так на самом деле
    src = f'<div class="src">{e(s["src"])}</div>' if s.get("src") else ""
    return (head_block(s) + auto_sticker(s["img"], **s.get("auto", {}))
            + f'<div class="col txt body" style="bottom:122px">'
              f'<div class="row-l muted">так кажется</div><div class="row-t muted" style="font-weight:500">{e(s["seems"])}</div>'
              f'<div class="card" style="margin-top:26px"><div class="row-l lime">на самом деле</div>'
              f'<div class="row-t">{e(s["real"])}</div></div>{src}</div>')


def point_said(s):  # Б: что внутри / что говорим вслух
    return (head_block(s) + auto_sticker(s["img"], **s.get("auto", {}))
            + f'<div class="col txt body" style="bottom:122px"><div class="row-t">{e(s["body"])}</div>'
              f'<div class="card" style="margin-top:28px"><div class="row-l lime">а вслух</div>'
              f'<div class="row-t">{e(s["said"])}</div></div></div>')


def point_key(s):  # В: ловушка и ключ
    return (head_block(s) + auto_sticker(s["img"], **s.get("auto", {}))
            + f'<div class="col txt body" style="bottom:122px"><div class="row-t muted" style="font-weight:500">{e(s["body"])}</div>'
              f'<div class="card" style="margin-top:26px"><div class="row-l lime">ключ</div>'
              f'<div class="row-t">{e(s["key"])}</div></div></div>')


def summary(s):
    items = "".join(f'<li data-n="{i + 1}">{e(t)}</li>' for i, t in enumerate(s["items"]))
    note = f'<div class="src" style="font-size:30px;margin-top:26px;max-width:600px">{e(s["note"])}</div>' if s.get("note") else ""
    img = sticker(s["img"], s["h"], **s["pos"]) if s.get("img") else ""
    return (f'<div class="col txt" style="top:128px"><div class="label">{e(s["label"])}</div>'
            f'<div class="h" style="margin-top:16px;font-size:{s.get("fs", 84)}px">{e(s["head"])}</div>'
            f'<ul class="sum" style="margin-top:34px">{items}</ul>{note}</div>' + img)


def cta(s):
    return (f'<div class="col txt" style="top:150px;text-align:center"><div class="h" style="font-size:96px">'
            f'Напиши<br><span class="lime" style="font-size:170px">«КОТ»</span><br>в комментариях</div>'
            f'<div style="margin-top:30px;font-size:48px;font-weight:600;line-height:1.25">{e(s["if"])}</div></div>'
            + sticker(s["img"], s["h"], **s["pos"])
            + f'<div class="col txt" style="bottom:130px;text-align:center;font-size:34px;color:{MUTED};line-height:1.3">{e(s["small"])}</div>')


T = {"cover_vs": cover_vs, "cover": cover, "ab": point_ab, "said": point_said, "key": point_key,
     "summary": summary, "cta": cta}


def render(folder: Path, slides: list):
    folder.mkdir(parents=True, exist_ok=True)
    pages = []
    for i, s in enumerate(slides, 1):
        p = folder / f"slide_{i:02d}.html"
        p.write_text(frame(T[s["t"]](s), i, len(slides)), encoding="utf-8")
        pages.append(str(p))
    js = CAR / "shoot.mjs"
    out = subprocess.run(["node", str(js), *pages], capture_output=True, text=True, check=True).stdout
    boxes = json.loads(out)
    for p in pages:
        Path(p).unlink()
    return boxes


def lum(c):
    c = np.asarray(c, float) / 255
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def contrast_report(folder: Path, boxes: dict) -> list:
    """Контраст по готовым пикселям: в рамке каждой строки текста — цвет букв (самые далёкие от фона пиксели)
    против фона (медиана по краю рамки). Ловит и текст, на который зашла наклейка."""
    rows = []
    for name, page in boxes.items():
        im = np.asarray(Image.open(folder / name).convert("RGB"))
        for r in page["text"]:
            x0, y0, x1, y1 = (int(round(v)) for v in r["box"])
            x0, y0 = max(x0, 0), max(y0, 0)
            crop = im[y0:y1, x0:x1]
            if crop.size == 0:
                continue
            edge = np.concatenate([crop[0], crop[-1], crop[:, 0], crop[:, -1]])
            bg = np.median(edge, axis=0)
            d = np.abs(crop.astype(int) - bg).sum(axis=2)
            fg = crop[d >= np.percentile(d, 97)].mean(axis=0)
            l1, l2 = sorted([lum(fg), lum(bg)], reverse=True)
            ratio = (l1 + 0.05) / (l2 + 0.05)
            rows.append((name, r["text"][:40], round(float(ratio), 2)))
    return rows


def overlaps(folder: Path, boxes: dict) -> list:
    """Буквы, на которые зашла непрозрачная часть наклейки: должно быть пусто. Буквы берутся со снимка без
    наклеек (пиксели, далёкие от фона, в рамках строк), наклейка — по её альфе; пересечение в пикселях."""
    bad = []
    for name, page in boxes.items():
        clean = np.asarray(Image.open(folder / name.replace(".png", ".noimg.png")).convert("RGB")).astype(int)
        ink = np.zeros(clean.shape[:2], bool)
        for r in page["text"]:
            x0, y0, x1, y1 = (int(round(v)) for v in r["box"])
            crop = clean[max(y0, 0):y1, max(x0, 0):x1]
            if crop.size == 0:
                continue
            edge = np.concatenate([crop[0], crop[-1], crop[:, 0], crop[:, -1]])
            ink[max(y0, 0):y1, max(x0, 0):x1] |= np.abs(crop - np.median(edge, axis=0)).sum(axis=2) > 90
        for im in page["imgs"]:
            x0, y0, x1, y1 = (int(round(v)) for v in im["box"])
            a = Image.open(im["src"].replace("file://", "")).getchannel("A").resize((x1 - x0, y1 - y0))
            cover = np.zeros(ink.shape, bool)
            sub = np.asarray(a) > 60
            cx0, cy0 = max(x0, 0), max(y0, 0)
            cx1, cy1 = min(x1, W), min(y1, H)
            cover[cy0:cy1, cx0:cx1] = sub[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
            n = int((ink & cover).sum())
            if n:
                bad.append((name, Path(im["src"]).stem, n))
        (folder / name.replace(".png", ".noimg.png")).unlink()
    return bad


def preview(folder: Path, n: int):
    files = sorted(folder.glob("slide_*.png"))
    cols = 4
    tw, th, pad = 360, 450, 24
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + pad + 34) + pad), (40, 40, 46))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT), 24)
    for k, f in enumerate(files):
        im = Image.open(f).convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = pad + (k % cols) * (tw + pad), pad + (k // cols) * (th + pad + 34)
        sheet.paste(im, (x, y))
        # рамка обрезки сетки профиля 3:4 (1012×1350 по центру)
        cx = (W - 1012) / 2 * tw / W
        d.rectangle([x + cx, y, x + tw - cx, y + th - 1], outline=(255, 90, 90), width=1)
        d.text((x, y + th + 4), f.name, fill=(220, 220, 220), font=font)
    sheet.save(folder / "preview.jpg", quality=88)


def main():
    from content import CAROUSELS
    keys = sys.argv[1:] or list(CAROUSELS)
    for k in keys:
        folder = CAR / CAROUSELS[k]["dir"]
        boxes = render(folder, CAROUSELS[k]["slides"])
        rep = contrast_report(folder, boxes)
        bad = [r for r in rep if r[2] < 4.5]
        worst = min(rep, key=lambda r: r[2])
        ov = overlaps(folder, boxes)
        edge = [(n, r["text"][:30]) for n, pg in boxes.items() for r in pg["text"]
                if r["box"][0] < 40 or r["box"][2] > W - 40 or r["box"][3] > H - 30]
        (folder / "contrast.json").write_text(json.dumps(
            {"min": worst, "below_4_5": bad, "lines": len(rep), "text_under_sticker": ov, "text_near_edge": edge}, ensure_ascii=False, indent=1), encoding="utf-8")
        for f in sorted(folder.glob("slide_*.png")):
            assert Image.open(f).size == (W, H), f
        preview(folder, len(CAROUSELS[k]["slides"]))
        print(k, folder.name, "слайдов", len(CAROUSELS[k]["slides"]), "строк текста", len(rep),
              "минимальный контраст", worst, "ниже 4,5:", bad, "буквы под наклейкой (px):", ov, "текст у края:", edge)


if __name__ == "__main__":
    sys.path.insert(0, str(CAR))
    main()
