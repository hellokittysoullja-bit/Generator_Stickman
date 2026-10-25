"""Хук «Опять не спишь?»: телефон выскальзывает из уставших лап и падает коту на морду, удар — на «спишь».

Рисунки: А — gen/n5_bed_side.png (держит телефон над лицом), Б — gen/n6_phone_fell.png (телефон на морде; тот же
рисунок, сдвиг 1 px). Слои снимаются с А один раз и лежат в кэше рилса (.cache/anim): телефон целиком, пальцы левой
лапы поверх него, стена без телефона (свет экрана — отдельным полем, едет вместе с телефоном).

Хронометраж (от начала слова «Опять», голос с 0 с):
  0 – 0.26   держит: телефон дрожит в уставших лапах, дрожь растёт (на двойках, 12 рисунков в секунду);
  0.26 – 0.36 замах: левый край выскальзывает из лапы, телефон кренится вокруг правой лапы (на двойках);
  0.36 – удар  падение: тяжесть (путь ∝ t²), поворот, телефон разворачивается к зрителю плоскостью, смаз позади
              (на единицах — быстрое движение рисуют на каждый кадр), свет экрана едет вместе с ним;
  удар        ударная гласная «спишь»: Б; задержка на ударе 2 кадра; сжатие морды под телефоном и отскок пружиной;
              вспышка экрана; штрихи удара вылетают и тают; тряска и толчок камеры;
  дальше      Б живёт: свет экрана мерцает, морда дышит.
"""
import math
import os

import cv2
import numpy as np
from PIL import Image

import anim

SOURCES = ["gen/n5_bed_side.png", "gen/n6_phone_fell.png"]
VERSION = 7
REEL_DIR = None                     # ставит anim.scene()

# разметка рисунка (координаты рисунка 1531 px; слои живут в ×2, как исходники рилса)
PHONE_POLY = [(739.3, 233.3), (790, 232.7), (1043.3, 285), (1049, 292), (1050, 302), (1047, 312), (1036, 318),
              (1000, 319.3), (976.7, 316.7), (756.7, 268.3), (736.7, 258.3), (733.3, 245)]
TOE_ARC = [(200, 205), (240, 186), (275, 171), (310, 166), (345, 180), (375, 188), (400, 199), (425, 216)]   # в кропе
PALM = [(1988, 545), (2076, 505), (2156, 525), (2171, 615), (2166, 715), (1966, 715), (1956, 637)]            # ×2
PALM_EDGE = [(2001, 530), (1984, 566), (1970, 604), (1960, 640), (1957, 656)]                                   # ×2
PIVOT = (2084, 598)               # правая лапа держит конец телефона: вокруг неё он кренится (×2)
B_PHONE = dict(center=(641.7 * 2, 449.3 * 2), angle=-13.8, thick=57 / 41)   # где и как телефон лежит на Б
HEAD = dict(center=(1240, 880), axes=(470, 420), base_y=1200)               # морда на Б (×2): сжатие на ударе
EYES_A = [(1115, 1108, 108), (1430, 948, 96)]   # глаза на А (×2): центр, низ, полуширина — под ними мешки (ночь)

_L = None


def _cache_path():
    d = os.path.join(REEL_DIR, ".cache", "anim"); os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"phone_fall_v{VERSION}.npz")


def _x2(rel):
    import upscale
    p = os.path.join(REEL_DIR, ".cache", "anim", os.path.basename(rel).replace(".png", "_x2.png"))
    if not os.path.exists(p):
        a = np.asarray(Image.open(os.path.join(REEL_DIR, rel)).convert("RGB"))
        Image.fromarray(upscale.upscale(a, 2)).save(p)
    return np.asarray(Image.open(p).convert("RGB"))


def _nfill(img, valid, sig):
    v = valid.astype(np.float32)
    num = cv2.GaussianBlur(img * v[..., None], (0, 0), sig); den = cv2.GaussianBlur(v, (0, 0), sig)[..., None]
    return num / np.maximum(den, 1e-6), den[..., 0]


def _lowpass(img, valid, sigs):
    out, _ = _nfill(img, valid, sigs[-1])
    for s in reversed(sigs[:-1]):
        f, d = _nfill(img, valid, s); out = np.where((d > 0.15)[..., None], f, out)
    return out


def prepare():
    """Слои из рисунков А и Б (один раз; дальше — из кэша)."""
    p = _cache_path()
    if os.path.exists(p):
        z = np.load(p)
        return {k: z[k] for k in z.files}
    A = _x2(SOURCES[0]); B = _x2(SOURCES[1]).astype(np.float32)
    H, W = A.shape[:2]
    B = cv2.warpAffine(B, np.float32([[1, 0, 0], [0, 1, 2]]), (W, H), borderMode=cv2.BORDER_REFLECT)   # Б ниже на 1 px
    poly = np.float32(PHONE_POLY) * 2
    x0, y0 = int(poly[:, 0].min()) - 80, int(poly[:, 1].min()) - 80
    x1, y1 = int(poly[:, 0].max()) + 80, int(poly[:, 1].max()) + 80
    crop = A[y0:y1, x0:x1].copy()
    # телефон: GrabCut от многоугольника (контур тушью — тоже телефон)
    m = np.zeros(crop.shape[:2], np.uint8); cv2.fillPoly(m, [np.int32(poly - [x0, y0])], 1)
    gc = np.full(crop.shape[:2], cv2.GC_BGD, np.uint8)
    gc[cv2.dilate(m, np.ones((25, 25), np.uint8)) > 0] = cv2.GC_PR_BGD
    gc[m > 0] = cv2.GC_PR_FGD
    gc[cv2.erode(m, np.ones((13, 13), np.uint8)) > 0] = cv2.GC_FGD
    cv2.grabCut(cv2.cvtColor(crop, cv2.COLOR_RGB2BGR), gc, None, np.zeros((1, 65)), np.zeros((1, 65)), 6, cv2.GC_INIT_WITH_MASK)
    ph = np.isin(gc, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.uint8)
    _, lab, st, _ = cv2.connectedComponentsWithStats(ph)
    ph = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    cut = np.zeros_like(ph)
    xs = np.arange(int(TOE_ARC[0][0]), int(TOE_ARC[-1][0]))
    for x, yv in zip(xs, np.interp(xs, *np.float32(TOE_ARC).T).astype(int)):
        cut[yv:, x] = 1                              # пальцы левой лапы — поверх нижнего края телефона
    Lc = cv2.cvtColor(crop, cv2.COLOR_RGB2LAB)[..., 0]
    toes = ((m > 0) & (ph == 0) & (cut > 0)).astype(np.uint8)
    near_poly = cv2.dilate(m, np.ones((5, 5), np.uint8)) > 0
    ph = (near_poly & (toes == 0) & ((ph > 0) | (Lc < 60)) & (cut == 0)).astype(np.uint8)
    ph = cv2.morphologyEx(ph, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    phone = np.zeros((H, W), np.uint8); phone[y0:y1, x0:x1] = ph
    toe_m = np.zeros((H, W), np.uint8); toe_m[y0:y1, x0:x1] = cut & cv2.dilate(m, np.ones((41, 41), np.uint8))
    # телефон целиком: под пальцами кусок нижнего края спрятан — достраивается вдоль оси (корпус одинаков по длине)
    ang = math.degrees(math.atan2(poly[2, 1] - poly[0, 1], poly[2, 0] - poly[0, 0]))
    hull = np.zeros((H, W), np.uint8); cv2.fillPoly(hull, [cv2.convexHull(np.int32(poly))], 1)
    hidden = (hull > 0) & (phone == 0) & (toe_m > 0)
    full_phone = phone.copy(); full_rgb = A.astype(np.float32).copy()
    if hidden.any():
        c = poly.mean(0); R = cv2.getRotationMatrix2D(tuple(map(float, c)), ang, 1.0)
        rot = cv2.warpAffine(full_rgb, R, (W, H), flags=cv2.INTER_LINEAR)
        rp = cv2.warpAffine(phone.astype(np.float32), R, (W, H)) > 0.5
        rh = cv2.warpAffine(hidden.astype(np.float32), R, (W, H)) > 0.5
        ys, xs_ = np.nonzero(rh)
        span = 140
        for y, x in zip(ys, xs_):                    # тот же ряд корпуса правее пальцев
            for dx in range(20, span, 4):
                if x + dx < W and rp[y, x + dx] and not rh[y, x + dx]:
                    rot[y, x] = rot[y, x + dx]; break
        Ri = cv2.invertAffineTransform(R)
        back = cv2.warpAffine(rot, Ri, (W, H), flags=cv2.INTER_LINEAR)
        full_rgb[hidden] = back[hidden]; full_phone[hidden] = 1
    # фон без телефона: стена — продолжение ближайшей стены + зерно стены выше; ладонь правой лапы — мехом и контуром
    L = cv2.cvtColor(A, cv2.COLOR_RGB2LAB)[..., 0]; LB = cv2.cvtColor(np.clip(B, 0, 255).astype(np.uint8), cv2.COLOR_RGB2LAB)[..., 0]
    toes_only = cv2.dilate(toe_m & (1 - phone), np.ones((3, 3), np.uint8))
    hole = ((cv2.dilate(phone, np.ones((45, 45), np.uint8)) > 0) & (toes_only == 0)).astype(np.uint8)
    hole &= (1 - (toe_m & (phone == 0))).astype(np.uint8)
    af = A.astype(np.float32)
    wallA = (L > 85) & (hole == 0)
    both = wallA & (LB > 70)
    glow = np.clip(_lowpass(af, both, (25, 60, 150)) - _lowpass(B, both, (25, 60, 150)), 0, None)
    near = _lowpass(af, wallA, (10, 25, 60))
    hfA = af - cv2.GaussianBlur(af, (0, 0), 2.5)
    grain = np.roll(hfA, int(cv2.boundingRect(hole)[3] * 1.3), axis=0)
    sil = np.zeros((H, W), np.uint8); cv2.fillPoly(sil, [np.int32(PALM)], 1)
    zone = cv2.dilate(sil, np.ones((81, 81), np.uint8)) > 0
    ff, _ = _nfill(af, (L > 48) & (L < 92) & (hole == 0) & zone, 30)
    hf_big = af - cv2.GaussianBlur(af, (0, 0), 9)
    no_line = cv2.erode(((L > 42) & (L < 90)).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(np.float32)
    no_line = cv2.GaussianBlur(no_line, (0, 0), 2)[..., None]
    paw_tex = np.roll(np.clip(hf_big, -14, 14) * no_line * 0.8, -125, axis=0)
    k_fur = cv2.GaussianBlur((sil & hole).astype(np.float32), (0, 0), 1.2)[..., None]
    fill = (near + grain) * (1 - k_fur) + (ff + paw_tex) * k_fur
    edge = np.zeros((H, W), np.uint8); cv2.polylines(edge, [np.int32(PALM_EDGE)], False, 1, 6, cv2.LINE_AA)
    ink = cv2.GaussianBlur((edge & hole).astype(np.float32), (0, 0), 1.0)[..., None]
    fill = fill * (1 - ink * 0.92) + np.float32([16, 16, 20]) * ink * 0.92
    al = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 5)[..., None]
    clean = af * (1 - al) + fill * al
    # свет экрана: гладкое пятно по форме телефона; сила и цвет — по свету на стене у самого телефона (разница А и Б)
    ring = (cv2.dilate(phone, np.ones((61, 61), np.uint8)) > 0) & (hole == 0) & wallA
    col = np.median(glow[ring], axis=0) if ring.any() else np.float32([20, 30, 45])
    shape = cv2.GaussianBlur(cv2.dilate(phone, np.ones((31, 31), np.uint8)).astype(np.float32), (0, 0), 90)
    shape /= max(1e-6, float(shape[ring].mean()) if ring.any() else float(shape.max()))
    light = (np.clip(shape, 0, 1.6)[..., None] * col[None, None] * 0.8).astype(np.float32)
    # телефон уносит свой свет: всё вокруг (стена, лапы) темнеет плавно, как гаснет лампа, до тона Б.
    # Множитель — отношение гладких яркостей Б и А по стене, без резких границ (замена кусков стеной Б давала
    # рваный край у лап). Глаза и морда А не тронуты: на них свет падает и дальше — телефон летит к ним.
    lpa = _lowpass(af, both, (25, 60, 150)); lpb = _lowpass(B, both, (25, 60, 150))
    ratio = np.clip(lpb.mean(2) / np.maximum(lpa.mean(2), 1), 0.45, 1.0)
    head_a = np.zeros((H, W), np.float32); cv2.ellipse(head_a, (1280, 940), (470, 350), 0, 0, 360, 1.0, -1)
    head_a = cv2.GaussianBlur(head_a, (0, 0), 80)
    dim = cv2.GaussianBlur((1 - ratio).astype(np.float32), (0, 0), 40) * (1 - head_a)
    toes_layer = np.zeros((H, W), np.float32)
    toes_layer[:] = cv2.GaussianBlur((toe_m & (1 - full_phone) & (L < 92).astype(np.uint8)).astype(np.float32), (0, 0), 0.8)
    out = dict(A=A, B=np.clip(B, 0, 255).astype(np.uint8), clean=np.clip(clean, 0, 255).astype(np.uint8),
               light=light.astype(np.float16), dim=dim.astype(np.float16),
               phone_rgb=np.clip(full_rgb, 0, 255).astype(np.uint8),
               phone_a=cv2.GaussianBlur(full_phone.astype(np.float32), (0, 0), 0.9), toes_a=toes_layer,
               ang=np.float32(ang))
    np.savez(p, **out)
    return out


def layers():
    global _L
    if _L is None:
        d = prepare()
        ph = anim.Layer.cut(d["phone_rgb"], d["phone_a"] > 0.5, pad=8, feather=0)
        x0, y0 = ph.origin.astype(int); h, w = ph.a.shape
        ph.a = d["phone_a"][y0:y0 + h, x0:x0 + w]
        # опора телефона — правая лапа: так крен на замахе — поворот вокруг неё
        ph.pivot = np.float32(PIVOT) - ph.origin
        toes = anim.Layer.cut(d["A"], d["toes_a"] > 0.02, pad=6, feather=0)
        tx, ty = toes.origin.astype(int); th, tw = toes.a.shape
        toes.a = d["toes_a"][ty:ty + th, tx:tx + tw]
        lit = d["light"].astype(np.float32)
        lx, ly, lw, lh = cv2.boundingRect((lit.max(2) > 1.0).astype(np.uint8))
        light = anim.Layer(lit[ly:ly + lh, lx:lx + lw], np.ones((lh, lw), np.float32), np.float32(PIVOT) - (lx, ly))
        light.origin = np.float32((lx, ly))
        center_a = np.float32(np.argwhere(d["phone_a"] > 0.5).mean(0)[::-1])
        _L = dict(d=d, phone=ph, toes=toes, light=light, ang_a=float(d["ang"]), center_a=center_a,
                  head=_head_mask(d["A"].shape[:2]))
    return _L


def _head_mask(shape):
    m = np.zeros(shape, np.float32)
    cv2.ellipse(m, tuple(map(int, HEAD["center"])), tuple(map(int, HEAD["axes"])), 0, 0, 360, 1.0, -1)
    return cv2.GaussianBlur(m, (0, 0), 60)


def timing(ctx):
    """Ключевые моменты по голосу: удар — ударная гласная «спишь» (≈ 0.07 с от начала слова)."""
    w = ctx["words"]                                  # [(start, end)] слов фразы в секундах ролика
    hit = w[2][0] + 0.07
    return dict(slip=hit - 0.27, fall=hit - 0.17, hit=hit)


def phone_pose(t, T, Lr):
    """Опора телефона (правая лапа), угол и толщина в момент t (до удара)."""
    ang_a = Lr["ang_a"]
    if t < T["slip"]:                                 # держит: дрожь растёт; на двойках
        tt = anim.on_twos(t)
        amp = 0.5 + 1.6 * anim.clamp01(tt / T["slip"])
        rng = np.random.default_rng(int(round(tt * anim.DRAW_FPS)) + 7)
        return np.float32(PIVOT) + rng.uniform(-1.5, 1.5, 2) * amp, ang_a + rng.uniform(-1, 1) * amp, 1.0, None
    if t < T["fall"]:                                 # замах: левый край выскальзывает, крен вокруг правой лапы
        tt = anim.on_twos(t)
        u = anim.EASE_IN((tt - T["slip"]) / (T["fall"] - T["slip"]))
        return np.float32(PIVOT) + (0, -6 * math.sin(math.pi * u)), ang_a - 7.0 * u, 1.0, None
    # падение — на единицах: опора уходит от лапы к месту на морде (Б); тяжесть по вертикали
    u = anim.clamp01((t - T["fall"]) / (T["hit"] - T["fall"]))
    start = np.float32(PIVOT); ang0 = ang_a - 7.0
    # где на Б окажется точка телефона, бывшая у правой лапы: тот же отрезок «центр -> опора», повёрнутый и сжатый
    ca = Lr["center_a"]; off = start - ca
    b = math.radians(B_PHONE["angle"] - ang_a)
    off_b = np.float32([off[0] * math.cos(b) - off[1] * math.sin(b), off[0] * math.sin(b) + off[1] * math.cos(b)])
    end = np.float32(B_PHONE["center"]) + off_b
    pos = np.float32([start[0] + (end[0] - start[0]) * (0.25 * u + 0.75 * u ** 1.6), start[1] + (end[1] - start[1]) * anim.gravity(u)])
    ang = ang0 + (B_PHONE["angle"] - ang0) * anim.EASE_IO(u)
    thick = 1.0 + (B_PHONE["thick"] - 1.0) * u ** 2   # разворачивается к зрителю плоскостью
    return pos, ang, thick, u


def phone_on_b(T, Lr, shape):
    """Где лежит телефон на Б (маска): твёрдый — при сжатии морды сдвигается целиком, не гнётся (лист 25.10)."""
    if "phone_b" not in Lr:
        pos, ang, thick, _ = phone_pose(T["hit"] - 1e-4, T, Lr)
        L = Lr["phone"]; ones = anim.Layer(np.full_like(L.rgb, 255.0), L.a, L.pivot)
        cv = np.zeros(shape, np.float32)
        ones.draw(cv, pos, ang - Lr["ang_a"], 1.0, thick, axis=Lr["ang_a"])
        m = cv2.dilate((cv[..., 0] > 60).astype(np.uint8), np.ones((13, 13), np.uint8)).astype(np.float32)
        Lr["phone_b"] = cv2.GaussianBlur(m, (0, 0), 3)
    return Lr["phone_b"]


def bags(t):
    """Мешки под глазами проступают за первые полсекунды: ночь, не спит (на двойках — это рисунок)."""
    return 0.35 + 0.65 * anim.EASE_OUT(anim.on_twos(t) / 0.6)


def frame(t, ctx):
    """Картинка исходника (×2) и поправка камеры в момент t ролика."""
    Lr = layers(); d = Lr["d"]; T = timing(ctx)
    cam = dict(dx=0.0, dy=0.0, zoom=1.0, rot=0.0)
    # вход: резкий наезд с первого кадра (80% пути за первую треть), удар звука — на 0
    cam["zoom"] *= 1 / (1 + 0.12 * (1 - anim.SNAP(t / 0.30)))   # >1 — ближе: старт шире на 12%, к 0.3 с — на месте
    if t < T["hit"]:
        pos, ang, thick, u = phone_pose(t, T, Lr)
        if u is None:                                  # телефон в лапах: свет экрана на стене как нарисован
            img = anim.eye_bags(d["clean"].astype(np.float32), EYES_A, bags(t))
            Lr["phone"].draw(img, pos, ang - Lr["ang_a"])
            Lr["toes"].draw(img, Lr["toes"].home())
            return img, cam
        img = anim.eye_bags(d["clean"].astype(np.float32), EYES_A, bags(t))
        img *= 1 - d["dim"].astype(np.float32)[..., None] * u
        lt = Lr["light"]                               # свет экрана едет с телефоном и гаснет на стене
        lt_img = np.zeros_like(img); lt.draw(lt_img, pos, ang - Lr["ang_a"])
        img += lt_img * u
        prev = phone_pose(max(T["fall"], t - 1 / 30), T, Lr)[0]
        v = (pos - prev) * 0.9
        Lr["phone"].draw(img, pos, ang - Lr["ang_a"], 1.0, thick, axis=Lr["ang_a"], smear=(float(v[0]), float(v[1])))
        Lr["toes"].draw(img, Lr["toes"].home())
        cam["zoom"] *= 1 + 0.03 * u                    # камера тянется за падением
        return img, cam
    # удар и после: рисунок Б
    th = t - T["hit"]
    def squash(tt):                  # удар и первый отскок на единицах, дальше на двойках; задержка 2 кадра
        h_ = tt - T["hit"]
        if h_ < 0: return 0.0
        q = h_ if h_ < 0.2 else anim.on_twos(h_)
        return 0.07 * anim.spring(max(0.0, q - 2 / 30), freq=4.5, damping=0.32)
    img = d["B"].astype(np.float32)                    # морда сминается под телефоном, уши догоняют, объём держится
    img = anim.squash_follow(img, Lr["head"], (HEAD["center"][0], HEAD["base_y"]), squash, t, lag=0.10,
                             focus=tuple(int(v) for v in B_PHONE["center"]), rigid=[phone_on_b(T, Lr, img.shape)])
    flash = math.exp(-th / 0.09) if th >= 0 else 0.0   # вспышка экрана: свет на морде и стене
    if flash > 0.02:
        g = np.zeros(img.shape[:2], np.float32)
        cv2.ellipse(g, tuple(map(int, B_PHONE["center"])), (420, 230), B_PHONE["angle"], 0, 360, 1.0, -1)
        g = cv2.GaussianBlur(g, (0, 0), 70)[..., None]
        img += g * np.float32([28, 40, 58]) * flash
    for spread, seed in (((198, 250), 5), ((290, 342), 6)):    # два веера по бокам: верх кадра — под якорем хука
        anim.impact_strokes(img, (B_PHONE["center"][0], B_PHONE["center"][1] - 30), anim.on_twos(max(0.0, th - 2 / 30)),
                            r0=290, r1=400, n=3, spread=spread, width=18, color=(220, 232, 255), seed=seed, life=0.30)
    if th >= 2 / 30:                                  # тряска после задержки, гаснет за 0.4 с; толчок камеры пружиной
        k = math.exp(-(th - 2 / 30) / 0.12)
        cam["dx"] += 16 * k * math.sin(th * 95); cam["dy"] += 12 * k * math.cos(th * 77)
        cam["rot"] += 0.5 * k * math.sin(th * 61)
    cam["zoom"] *= 1 + 0.07 * max(0.0, anim.spring(th, freq=3.0, damping=0.45)) + 0.03
    return img, cam
