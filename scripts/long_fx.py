#!/usr/bin/env python3
"""Эффекты удержания длинного ролика поверх кадра (28.10, по образцу, который прислал владелец):
кот-ведущий выходит к зрителю перед размытой сценой и жирный текст, вылетающий под голос.

Решения владельца 28.10: размытие — только когда кот обращается к зрителю; рукописный карандаш остаётся как был, а
жирный текст — шрифт субтитров рилсов (Onest Black), белый со слабой чёрной обводкой, вылетает (по буквам и другими
эффектами). Как выглядит — на согласование владельцу до встраивания в ролик."""
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw

W, H = 1920, 1080
FONT_AXES = {"Weight": 900}
STROKE = 3                 # слабая обводка: тонкая и полупрозрачная, не наклейка
STROKE_ALPHA = 0.55
SHADOW = (0, 5, 9, 0.55)   # dx, dy, blur, alpha: мягкая тень под буквами
GLOW = (14, 0.38)          # размытие и сила тёмного ореола: белое на кремовой бумаге без него не читается (пробник 28.10)


def _font(size):
    import reel
    return reel.font(reel.CAP_FONT, size, FONT_AXES, raqm=True)


def back_out(u, s=1.7):
    """Перелёт к 1 с отскоком (как поп слов в субтитрах рилсов)."""
    u = min(max(u, 0.0), 1.0) - 1
    return 1 + u*u*((s + 1)*u + s)


def ease_out(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u)**3


# --------------------------------------------------------------------------- размытие под ведущим

def focus_blur(f, t, t0, t1, sigma=14, dark=0.12, ramp=0.3):
    """Сцена уходит в расфокус (и чуть темнеет), пока кот говорит со зрителем, потом возвращается."""
    k = ease_out((t - t0)/ramp) * (1 - ease_out((t - (t1 - ramp))/ramp))
    if k <= 0.01:
        return f
    b = cv2.GaussianBlur(np.ascontiguousarray(f, np.float32), (0, 0), sigma*k + 0.1)
    return b*(1 - dark*k)


# --------------------------------------------------------------------------- кот-ведущий

class Narrator:
    """Кукла кота во весь рост перед сценой: выпрыгивает снизу с перелётом, моргает, смотрит на зрителя, уходит."""

    def __init__(self, dur, cx=0.72, height=0.78, seed=3, words=None, text=""):
        import mascot_live as M
        self.M, self.R = M, M.rig()
        acts = M.plan_actions(dur, words or [], text, [0.0, 0.0], seed=seed)
        self.state = M._mod().plan(dur, acts, seed=seed)
        self.dur, self.cx, self.height = dur, cx, height

    def composite(self, f, t, pop=0.32, out=0.22):
        st = self.state(t)
        rgba = self.R.frame_rgba(st, t)
        x0, y0, x1, y1 = self.R.bb_for(st)
        sub = np.ascontiguousarray(rgba[y0:y1, x0:x1])
        s_in = back_out(t/pop) if t < pop else 1.0
        s_out = 1 - ease_out((t - (self.dur - out))/out) if t > self.dur - out else 1.0
        s = max(0.02, s_in*s_out)
        k = self.height*H/sub.shape[0]*s
        nw, nh = max(1, int(sub.shape[1]*k)), max(1, int(sub.shape[0]*k))
        small = cv2.resize(sub, (nw, nh), interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_LINEAR)
        base_y = H + 6                                 # лапы у нижнего края кадра
        x, y = int(self.cx*W - nw/2), int(base_y - nh)
        out_ = f.copy()
        xa, ya, xb, yb = max(0, x), max(0, y), min(W, x + nw), min(H, y + nh)
        if xb <= xa or yb <= ya:
            return out_
        piece = small[ya - y:yb - y, xa - x:xb - x]
        a = np.clip(piece[..., 3:4], 0, 1)
        # мягкая тень за котом — он стоит перед сценой, а не вклеен
        sh = cv2.GaussianBlur(a[..., 0], (0, 0), 18)[..., None]*0.28
        region = out_[ya:yb, xa:xb]
        region *= 1 - sh
        out_[ya:yb, xa:xb] = region*(1 - a) + np.clip(piece[..., :3], 0, 255)
        return out_


# --------------------------------------------------------------------------- жирный текст

def _glyphs(text, size):
    """[(символ, x, ширина)] строки и её габариты."""
    f = _font(size)
    xs, x = [], 0.0
    for ch in text:
        w = f.getlength(ch)
        xs.append((ch, x, w))
        x += w
    asc, desc = f.getmetrics()
    return f, xs, x, asc + desc


def _glyph_rgba(ch, f, size):
    pad = STROKE + 14
    w = int(f.getlength(ch)) + 2*pad
    h = size + 2*pad
    im = Image.new("L", (w, h), 0)
    st = Image.new("L", (w, h), 0)
    ImageDraw.Draw(st).text((pad, pad), ch, font=f, fill=255, stroke_width=STROKE, stroke_fill=255)
    ImageDraw.Draw(im).text((pad, pad), ch, font=f, fill=255)
    fill = np.asarray(im, np.float32)/255
    stroke = np.asarray(st, np.float32)/255
    a = np.maximum(fill, stroke*STROKE_ALPHA)
    rgb = np.repeat((fill/np.maximum(a, 1e-4))[..., None]*255, 3, axis=2)     # белое внутри, тёмная обводка
    return np.dstack([rgb*a[..., None], a]), pad


def _paste(f, rgba, cx, cy, scale=1.0, rot=0.0, alpha=1.0, blur_x=0):
    h, w = rgba.shape[:2]
    M = cv2.getRotationMatrix2D((w/2, h/2), rot, scale)
    M[0, 2] += cx - w/2
    M[1, 2] += cy - h/2
    warped = cv2.warpAffine(rgba, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
    if blur_x > 1:
        n = int(blur_x) | 1
        warped = cv2.filter2D(warped, -1, np.ones((1, n), np.float32)/n)
    a = warped[..., 3:4]*alpha
    dx, dy, sb, sa = SHADOW
    sh = cv2.GaussianBlur(np.roll(np.roll(a, dy, 0), dx, 1)[..., 0], (0, 0), sb)[..., None]*sa
    gb, ga = GLOW
    glow = cv2.GaussianBlur(cv2.dilate(a[..., 0], np.ones((9, 9), np.float32)), (0, 0), gb)[..., None]*ga
    f = f*(1 - np.clip(sh + glow, 0, 0.8))
    return f*(1 - a) + warped[..., :3]*alpha


class BoldText:
    """Жирная строка, вылетающая под голос. style: letters — по буквам с отскоком (как в образце); slam — слово
    целиком влетает крупным и встаёт с тряской; rise — слова поднимаются снизу по очереди."""

    def __init__(self, text, cx, cy, size=120, style="letters", t0=0.0, per=0.05, word_times=None):
        self.f, self.xs, self.width, self.h = _glyphs(text, size)
        self.text, self.cx, self.cy, self.size, self.style, self.t0, self.per = text, cx, cy, size, style, t0, per
        self.cache = {}
        self.word_times = word_times

    def _g(self, ch):
        if ch not in self.cache:
            self.cache[ch] = _glyph_rgba(ch, self.f, self.size)
        return self.cache[ch]

    def composite(self, f, t, t_end=None):
        if t < self.t0:
            return f
        fade = 1.0
        if t_end is not None and t > t_end - 0.18:
            fade = max(0.0, (t_end - t)/0.18)
        left = self.cx - self.width/2
        u0 = t - self.t0
        if self.style == "slam":
            u = min(1.0, u0/0.22)
            sc = 1.9 - 0.9*ease_out(u)
            shake = 0.0 if u0 < 0.22 else 7*math.exp(-(u0 - 0.22)/0.08)*math.sin(2*math.pi*16*(u0 - 0.22))
            for ch, x, w in self.xs:
                if ch == " ":
                    continue
                g, pad = self._g(ch)
                gx = self.cx + (left + x + w/2 - self.cx)*sc
                f = _paste(f, g, gx + shake, self.cy, scale=sc, alpha=min(1.0, u*3)*fade, blur_x=(1 - u)*40)
            return f
        if self.style == "rise":
            words, cur, wi = [], [], 0
            for i, (ch, x, w) in enumerate(self.xs):
                if ch == " ":
                    wi += 1
                    continue
                d = u0 - wi*0.16
                if d <= 0:
                    continue
                u = min(1.0, d/0.28)
                g, pad = self._g(ch)
                f = _paste(f, g, left + x + w/2, self.cy + 70*(1 - ease_out(u)), alpha=ease_out(u)*fade)
            return f
        # letters: каждая буква выпрыгивает из маленькой с отскоком и лёгким поворотом (как в образце)
        for i, (ch, x, w) in enumerate(self.xs):
            if ch == " ":
                continue
            d = u0 - i*self.per
            if d <= 0:
                continue
            u = min(1.0, d/0.18)
            g, pad = self._g(ch)
            rot = (8 if i % 2 else -8)*(1 - u)
            f = _paste(f, g, left + x + w/2, self.cy + 18*(1 - u), scale=max(0.05, back_out(u)), rot=rot, alpha=fade)
        return f
