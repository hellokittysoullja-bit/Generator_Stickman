#!/usr/bin/env python3
"""Переходы по смыслу на склейке ручного монтажа длинного ролика (владелец 15.11, пункт 3: «почти все стыки — простые
склейки… переходы по смыслу»). Только по желанию: план edit.json с полем

    "transition": {"kind": "move" | "through" | "light", "why": "зачем этот переход по смыслу", ...}

Без поля ничего не меняется — сборка байт в байт прежняя (правило владельца 15.11: новое — только с его согласия).

  move     переход по движению: камера уходящего плана разгоняется в сторону "dir" (left/right/up/down — куда едет
           камера) и входящий план прилетает с той же стороны, тормозя; смаз по направлению. Скорость на стыке одна
           (разгон t² и торможение 1−(1−t)² сходятся с одной производной) — глаз не спотыкается.
  through  переход по форме: уходящий план влетает в точку "from_point" (свой рисунок, px), входящий выходит из точки
           "point" (свой рисунок, px) — круглое в круглое, экран в экран; радиальное размытие, пока летит.
  light    мягкий переход света при сильном перепаде яркости (чёрный кот крупно → белая бумага): LIGHT_FRAMES кадров с
           каждой стороны тянутся к среднему тону другой стороны, на стыке средняя яркость одна. Это не наплыв двух
           картинок: смешивается с ровным тоном, сама склейка остаётся на своём кадре.

Склейка остаётся на том же кадре (на начале слова, PHRASE LOCK): переход занимает кадры по обе стороны, а не сдвигает
её. Длина — MOVE_SEC/THROUGH_* (0,2–0,25 с на сторону) и LIGHT_FRAMES (3 + 3 кадра при 24 к/с).
Звук: move и through — движение, им нужен свой "sound" у плана (свист можно); light — как у простой склейки
(long_montage.transition_checks)."""
import numpy as np

VERSION = 1
KINDS = ("move", "through", "light")
DIRS = {"left": (-1, 0), "right": (1, 0), "up": (0, -1), "down": (0, 1)}
MOVE_SEC = 0.2            # на каждую сторону стыка
MOVE_SHIFT = 0.42         # на сколько ширины экрана уезжает картинка за полперехода
MOVE_BLUR = 70            # px смаза на пике скорости (1920 px экрана)
THROUGH_OUT_SEC = 0.2
THROUGH_IN_SEC = 0.25
THROUGH_ZOOM = 1.9        # во сколько раз ближе в точке стыка
THROUGH_BLUR = 0.12       # доля радиуса радиального размытия на пике
LIGHT_FRAMES = 3          # кадров с каждой стороны; на стыке — половина пути к тону другой стороны


def spec(shot):
    """Поле transition плана edit.json -> словарь для сегмента (или None). Ошибки формы — ValueError."""
    tr = shot.get("transition")
    if not tr:
        return None
    if tr.get("kind") not in KINDS:
        raise ValueError(f"transition.kind «{tr.get('kind')}» — один из {', '.join(KINDS)}")
    out = {"kind": tr["kind"], "v": VERSION}
    if tr["kind"] == "move":
        if tr.get("dir") not in DIRS:
            raise ValueError(f"transition move: dir «{tr.get('dir')}» — left/right/up/down (куда едет камера)")
        out["dir"] = tr["dir"]
    if tr["kind"] == "through":
        for k in ("point", "from_point"):
            if tr.get(k) is not None:
                out[k] = [float(v) for v in tr[k]]
    return out


def _sides(seg, t, fps):
    """(сторона, u) — 'in' с u от 0 у стыка, 'out' с u от 0 у стыка (u растёт ОТ стыка), или (None, None)."""
    tin, tout = seg.get("trans"), seg.get("trans_out")
    if tin:
        d = {"move": MOVE_SEC, "through": THROUGH_IN_SEC, "light": LIGHT_FRAMES/fps}[tin["kind"]]
        if t - seg["t0"] < d - 1e-9:
            return "in", tin, (t - seg["t0"])/d
    if tout:
        d = {"move": MOVE_SEC, "through": THROUGH_OUT_SEC, "light": LIGHT_FRAMES/fps}[tout["kind"]]
        # последний кадр плана — t1 − 1/fps: он и есть «у стыка»
        left = seg["t1"] - 1.0/fps - t
        if left < d - 1e-9:
            return "out", tout, max(0.0, left)/d
    return None, None, None


def active(seg, t, fps):
    return _sides(seg, t, fps)[0] is not None


def needs_light(seg):
    return any((x or {}).get("kind") == "light" for x in (seg.get("trans"), seg.get("trans_out")))


PAPER = (250.0, 247.0, 240.0)     # canvas.CREAM: за краем холста — та же бумага


def camera_window(seg, t, fps, win, off):
    """Окно камеры (координаты холста, БЕЗ зажима в холст) на кадре перехода move/through, иначе None. Двигается сама
    камера по миру рисунка — в кадр въезжает настоящий соседний рисунок, а за краем холста кремовая бумага (первая
    версия сдвигала готовый кадр с повтором крайнего столбца: L03 15.11, фраза 47 — оранжевые полосы через экран)."""
    side, tr, u = _sides(seg, t, fps)
    if side is None or tr["kind"] not in ("move", "through"):
        return None
    x0, y0, x1, y1 = win
    ww, hh = x1 - x0, y1 - y0
    g = (1 - u)**2                                  # путь от стыка: 1 у стыка; out — разгон, in — торможение
    if tr["kind"] == "move":
        dx, dy = DIRS[tr["dir"]]
        sgn = 1 if side == "out" else -1           # out: камера уходит вперёд; in: приходит из-за спины
        sh = sgn*MOVE_SHIFT*g*ww
        return (x0 + dx*sh, y0 + dy*sh*hh/ww, x1 + dx*sh, y1 + dy*sh*hh/ww)
    pt = tr.get("point" if side == "in" else "from_point")
    cx, cy = (x0 + x1)/2, (y0 + y1)/2
    px, py = (pt[0] + off[0], pt[1] + off[1]) if pt else (cx, cy)
    z = 1 + (THROUGH_ZOOM - 1)*g
    nx, ny = cx + (px - cx)*g, cy + (py - cy)*g     # к стыку центр окна приходит в точку формы
    return (nx - ww/z/2, ny - hh/z/2, nx + ww/z/2, ny + hh/z/2)


def apply(f, seg, t, fps, win, off, other_mean=None, moved=False):
    """Кадр f (float HxWx3) с переходом в момент t плана seg. other_mean — средний тон кадра по другую сторону стыка
    (для light). moved — окно камеры уже сдвинуто (camera_window): остаётся смаз; иначе (сцена на бумаге) кадр
    сдвигается целиком, за краем — бумага."""
    import cv2
    side, tr, u = _sides(seg, t, fps)
    if side is None:
        return f
    H, W = f.shape[:2]
    f = np.ascontiguousarray(f, np.float32)
    if tr["kind"] == "light":
        if other_mean is None:
            return f
        n = LIGHT_FRAMES
        i = int(round(u*n))                         # 0 — кадр у стыка
        a = 0.5*(n - i)/n
        return f*(1 - a) + np.asarray(other_mean, np.float32)[None, None, :]*a
    g = (1 - u)**2
    if tr["kind"] == "move":
        dx, dy = DIRS[tr["dir"]]
        if not moved:
            sgn = 1 if side == "out" else -1
            shift = -sgn*MOVE_SHIFT*g*W                  # камера вправо -> картинка влево
            M = np.float32([[1, 0, dx*shift], [0, 1, dy*shift*H/W]])
            f = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=PAPER)
        n = int(MOVE_BLUR*(W/1920)*2*(1 - u)) | 1     # скорость пропорциональна (1 − u)
        if n > 2:
            k = np.zeros((n, n), np.float32)
            if dx:
                k[n//2, :] = 1.0/n
            else:
                k[:, n//2] = 1.0/n
            f = cv2.filter2D(f, -1, k, borderType=cv2.BORDER_REFLECT)
        return f
    if not moved:                                   # through на сцене на бумаге: влёт в центр кадра
        z = 1 + (THROUGH_ZOOM - 1)*g
        M = np.float32([[z, 0, W/2*(1 - z)], [0, z, H/2*(1 - z)]])
        f = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=PAPER)
    spread = THROUGH_BLUR*(1 - u)
    if spread > 0.004:
        import anim
        f = anim.zoom_blur(f, spread).astype(np.float32)
    return f


def mean_rgb(f):
    return [float(v) for v in np.asarray(f, np.float32).reshape(-1, 3).mean(0)]


def luma(rgb):
    return 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]

