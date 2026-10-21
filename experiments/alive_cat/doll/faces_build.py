"""Лица куклы из кадров GPT-Image-2 (веселый с язычком, сон с дугами-глазами): совмещение с эталоном героя
(look/hero.png) и вырезание заплаток лица. Один раз при подготовке, CPU, бесплатно (кадры уже сгенерированы:
faces/<имя>_src.png, RGBA или RGB на любом фоне — фон нигде не нужен, заплатка целиком внутри головы).

Совмещение: по двум зелёным глазам (центры -> масштаб и сдвиг, без поворота), затем уточнение сдвига ECC по серому
лобовой части. Заплатка = область лица, где сгенерированный кадр отличается от эталона, с мягким краем; тон меха
вокруг подгоняется под эталон (низкие частоты), чтобы шва не было."""
import os
import numpy as np
import cv2
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
HERO = os.path.join(HERE, "../../../look/hero.png")
EYES = np.load(os.path.join(HERE, "eyes.npy"))            # (cx, cy, rx, ry) обоих глаз эталона


def green_centers(rgb):
    f = rgb.astype(np.int32); r, g, b = f[..., 0], f[..., 1], f[..., 2]
    m = ((g > 150) & (g - b > 60) & (g - r > 5)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    idx = sorted(range(1, n), key=lambda i: -st[i, cv2.CC_STAT_AREA])[:2]
    if len(idx) < 2: raise RuntimeError("зелёные глаза не найдены")
    c = sorted([tuple(cen[i]) for i in idx], key=lambda p: p[0])
    return c, [int(st[i, cv2.CC_STAT_AREA]) for i in idx]


def register(gen_rgb, hero_rgb):
    """Преобразование генерации -> координаты эталона: масштаб s и сдвиг (tx, ty). Возвращает 2x3."""
    (gl, gr), _ = green_centers(gen_rgb)
    hl, hr = (float(EYES[0, 0]), float(EYES[0, 1])), (float(EYES[1, 0]), float(EYES[1, 1]))
    s = (hr[0] - hl[0]) / (gr[0] - gl[0])
    tx = (hl[0] + hr[0]) / 2 - s * (gl[0] + gr[0]) / 2
    ty = (hl[1] + hr[1]) / 2 - s * (gl[1] + gr[1]) / 2
    return np.array([[s, 0, tx], [0, s, ty]], np.float32)


def refine(M, gen_rgb, hero_rgb, roi):
    """Уточнение сдвига по серому лбу и щекам (без рта и глаз): ECC, перенос."""
    H, W = hero_rgb.shape[:2]
    w = cv2.warpAffine(gen_rgb, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    g0 = cv2.GaussianBlur(cv2.cvtColor(hero_rgb, cv2.COLOR_RGB2GRAY), (0, 0), 2).astype(np.float32)
    g1 = cv2.GaussianBlur(cv2.cvtColor(w, cv2.COLOR_RGB2GRAY), (0, 0), 2).astype(np.float32)
    x0, y0, x1, y1 = roi
    mask = np.zeros((H, W), np.uint8); mask[y0:y1, x0:x1] = 255
    warp = np.eye(2, 3, dtype=np.float32)
    try:
        cc, warp = cv2.findTransformECC(g0, g1, warp, cv2.MOTION_TRANSLATION,
                                        (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), mask, 5)
    except cv2.error:
        return M, 0.0, (0.0, 0.0)
    d = (float(warp[0, 2]), float(warp[1, 2]))
    M2 = M.copy(); M2[0, 2] += -d[0]; M2[1, 2] += -d[1]      # ECC ищет сдвиг g1 -> g0 в обратной форме
    return M2, float(cc), d


# ----------------------------------------------------------------------------- заплатки
def ellipse_mask(shape, cx, cy, rx, ry, feather):
    H, W = shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    f = feather / max(rx, ry)
    return np.clip((1 - d) / f, 0, 1)


def smooth01(x):
    return x * x * (3 - 2 * x)


def tone_match(gen, hero, mask):
    """Подогнать низкие частоты заплатки к эталону по кольцу вокруг неё (мех вокруг рта не должен менять тон)."""
    ring = (mask < 0.02) & (cv2.dilate((mask > 0.02).astype(np.uint8), np.ones((41, 41), np.uint8)) > 0)
    if ring.sum() < 50: return gen
    off = (hero[ring].astype(np.float32) - gen[ring].astype(np.float32)).mean(0)
    return np.clip(gen.astype(np.float32) + off, 0, 255)


def build_patch(name, aligned, hero, ellipses, feather=12, keep_nose=None):
    """Заплатка из выровненного кадра: объединение эллипсов (cx, cy, rx, ry) с мягким краем. keep_nose — (cx, cy, rx, ry):
    область, которая остаётся эталонной (нос), вычитается из маски."""
    H, W = hero.shape[:2]
    m = np.zeros((H, W), np.float32)
    for e in ellipses: m = np.maximum(m, smooth01(ellipse_mask((H, W), *e, feather)))
    if keep_nose is not None: m = m * (1 - smooth01(ellipse_mask((H, W), *keep_nose, 6)))
    g = tone_match(aligned, hero, m)
    ys, xs = np.nonzero(m > 0)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    np.savez_compressed(os.path.join(HERE, "faces", f"{name}.npz"), box=np.array([x0, y0, x1, y1]),
                        rgb=g[y0:y1, x0:x1].astype(np.uint8), a=(m[y0:y1, x0:x1] * 255).astype(np.uint8))
    out = hero.astype(np.float32).copy()
    out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - m[y0:y1, x0:x1, None]) + g[y0:y1, x0:x1] * m[y0:y1, x0:x1, None]
    return out.astype(np.uint8)


def on_white(path):
    im = Image.open(path).convert("RGBA"); bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
    return np.asarray(bg.convert("RGB"))


def register_sift(gen_rgb, hero_rgb):
    """Совмещение без зелёных глаз (закрытые глаза): SIFT по голове, подобие (масштаб + сдвиг), RANSAC."""
    sift = cv2.SIFT_create(4000)
    g0 = cv2.cvtColor(hero_rgb, cv2.COLOR_RGB2GRAY); g1 = cv2.cvtColor(gen_rgb, cv2.COLOR_RGB2GRAY)
    k0, d0 = sift.detectAndCompute(g0, None); k1, d1 = sift.detectAndCompute(g1, None)
    mt = cv2.BFMatcher().knnMatch(d1, d0, k=2)
    good = [m for m, n in mt if m.distance < 0.7 * n.distance]
    src = np.float32([k1[m.queryIdx].pt for m in good]); dst = np.float32([k0[m.trainIdx].pt for m in good])
    M, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=2.0, maxIters=5000)
    return M.astype(np.float32), int(inl.sum()), len(good)


HERO_CHEEK_ROI = ((380, 420, 570, 530), (700, 420, 900, 530))     # рыжие полоски щёк на эталоне: левая и правая


def _orange(rgb, roi):
    x0, y0, x1, y1 = [int(v) for v in roi]
    sub = rgb[max(0, y0):y1, max(0, x0):x1].astype(np.int32); r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    m = (r > 190) & (g > 90) & (g < 175) & (b < 100) & (r - g > 50)
    ys, xs = np.nonzero(m)
    if len(xs) < 40: raise RuntimeError("рыжие полоски не найдены")
    return (xs.mean() + max(0, x0), ys.mean() + max(0, y0))


def register_cheeks(gen_rgb, hero_rgb, M0):
    """Совмещение по рыжим полоскам щёк (есть при любых глазах и рте): масштаб и сдвиг по двум центрам. M0 — грубое
    приближение gen -> hero (SIFT), по нему в кадре генерации находятся те же две области."""
    Mi = cv2.invertAffineTransform(M0)
    hc = [_orange(hero_rgb, roi) for roi in HERO_CHEEK_ROI]
    gc = []
    for roi in HERO_CHEEK_ROI:
        c = np.array([[(roi[0] + roi[2]) / 2, (roi[1] + roi[3]) / 2]], np.float32) @ Mi[:, :2].T + Mi[:, 2]
        k = 1 / M0[0, 0]; hw, hh = (roi[2] - roi[0]) * k * .75, (roi[3] - roi[1]) * k * .75
        gc.append(_orange(gen_rgb, (c[0, 0] - hw, c[0, 1] - hh, c[0, 0] + hw, c[0, 1] + hh)))
    s = (hc[1][0] - hc[0][0]) / (gc[1][0] - gc[0][0])
    tx = (hc[0][0] + hc[1][0]) / 2 - s * (gc[0][0] + gc[1][0]) / 2
    ty = (hc[0][1] + hc[1][1]) / 2 - s * (gc[0][1] + gc[1][1]) / 2
    return np.array([[s, 0, tx], [0, s, ty]], np.float32)


HERO_NOSE_ROI = (585, 430, 650, 485)


def _nose(rgb, roi):
    x0, y0, x1, y1 = [int(v) for v in roi]
    sub = rgb[y0:y1, x0:x1].astype(np.int32); r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    m = (r > 120) & (r - g > 25) & (r - b > 20) & (g > 70) & (r < 245) & ~((g > 150) & (b < 100))
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    ys, xs = np.nonzero(m)
    if len(xs) < 25: raise RuntimeError("нос не найден")
    return (xs.mean() + x0, ys.mean() + y0)


def register_local(gen_rgb, hero_rgb, M0):
    """Для заплаток лица: масштаб — по полоскам щёк, положение — по носу (ближайший общий ориентир к рту и глазам)."""
    Mc = register_cheeks(gen_rgb, hero_rgb, M0)
    s = Mc[0, 0]
    hn = _nose(hero_rgb, HERO_NOSE_ROI)
    Mi = cv2.invertAffineTransform(M0)
    c = np.array([[(HERO_NOSE_ROI[0] + HERO_NOSE_ROI[2]) / 2, (HERO_NOSE_ROI[1] + HERO_NOSE_ROI[3]) / 2]], np.float32) @ Mi[:, :2].T + Mi[:, 2]
    k = 1 / M0[0, 0]; w = 60 * k
    gn = _nose(gen_rgb, (c[0, 0] - w, c[0, 1] - w, c[0, 0] + w, c[0, 1] + w))
    return np.array([[s, 0, hn[0] - s * gn[0]], [0, s, hn[1] - s * gn[1]]], np.float32), hn, gn


def happy_mouth(hero):
    g = on_white(os.path.join(HERE, "faces", "happy_src.png"))
    M = register(g, hero)                      # глаза в кадре те же, зелёные: по ним рот встаёт точнее, чем по носу (замер глазами)
    H, W = hero.shape[:2]
    al = cv2.warpAffine(g, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return build_patch("happy_mouth", al, hero, [(612, 497, 62, 48)], feather=14, keep_nose=(617, 457, 20, 14))


def sleep_eyes(hero, dy=-22):
    """Дуги закрытых глаз: только чернила (покрытие по тёмному против меха), поверх меха куклы без глаз. dy — подъём дуг
    к уровню глаз эталона."""
    from scipy import ndimage
    g = on_white(os.path.join(HERE, "faces", "sleep_src.png"))
    M0, _, _ = register_sift(g, hero); M, _, _ = register_local(g, hero, M0)
    M = M.copy(); M[1, 2] += dy
    H, W = hero.shape[:2]
    lum = cv2.cvtColor(g, cv2.COLOR_RGB2GRAY).astype(np.float32)
    fur = cv2.medianBlur(lum.astype(np.uint8), 51).astype(np.float32)
    cov = np.clip((fur - lum) / np.maximum(fur - 18, 1), 0, 1)
    cov = np.where(cov > .12, cov, 0); cov = np.clip((cov - .12) / .6, 0, 1)
    ink = cv2.warpAffine(cov, M, (W, H), flags=cv2.INTER_AREA if M[0, 0] < 1 else cv2.INTER_CUBIC, borderValue=0)
    rgb = cv2.warpAffine(g, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    m = np.zeros((H, W), np.float32)
    for cx, cy, rx, ry in EYES:
        m = np.maximum(m, (ellipse_mask((H, W), cx, cy, rx + 14, ry + 16, 2) > 0).astype(np.float32))
    a = ink * m
    lab, n = ndimage.label(a > .2, structure=np.ones((3, 3)))
    sizes = ndimage.sum(a > .2, lab, range(1, n + 1))
    keep = 1 + np.argsort(-np.asarray(sizes))[:2]                     # две дуги; рыжие обводки и усы отпадают
    mk = cv2.dilate(np.isin(lab, keep).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
    a = a * mk
    ys, xs = np.nonzero(a > 0.01); x0, y0, x1, y1 = xs.min() - 1, ys.min() - 1, xs.max() + 2, ys.max() + 2
    np.savez_compressed(os.path.join(HERE, "faces", "sleep_eyes.npz"), box=np.array([x0, y0, x1, y1]),
                        rgb=rgb[y0:y1, x0:x1].astype(np.uint8), a=(a[y0:y1, x0:x1] * 255).astype(np.uint8))


if __name__ == "__main__":
    hero = np.asarray(Image.open(HERO).convert("RGB"))
    for fn, src in ((happy_mouth, "happy_src.png"), (sleep_eyes, "sleep_src.png")):
        if os.path.exists(os.path.join(HERE, "faces", src)):
            fn(hero)
        else:
            print(f"нет faces/{src} — лицо не собирается (эталон снят, см. look/README.md, правило эталонов)")
