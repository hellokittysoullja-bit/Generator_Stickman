"""Карусели формата 2 (второй набор правил владельца, 21.11): 1080×1440, безопасная зона 50 px по бокам и 180 px
сверху и снизу; текст ≥ 32 px (пояснение ≥ 40, «а вслух» ≥ 38); последняя строка слайда — свой мостик к
следующему; рисунок без каймы, заходит на край букв заголовка, сзади мягкий свет, снизу тень; в каждом пункте
одна строка-ключ «что с этим делать».

    python carousels/stickers.py --cut <имена>   # рисунки без каймы в carousels/_img/cut/
    python carousels/build_v2.py B

Проверки кодом (сборка падает, если нарушено): контраст ≥ 4,5:1 по готовым пикселям; кегль ≥ 32 px; весь текст и
непрозрачная часть рисунков внутри безопасной зоны; строка-ключ в одну строку; рисунок закрывает не больше
`HEAD_COVER_MAX` букв строки заголовка и ни одного пикселя остального текста.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import BG_MID, BG_TOP, BRAND, CAR, FONT, INK, LIME, MUTED, e, lum  # noqa: E402

W, H = 1080, 1440
SAFE_X, SAFE_Y = 50, 180
CUT = CAR / "_img" / "cut"
HEAD_COVER_MAX = 0.14   # доля букв строки заголовка под рисунком: край букв, слово читается целиком
LETTER_COVER_MAX = 0.25  # и ни одна буква (окно шириной в букву) не закрыта больше чем на четверть
MIN_FONT = 32

CSS = """
@font-face { font-family: Onest; src: url('FONT') format('truetype'); font-weight: 100 900; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 1080px; height: 1440px; overflow: hidden; }
body { font-family: Onest, sans-serif; color: INK; position: relative;
  background: radial-gradient(ellipse 90% 70% at 50% 47%, BG_MID 0%, BG_TOP 75%); }
.top { position: absolute; top: 186px; left: 64px; right: 64px; display: flex; justify-content: space-between;
  font-size: 32px; font-weight: 600; color: MUTED; }
.bridge { position: absolute; bottom: 186px; left: 64px; right: 64px; font-size: 36px; font-weight: 700;
  color: LIME; line-height: 1.2; z-index: 2; }
.label { font-size: 34px; font-weight: 800; color: LIME; letter-spacing: .08em; text-transform: uppercase; }
.h { font-weight: 900; text-transform: uppercase; line-height: .98; letter-spacing: -.01em; }
.lime { color: LIME; }
.txt { position: relative; z-index: 2; }
.col { position: absolute; left: 64px; right: 64px; }
.st { position: absolute; z-index: 3; filter: drop-shadow(0 22px 22px rgba(0,0,0,.6)) drop-shadow(0 5px 7px rgba(0,0,0,.4)); }
.glow { position: absolute; z-index: 1; pointer-events: none; border-radius: 50%;
  background: radial-gradient(closest-side, rgba(214,236,120,.40) 0%, rgba(255,176,84,.20) 45%, rgba(255,176,84,0) 100%); }
.body-t { font-size: 40px; font-weight: 600; line-height: 1.2; }
.card { border: 3px solid LIME; border-radius: 26px; padding: 18px 28px 22px; background: rgba(198,240,90,.06); margin-top: 22px; }
.card-l { font-size: 32px; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: LIME; }
.card-t { font-size: 38px; font-weight: 600; line-height: 1.2; margin-top: 4px; }
.key { display: flex; align-items: center; gap: 18px; margin-top: 22px; }
.key-l { flex: none; font-size: 32px; font-weight: 900; color: BG_TOP; background: LIME; border-radius: 14px;
  padding: 4px 16px 8px; text-transform: uppercase; letter-spacing: .06em; }
.key-t { font-size: 38px; font-weight: 700; line-height: 1.15; white-space: nowrap; }
ul.sum { list-style: none; }
ul.sum li { font-size: 44px; font-weight: 600; line-height: 1.18; padding: 18px 0 18px 64px; position: relative;
  border-bottom: 2px solid rgba(246,241,231,.12); }
ul.sum li:last-child { border-bottom: 0; }
ul.sum li i { display: block; font-style: normal; font-size: 34px; font-weight: 600; color: LIME; margin-top: 4px; }
ul.sum li::before { content: attr(data-n); position: absolute; left: 0; top: 16px; color: LIME; font-weight: 900; font-size: 44px; }
"""

LAYOUT_JS = """
function layout(){
  const body=document.querySelector('.body');
  for (const img of document.querySelectorAll('img.st')){
    const hd=document.querySelector('.hdr .h');
    const r=document.createRange(); r.selectNodeContents(hd);
    const rects=[...r.getClientRects()].filter(b=>b.width>4);
    const maxB=Math.max(...rects.map(b=>b.bottom));
    const bt=body.getBoundingClientRect().top;
    const ar=img.naturalWidth/img.naturalHeight, cx=+img.dataset.cx, ov=+img.dataset.ov, maxh=+img.dataset.max;
    let top=maxB-ov, h=Math.min(maxh, bt-24-top, (1080-2*70)/ar), w=h*ar;
    top+=Math.max(0,(bt-24-top-h)*(+img.dataset.sink));
    const left=Math.min(Math.max(cx-w/2,60),1020-w);
    Object.assign(img.style,{top:top+'px',height:h+'px',left:left+'px'});
    const g=document.createElement('div'); g.className='glow';
    const gw=w*1.25, gh=h*1.2;
    Object.assign(g.style,{left:(left+w/2-gw/2)+'px',top:(top+h/2-gh/2)+'px',width:gw+'px',height:gh+'px'});
    document.body.appendChild(g);
  }
  window.__laid=true;
}
document.fonts.ready.then(()=>Promise.all([...document.images].map(i=>i.decode()))).then(layout);
"""


def css() -> str:
    font = FONT.as_uri().replace("[", "%5B").replace("]", "%5D")
    s = CSS.replace("FONT", font)
    for k, v in (("BG_TOP", BG_TOP), ("BG_MID", BG_MID), ("INK", INK), ("MUTED", MUTED), ("LIME", LIME)):
        s = s.replace(k, v)
    return s


def pic(name, cx=540, ov=26, max_h=520, sink=0.0):
    """Рисунок встаёт под заголовок, заходя на низ его последней строки на `ov` px; `sink` — доля
    свободного места, на которую он опускается вниз (0 — вплотную к заголовку)."""
    return (f'<img class="st" data-cx="{cx}" data-ov="{ov}" data-max="{max_h}" data-sink="{sink}" '
            f'src="{(CUT / (name + ".png")).as_uri()}" style="height:10px;left:0;top:0">')


def frame(body: str, n: int, total: int, bridge: str) -> str:
    br = f'<div class="bridge">{e(bridge)}</div>' if bridge else ""
    return (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>{css()}</style></head><body>'
            f'<div class="top"><span>{BRAND}</span><span>{n}/{total}</span></div>{body}{br}'
            f'<script>{LAYOUT_JS}</script></body></html>')


def cover(s):
    return (f'<div class="col txt hdr" style="top:250px"><div class="label">{e(s["label"])}</div>'
            f'<div class="h" style="margin-top:16px;font-size:{s.get("fs", 116)}px">{e(s["head"])}</div></div>'
            + pic(s["img"], **s.get("pic", {}))
            + f'<div class="col txt body" style="bottom:250px;font-size:46px;font-weight:600;line-height:1.22">{e(s["sub"])}</div>')


def point(s):
    return (f'<div class="col txt hdr" style="top:250px"><div class="label">{e(s["label"])}</div>'
            f'<div class="h" style="margin-top:14px;font-size:{s.get("fs", 86)}px">{e(s["head"])}</div></div>'
            + pic(s["img"], **s.get("pic", {}))
            + f'<div class="col txt body" style="bottom:252px"><div class="body-t">{e(s["body"])}</div>'
              f'<div class="card"><div class="card-l">а вслух</div><div class="card-t">{e(s["said"])}</div></div>'
              f'<div class="key"><span class="key-l">ключ</span><span class="key-t">{e(s["key"])}</span></div></div>')


def summary(s):
    items = "".join(f'<li data-n="{i + 1}">{e(a)}<i>{e(b)}</i></li>' for i, (a, b) in enumerate(s["items"]))
    return (f'<div class="col txt hdr" style="top:250px"><div class="label">{e(s["label"])}</div>'
            f'<div class="h" style="margin-top:14px;font-size:{s.get("fs", 80)}px">{e(s["head"])}</div>'
            f'<ul class="sum" style="margin-top:18px">{items}</ul></div><div class="body" style="position:absolute;top:1260px"></div>')


def cta(s):
    return (f'<div class="col txt hdr" style="top:250px;text-align:center"><div class="h" style="font-size:92px">'
            f'Напиши<br><span class="lime" style="font-size:160px">«КОТ»</span><br>в комментариях</div>'
            f'<div style="margin-top:26px;font-size:46px;font-weight:600;line-height:1.22">{e(s["if"])}</div></div>'
            + pic(s["img"], **s.get("pic", {}))
            + f'<div class="col txt body" style="bottom:200px;text-align:center;font-size:36px;color:{MUTED};line-height:1.3">{e(s["small"])}</div>')


T = {"cover": cover, "point": point, "summary": summary, "cta": cta}


def render(folder: Path, slides: list) -> dict:
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("slide_*.png"):
        old.unlink()
    pages = []
    for i, s in enumerate(slides, 1):
        p = folder / f"slide_{i:02d}.html"
        p.write_text(frame(T[s["t"]](s), i, len(slides), s.get("bridge", "")), encoding="utf-8")
        pages.append(str(p))
    out = subprocess.run(["node", str(CAR / "shoot.mjs"), *pages], capture_output=True, text=True, check=True,
                         env={"SHOT_H": str(H), **__import__("os").environ}).stdout
    for p in pages:
        Path(p).unlink()
    return json.loads(out)


def ink_mask(clean, box):
    x0, y0, x1, y1 = (int(round(v)) for v in box)
    x0, y0 = max(x0, 0), max(y0, 0)
    crop = clean[y0:y1, x0:x1]
    if crop.size == 0:
        return None, (x0, y0)
    edge = np.concatenate([crop[0], crop[-1], crop[:, 0], crop[:, -1]])
    return np.abs(crop - np.median(edge, axis=0)).sum(axis=2) > 90, (x0, y0)


def checks(folder: Path, boxes: dict) -> dict:
    rep = {"contrast_min": None, "contrast_below_4_5": [], "small_font": [], "outside_safe": [],
           "text_cover": [], "head_cover_max": 0.0, "key_lines": []}
    worst = None
    for name, page in boxes.items():
        im = np.asarray(Image.open(folder / name).convert("RGB")).astype(int)
        clean = np.asarray(Image.open(folder / name.replace(".png", ".noimg.png")).convert("RGB")).astype(int)
        cover = np.zeros(im.shape[:2], bool)
        for g in page["imgs"]:
            x0, y0, x1, y1 = (int(round(v)) for v in g["box"])
            a = np.asarray(Image.open(g["src"].replace("file://", "")).getchannel("A").resize((x1 - x0, y1 - y0))) > 60
            ys, xs = np.nonzero(a)
            bx0, by0, bx1, by1 = xs.min() + x0, ys.min() + y0, xs.max() + x0, ys.max() + y0
            if bx0 < SAFE_X or bx1 > W - SAFE_X or by0 < SAFE_Y or by1 > H - SAFE_Y:
                rep["outside_safe"].append((name, Path(g["src"]).stem, [int(bx0), int(by0), int(bx1), int(by1)]))
            cx0, cy0, cx1, cy1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
            cover[cy0:cy1, cx0:cx1] |= a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
        for r in page["text"]:
            x0, y0, x1, y1 = r["box"]
            if r["fs"] < MIN_FONT:
                rep["small_font"].append((name, r["text"][:30], r["fs"]))
            if x0 < SAFE_X or x1 > W - SAFE_X or y0 < SAFE_Y or y1 > H - SAFE_Y:
                rep["outside_safe"].append((name, r["text"][:30], [round(v) for v in r["box"]]))
            ink, (ox, oy) = ink_mask(clean, r["box"])
            if ink is None or not ink.any():
                continue
            cov = cover[oy:oy + ink.shape[0], ox:ox + ink.shape[1]][:ink.shape[0], :ink.shape[1]]
            share = float((ink & cov).sum()) / ink.sum()
            if r["head"] and share > 0:
                win = max(8, int(r["fs"] * 0.62))
                ink_c, cov_c = ink.sum(axis=0), (ink & cov).sum(axis=0)
                for x in range(0, max(1, ink.shape[1] - win), 4):
                    tot = ink_c[x:x + win].sum()
                    if tot > 0 and cov_c[x:x + win].sum() / tot > LETTER_COVER_MAX:
                        rep["text_cover"].append((name, r["text"][:30] + " (буква)", round(float(cov_c[x:x + win].sum() / tot), 2)))
                        break
            if r["head"]:
                rep["head_cover_max"] = max(rep["head_cover_max"], round(share, 3))
                rep.setdefault("head_cover", {})[name] = max(rep.get("head_cover", {}).get(name, 0), round(share, 3))
                if share > HEAD_COVER_MAX:
                    rep["text_cover"].append((name, r["text"][:30], round(share, 3)))
            elif share > 0:
                rep["text_cover"].append((name, r["text"][:30], round(share, 3)))
            # контраст: только непокрытые рисунком строки (покрытые — заголовок, меряется по краю)
            crop = im[oy:oy + ink.shape[0], ox:ox + ink.shape[1]]
            edge = np.concatenate([crop[0], crop[-1], crop[:, 0], crop[:, -1]])
            bg = np.median(edge, axis=0)
            fg = crop[ink & ~cov]
            if len(fg) < 20:
                continue
            fgc = fg[np.abs(fg - bg).sum(axis=1) >= np.percentile(np.abs(fg - bg).sum(axis=1), 60)].mean(axis=0)
            l1, l2 = sorted([lum(fgc), lum(bg)], reverse=True)
            ratio = round(float((l1 + 0.05) / (l2 + 0.05)), 2)
            if worst is None or ratio < worst[2]:
                worst = (name, r["text"][:30], ratio)
            if ratio < 4.5:
                rep["contrast_below_4_5"].append((name, r["text"][:30], ratio))
        for k in page["keys"]:
            if k["lines"] != 1:
                rep["key_lines"].append((name, k["text"][:30], k["lines"]))
        (folder / name.replace(".png", ".noimg.png")).unlink()
    rep["contrast_min"] = worst
    return rep


def preview(folder: Path):
    files = sorted(folder.glob("slide_*.png"))
    cols, tw = 4, 360
    th = round(tw * H / W)
    pad = 24
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + pad + 34) + pad), (40, 40, 46))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT), 24)
    k = tw / W
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = pad + (i % cols) * (tw + pad), pad + (i // cols) * (th + pad + 34)
        sheet.paste(im, (x, y))
        # красное — обрезка сетки 3:4 (1080×1440 по центру — без обрезки по бокам), жёлтое — безопасная зона
        d.rectangle([x + SAFE_X * k, y + SAFE_Y * k, x + tw - SAFE_X * k, y + th - SAFE_Y * k], outline=(240, 200, 60), width=1)
        d.text((x, y + th + 4), f.name, fill=(220, 220, 220), font=font)
    sheet.save(folder / "preview.jpg", quality=88)


def main():
    from content import CAROUSELS
    keys = sys.argv[1:] or [k for k, c in CAROUSELS.items() if c.get("format") == 2]
    bad_any = False
    for key in keys:
        c = CAROUSELS[key]
        assert c.get("format") == 2, f"{key}: не формат 2, собирать build.py"
        folder = CAR / c["dir"]
        boxes = render(folder, c["slides"])
        for f in sorted(folder.glob("slide_*.png")):
            assert Image.open(f).size == (W, H), f
        rep = checks(folder, boxes)
        (folder / "contrast.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
        preview(folder)
        bad = {k: v for k, v in rep.items() if isinstance(v, list) and v}
        bad_any |= bool(bad)
        print(key, folder.name, "слайдов", len(c["slides"]), "контраст мин.", rep["contrast_min"],
              "заголовок под рисунком макс.", rep["head_cover_max"], "нарушения:", bad or "нет")
        print("  доля букв заголовка под рисунком по слайдам:", rep.get("head_cover"))
    sys.exit(1 if bad_any else 0)


if __name__ == "__main__":
    main()
