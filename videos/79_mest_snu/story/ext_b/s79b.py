"""Рилс 79 «Месть сну», группа B: люди, кот, призыв. Время — только из shots.json и voice/words.json (слово по индексу wN).
s05: призыв «Телеграм» модулем scripts/story_cta_tg.py: PRESS = W[20].start + 0.12 («Телеграм»), T0 = PRESS − 1.10.
s07: мансарда снизу на люк, кот на изголовье: «смотри» (w30) к зрителю, «куда» (w31) звёзды стекают в свет экрана, «ночь» (w33) люк пуст.
s09: офис, «работы» (w39) шлёпается стопка папок, «других» (w42) люди с просьбами, Дима кивает и берёт.
s12: Дима обнимает тёплый сектор, «время» (w53) луна тянет луч, «сна» (w55) прижимает, «так» (w57) улыбка, кот вздыхает.
s15: тёплый вечер, «теперь» (w68) телефон в ящик, «берёт» (w70) гитару со стены, сдувает пыль, «себе» (w71) прижимает.
s16: играет на коврике, «полчаса» (w72) аккорд, «вечером» (w73) кот в такт, «ещё» (w74) глаза закрыты.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(STORY)))
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import lib  # noqa: E402
import people  # noqa: E402
import props as P  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, svg  # noqa: E402,F401

INK = lib.INK
W = json.load(open(os.path.join(STORY, "voice", "words.json")))
W = W if isinstance(W, list) else W["words"]
SH = {s["id"]: s for s in json.load(open(os.path.join(STORY, "shots.json")))["shots"]}


def ws(i):
    return W[i]["start"]


def we(i):
    return W[i]["end"]


def lerp(a, b, u):
    return a + (b - a) * u


# ═══════════════════════════════ s05: призыв «Телеграм» ═══════════════════════════════
def s05(t):
    import story_cta_tg as tg
    press = ws(20) + 0.12
    return tg.frame(t, t0=press - 1.10, press=press, common=COMMON)


def frame(sid, t):
    return globals()[sid](t)
