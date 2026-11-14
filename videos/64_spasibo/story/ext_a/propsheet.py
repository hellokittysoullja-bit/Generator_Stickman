"""Лист предметов раздела СПАСИБО (common/props.py) для проверки глазами: python3 propsheet.py out.svg [t]"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "common"))
import lib  # noqa: E402
import props as P  # noqa: E402

t = float(sys.argv[2]) if len(sys.argv) > 2 else 0.7
b = ['<rect width="1080" height="1920" fill="#F4ECD8"/>']
b.append(P.card(130, 190, 1.0))
b.append(P.card(330, 190, 1.0, open=.3))
b.append(P.card(520, 190, 1.0, open=.7))
b.append(P.card(830, 190, 1.0, open=1, inside="lines", write=.6))
b.append(P.letter(130, 520, .9, write=.55))
b.append(P.letter(340, 520, .9, write=1, fold=.4))
b.append(P.letter(540, 520, .9, write=1, fold=1))
tx, ty = P.letter_tip(130, 520, .9, write=.55)
b.append(P.pen(tx + 60, ty - 40, 1.0, -35, cap=1) + P.click(700, 420, 1, .4))
b.append(P.pen(780, 560, 1.0, 20) + P.pen(900, 560, 1.0, 0, cap=.5))
ph = P.memory_bubble(0, 0, 1, 1, 0)  # пусто
photo = P.house(0, 50, .45, 1) + P.sun(50, -30, 18, 1)
b.append(P.photo_frame(140, 820, 1.0, 0, 1, photo) + P.photo_frame(370, 820, 1.0, 0, .4, photo) + P.photo_frame(600, 820, 1.0, 0, 0))
b.append(P.drawer(880, 800, 300, 100, 1, inner=P.card(0, 0, .5, 80)))
b.append(P.handset(80, 1000, 1.0, 10))
b.append(P.gloom(240, 1080, 1.0, t) + P.gloom_burst(440, 1080, 1.0, .35))
b.append(P.sun(640, 1010, 60, .6, t) + P.house(840, 1110, .7, .3) + P.tree(990, 1110, .6, 1, t))
b.append(P.speech_bubble(150, 1230, 220, 140, 1.0))
b.append(P.chest_glow(380, 1300, 1.0, t, 1, .5) + P.heart_stroke(520, 1250, 1, .8) + P.sparkles(660, 1250, 1, 1, t) + P.purr(820, 1280, 1, t))
b.append(P.calendar(260, 1640, 380, 420, stamps=17.4, glow=.6))
b.append(P.bookshelf(640, 1880, 300, 420, 4))
b.append(P.memory_bubble(900, 1500, 240, 180, 1, inner=P.sun(0, 0, 30, 1), head=(900, 1800), thread=1, pale=.7))
b.append(P.memory_bubble(900, 1730, 200, 150, 1, inner=P.heart(0, 0, .5), warm=1))
b.append(P.sun_stamp(980, 1880, 26))
s, _ = P.day_arc(540, 1900, 200, 1.4)
b.append(s)
open(sys.argv[1], "w").write(lib.svg("".join(b)))
