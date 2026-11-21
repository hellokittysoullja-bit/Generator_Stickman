"""Вырезка готовых рисунков в «наклейки» для каруселей: предмет без фона с кремовой каймой.

Чёрный кот на тёмном слайде без каймы пропадает, поэтому вокруг рисунка остаётся полоса его же бумаги
(как у стикеров длинных роликов). Рисунок не перерисовывается и не искажается: пиксели внутри наклейки —
оригинал байт в байт, меняется только альфа снаружи. Ночная сцена с тёмным фоном — мягкий овал (`oval`).

    python carousels/stickers.py [имя ...]
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "carousels" / "_img"
CREAM = (246, 241, 230)
LIB = "library/cat/originals/"

# имя -> (исходник, рамка обрезки [x0, y0, x1, y1] или None, режим)
SOURCES = {
    "floor": ("videos/05_ustal/reel/gen/u1_floor.png", None, "cut"),
    "m1_wait": ("videos/09_napishi/reel/gen/m1_wait.png", None, "cut"),
    "doorway": ("videos/13_dver/reel/gen/d1_doorway.png", None, "cut"),
    "repot": ("videos/06_zaodno/reel/gen/d2_repot.png", (0, 560, 1024, 1536), "cut_main"),
    "zones": ("videos/21_son/reel/gen/s3_zones.png", None, "cut"),
    "lost": ("videos/06_zaodno/reel/gen/d4_lost.png", None, "cut"),
    "curtain": ("videos/13_dver/reel/gen/d5_curtain.png", None, "cut"),
    "wednesday": ("videos/14_ponedelnik/reel/gen/m2_wednesday.png", None, "cut"),
    "list": ("videos/07_potom/reel/gen/p3_list.png", None, "cut"),
    "envelope": ("videos/05_ustal/reel/gen/u4_envelope_on_back.png", None, "cut"),
    "night": ("videos/04_noch/reel/gen/n3_lamp_island.png", None, "oval"),
    "rush": ("videos/17_pashesh/reel/gen/p1_rush.png", None, "cut"),
    "push": ("videos/16_otlozhish/reel/gen/o1_push.png", None, "cut"),
    "tower": ("videos/07_potom/reel/gen/p1_tower.png", None, "cut"),
    "hourglass": ("videos/01_sdvg_pismo/reel/gen/r2_hourglass.png", None, "cut"),
    "drafts": ("videos/10_ideal/reel/gen/i2_drafts.png", None, "cut"),
    "together": ("videos/09_napishi/reel/gen/m2_back.png", None, "cut"),
    "happy": (LIB + "2026-10-21_experiments_alive_cat_doll_faces_happy_src_3cc40e40.png", None, "cut"),
    "wave": (LIB + "2026-10-07_experiments_alive_cat_doll_assets_hero_wave_9da89b40.png", None, "cut_holes"),
    "paw": (LIB + "2026-10-07_experiments_alive_cat_doll_assets_hero_paw_up_4277766f.png", None, "cut_holes"),
    "neutral": ("look/states/hero-neutral.png", None, "cut"),
}


def paper_bg(rgb: np.ndarray, tol: int = 26, holes: bool = False) -> np.ndarray:
    """Маска фона: бумага, до которой можно дойти от края картинки."""
    h, w, _ = rgb.shape
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    paper = np.median(border, axis=0)
    near = np.abs(rgb.astype(int) - paper).max(axis=2) <= tol
    m = Image.fromarray(np.where(near, 255, 0).astype(np.uint8)).copy()  # копия: заливка не пишет в чужой буфер numpy
    for x in range(0, w, 3):
        for y in (0, h - 1):
            if m.getpixel((x, y)) == 255:
                ImageDraw.floodfill(m, (x, y), 128)
    for y in range(0, h, 3):
        for x in (0, w - 1):
            if m.getpixel((x, y)) == 255:
                ImageDraw.floodfill(m, (x, y), 128)
    bg = np.array(m) == 128
    if not holes:
        return bg
    # крупные замкнутые просветы (между хвостом и телом) — тоже фон, иначе внутри наклейки белое пятно;
    # только для одиночного кота: у сцены так же пропали бы белые листы, циферблаты и экраны
    a = np.array(m)
    min_area = 0.004 * h * w
    ys, xs = np.nonzero(a == 255)
    for y, x in zip(ys[::97], xs[::97]):
        if m.getpixel((int(x), int(y))) != 255:
            continue
        ImageDraw.floodfill(m, (int(x), int(y)), 64)
        comp = np.array(m) == 64
        if comp.sum() >= min_area:
            bg |= comp
        m.paste(10, mask=Image.fromarray((comp * 255).astype(np.uint8)))
    return bg


def largest(fg: np.ndarray) -> np.ndarray:
    m = Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).copy()
    best, best_n = None, 0
    ys, xs = np.nonzero(np.array(m) == 255)
    for y, x in zip(ys[::53], xs[::53]):
        if m.getpixel((int(x), int(y))) != 255:
            continue
        ImageDraw.floodfill(m, (int(x), int(y)), 100)
        comp = np.array(m) == 100
        if comp.sum() > best_n:
            best, best_n = comp, comp.sum()
        m.paste(20, mask=Image.fromarray((comp * 255).astype(np.uint8)))
    return fg & best


def sticker(src: Path, mode: str, crop=None, border_px: int = 18) -> Image.Image:
    im = Image.open(src)
    if crop:
        im = im.crop(crop)
    if im.mode == "RGBA":
        a = np.array(im)[:, :, 3]
        fg = a > 24
        flat = Image.new("RGB", im.size, CREAM)
        flat.paste(im, (0, 0), im)
        rgb = np.array(flat)
    else:
        rgb = np.array(im.convert("RGB"))
        fg = ~paper_bg(rgb, holes=(mode == "cut_holes"))
    h, w = fg.shape
    if mode == "oval":
        yy, xx = np.mgrid[0:h, 0:w]
        d = ((xx - w / 2) / (w * 0.47)) ** 2 + ((yy - h / 2) / (h * 0.47)) ** 2
        alpha = np.clip((1.0 - d) / 0.35, 0, 1) ** 1.4
        out = np.dstack([rgb, (alpha * 255).astype(np.uint8)])
        return Image.fromarray(out, "RGBA")
    if mode == "cut_main":  # только самый крупный кусок (обрывок соседнего предмета у края рамки — прочь)
        fg = largest(fg)
    # убрать мелкие крошки фона, сгладить, расширить на кайму
    m = Image.fromarray((fg * 255).astype(np.uint8))
    m = m.filter(ImageFilter.GaussianBlur(3)).point(lambda v: 255 if v > 140 else 0)
    big = m.filter(ImageFilter.GaussianBlur(border_px * 0.6)).point(lambda v: 255 if v > 8 else 0)
    big = big.filter(ImageFilter.GaussianBlur(1.6))
    pad = border_px + 6
    canvas = Image.new("RGB", (w + 2 * pad, h + 2 * pad), CREAM)
    canvas.paste(Image.fromarray(rgb), (pad, pad))
    mask = Image.new("L", canvas.size, 0)
    mask.paste(big, (pad, pad))
    # кайма за краем исходника (предмет, обрезанный рамкой): дорастить по краю
    mask = mask.filter(ImageFilter.MaxFilter(3))
    out = canvas.convert("RGBA")
    out.putalpha(mask)
    return out.crop(out.getbbox())


def main(names=None):
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (src, crop, mode) in SOURCES.items():
        if names and name not in names:
            continue
        s = sticker(ROOT / src, mode, crop)
        s.thumbnail((1100, 1100))
        s.save(OUT / f"{name}.png", optimize=True)
        print(name, s.size)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
