"""Слои хука рилса 19 «Встал рано, а ты опоздал?» для HyperFrames — по базе рилса 13.

Рисунок gen/d1_clock.png ×2 (.cache/anim/d1_clock_x2.png, upscale.py); координаты ×2, сняты сеткой anim.grid 04.11.
Слои: часы целиком (обод, циферблат, подвес) — качаются на гвозде; минутная и часовая стрелки — крутятся; кот (тело со
шарфом и ботинками); хвост (сеткой с физикой, tail_rig); три капли пота. Стена с дверью и полом — фон
(anim.inpaint_bg под каждым предметом). Стена и пол цветные — кота режем по туши (тёмное), а не по «не бумаге»."""
import json
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); REEL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REEL, "..", "..", "..", "scripts"))
import anim  # noqa: E402
import tail_rig  # noqa: E402

OUT = os.path.join(HERE, "kit")
CACHE = os.path.join(REEL, ".cache", "anim")
ORIGIN = (0, 0)
SIZE = (2048, 3072)
CLOCK_C = (982, 762)              # ось стрелок
NAIL = (982, 88)                  # гвоздь подвеса — ось качания часов
FACE_R, RIM_R0, RIM_R1 = 470, 470, 590
HANGER_BOX = (800, 30, 1170, 240)
CAT_POLY = [(520, 1500), (1000, 1420), (1200, 1450), (1240, 1600), (1300, 1720), (1450, 1790), (1460, 2200),
            (1420, 2560), (1200, 2570), (1160, 2850), (500, 2860), (520, 2620), (600, 2500), (430, 2430), (420, 2200),
            (540, 2150), (520, 2070), (430, 2060), (430, 1900), (520, 1880)]
TAIL_POLY = [(100, 1540), (520, 1540), (520, 2150), (430, 2190), (420, 2430), (610, 2470), (640, 2620), (100, 2620)]
TAIL_PIVOT = (620, 2500)          # основание хвоста у тела
DROPS_BOX = (1195, 1430, 1410, 1740)
FEET = (850, 2800)
HEAD = (1000, 1880)


def fill_smooth(img, hole, k=8, seed=19):
    """Гладкая стена за часами: LaMa на дыре в полстены дорисовывала призрак обода (кольцо из тени). Стена здесь —
    ровный градиент, поэтому заливка — TELEA на копии в k раз меньше + зерно этой же стены, без придумывания линий."""
    H, W = hole.shape
    u8 = np.clip(img, 0, 255).astype(np.uint8)
    sm = cv2.resize(u8, (W // k, H // k), interpolation=cv2.INTER_AREA)
    hs = (cv2.resize(hole.astype(np.uint8), (W // k, H // k), interpolation=cv2.INTER_AREA) > 0).astype(np.uint8)
    hs = cv2.dilate(hs, np.ones((3, 3), np.uint8))
    f = cv2.inpaint(sm, hs, 12, cv2.INPAINT_TELEA)
    f = cv2.GaussianBlur(f.astype(np.float32), (0, 0), 2.0)
    up = cv2.resize(f, (W, H), interpolation=cv2.INTER_CUBIC)
    ring = cv2.dilate(hole.astype(np.uint8), np.ones((61, 61), np.uint8)).astype(bool) & ~hole
    hp = img - cv2.GaussianBlur(img, (0, 0), 3)
    sd = float(hp[ring].std()) if ring.any() else 2.0
    rng = np.random.default_rng(seed)
    noise = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.8)
    noise *= sd / max(float(noise.std()), 1e-6)
    up = up + noise[..., None]
    a = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 3)[..., None]
    a = np.maximum(a, hole[..., None].astype(np.float32))
    return img * (1 - a) + up * a


def fill_holes(m):
    m = (m > 0).astype(np.uint8)
    h, w = m.shape
    ff = m.copy(); pad = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 1)
    return (m | (1 - ff)).astype(np.uint8)


def poly_mask(shape, poly):
    reg = np.zeros(shape[:2], np.uint8); cv2.fillPoly(reg, [np.int32(poly)], 1); return reg


def lab_l(A):
    return cv2.cvtColor(np.clip(A, 0, 255).astype(np.uint8), cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32) * 100 / 255


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.path.join(CACHE, "d1_clock_x2.png")).convert("RGB")).astype(np.float32)
    H, Wd = A.shape[:2]
    L = lab_l(A); sat = A.max(2) - A.min(2)
    yy, xx = np.mgrid[0:H, 0:Wd]
    r = np.hypot(xx - CLOCK_C[0], yy - CLOCK_C[1])
    ang = np.degrees(np.arctan2(yy - CLOCK_C[1], xx - CLOCK_C[0]))          # 0° — вправо, по часовой (y вниз)
    # стрелки: тёмное внутри циферблата, по углу (минутная ~ -61°, часовая ~ -152°), ступица — отдельно
    dark = (L < 45) & (r < FACE_R - 20)
    def adiff(a, b): return np.abs((a - b + 180) % 360 - 180)
    hub = dark & (r < 52)
    minute = dark & ~hub & (adiff(ang, -61) < 14)
    hour = dark & ~hub & (adiff(ang, -153) < 16)
    k3 = np.ones((3, 3), np.uint8)
    minute = cv2.morphologyEx(minute.astype(np.uint8), cv2.MORPH_CLOSE, k3)
    hour = cv2.morphologyEx(hour.astype(np.uint8), cv2.MORPH_CLOSE, k3)
    hub = fill_holes(cv2.morphologyEx(((L < 60) & (r < 60)).astype(np.uint8), cv2.MORPH_CLOSE, k3))
    # всё, что лежит на циферблате (стрелки и их тени), стирается с циферблата
    on_face = ((L < 92) & (r < FACE_R - 15)).astype(np.uint8)
    face_hole = cv2.dilate(on_face, np.ones((15, 15), np.uint8)) > 0
    Af = anim.inpaint_bg(A, face_hole, cache_dir=CACHE)
    # часы: циферблат + обод (оранжевый и тушь) + подвес
    rim = ((sat > 35) | (L < 60)) & (r >= RIM_R0) & (r < RIM_R1)
    x0, y0, x1, y1 = HANGER_BOX
    hang = np.zeros((H, Wd), bool); hang[y0:y1, x0:x1] = True
    hanger = hang & ((sat > 35) | (L < 70)) & (r >= RIM_R0)
    clock = fill_holes(cv2.morphologyEx((rim | hanger | (r < RIM_R0)).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)))
    clock &= ((r < 575) | hang).astype(np.uint8)
    # кот: тушь и шерсть (тёмное) внутри многоугольника, всё внутри контура — коту (глаза, рот, шарф, ботинки)
    # капли пота: голубая заливка и её тушь, каждая отдельно (ink_objects слил их в одно пятно с ухом)
    bx0, by0, bx1, by1 = DROPS_BOX
    inbox = np.zeros(A.shape[:2], bool); inbox[by0:by1, bx0:bx1] = True
    blue = inbox & (A[..., 2] - A[..., 0] > 14) & (L > 50)
    blue = cv2.morphologyEx(blue.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    near = cv2.dilate(blue, np.ones((13, 13), np.uint8)) > 0
    dm = fill_holes(cv2.morphologyEx((blue > 0) | (near & (L < 62) & inbox), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) if False else
                    cv2.morphologyEx(((blue > 0) | (near & (L < 62) & inbox)).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(dm)
    drops = [(lab == i).astype(np.uint8) for i in range(1, n) if st[i, 4] > 600]
    drops_all = cv2.dilate(np.maximum.reduce(drops), np.ones((7, 7), np.uint8)) if drops else 0
    cat_reg, tail_reg = poly_mask(A.shape, CAT_POLY), poly_mask(A.shape, TAIL_POLY)
    cat_reg = cat_reg & (1 - drops_all) if drops else cat_reg
    # силуэт по туши: контур кота, шарфа и ботинок толстый и тёмный — замкнуть и залить всё внутри (глаза, шарф,
    # подошвы); тень на полу светлее (L≈48–65) и остаётся фону
    cat_dark = ((((L < 38)) | ((L < 72) & (sat < 42))) & (cat_reg > 0)).astype(np.uint8)   # тушь + серая шерсть, шарф, ботинки
    cat = fill_holes(cv2.morphologyEx(cat_dark, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))) & cat_reg
    cat = anim.keep_attached(cat)
    flame = (sat > 70) & (A[..., 0] > 180) & (tail_reg > 0) & (yy < 2160)
    tail_ink = ((L < 42) & (tail_reg > 0)) | flame
    tail_ink = cv2.morphologyEx(tail_ink.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    tail = anim.keep_attached(fill_holes(cv2.morphologyEx(tail_ink, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))) & tail_reg & ~cat.astype(bool))
    full = (cat | tail).astype(np.uint8)
    tail, body = anim.split_part(tail, cat)
    tail, body, tail_fill = anim.claim_strokes(A, tail, body)
    tail = anim.underlap(tail, body, full, around=(*TAIL_PIVOT, 200))
    drops.sort(key=lambda o: np.argwhere(o)[:, 0].mean())
    bg = Af.copy()
    flame_all = ((sat > 70) & (A[..., 0] > 180) & (tail_reg > 0) & (yy < 2160)).astype(np.uint8)   # оторванные язычки огня — со стены вон
    bg = fill_smooth(bg, cv2.dilate(clock, np.ones((41, 41), np.uint8)) > 0)    # часы с тенью — гладкой стеной
    for m in [full | flame_all] + drops:
        hole = cv2.dilate(m.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
        bg = anim.inpaint_bg(bg, hole, cache_dir=CACHE)
    Ap, Afp, bg = anim.paper_like(A), anim.paper_like(Af), anim.paper_like(bg)
    Ap_tail = Ap
    if tail_fill.any():
        u8 = np.clip(Ap, 0, 255).astype(np.uint8)
        Ap_tail = cv2.inpaint(u8, cv2.dilate(tail_fill, np.ones((3, 3), np.uint8)), 4, cv2.INPAINT_TELEA).astype(Ap.dtype)
    layers = {}
    parts = [("clock", Afp, clock, False), ("minute", Ap, minute, True), ("hour", Ap, hour, True), ("hub", Ap, hub, True),
             ("tail", Ap_tail, tail, True), ("body", Ap, body, True)]
    parts += [(f"drop{i}", Ap, d, True) for i, d in enumerate(drops)]
    for name, img, m, keep in parts:
        anim.save_layer(OUT, name, img, m.astype(np.uint8), layers, keep_attached_=keep)
    ox, oy = ORIGIN; w, h = SIZE
    Image.fromarray(np.clip(bg[oy:oy + h, ox:ox + w], 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    tx, ty = layers["tail"]["xy"]
    tail_rig.prepare_part(os.path.join(OUT, "tail.png"), attach=(TAIL_PIVOT[0] - tx, TAIL_PIVOT[1] - ty), out_dir=OUT, name="tail")
    meta = dict(origin=ORIGIN, size=SIZE, layers=layers, tail_pivot=TAIL_PIVOT, feet=FEET, head=HEAD, clock_c=CLOCK_C,
                nail=NAIL, drops=len(drops), fps=30)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    # лист слоёв на синем — глазами
    sheet = np.zeros((H, Wd, 3), np.float32); sheet[:] = (60, 90, 170)
    for name, *_ in parts:
        L_ = layers[name]; im = np.asarray(Image.open(os.path.join(OUT, name + ".png")).convert("RGBA")).astype(np.float32)
        x, y = L_["xy"]; hh, ww = im.shape[:2]; a = im[..., 3:4] / 255
        sheet[y:y + hh, x:x + ww] = sheet[y:y + hh, x:x + ww] * (1 - a) + im[..., :3] * a
    left = ((L < 45) & ~cv2.dilate(np.maximum.reduce([clock, full] + drops), np.ones((5, 5), np.uint8)).astype(bool))
    Image.fromarray((left * 255).astype(np.uint8)).resize((512, 768)).save(os.path.join(CACHE, "kit_left.png"))
    Image.fromarray(np.clip(np.concatenate([sheet, bg], 1), 0, 255).astype(np.uint8)).resize((1024, 768)).save(
        os.path.join(CACHE, "kit_sheet.jpg"))
    print(json.dumps({k: v for k, v in meta.items() if k != "layers"}), {k: (v["xy"], v["wh"]) for k, v in layers.items()})


if __name__ == "__main__":
    main()
