"""Лист предметов раздела КОФЕ (common/props.py) для проверки глазами: python3 propsheet.py out.svg"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "common"))
import lib  # noqa: E402
import props as P  # noqa: E402

t = 0.7
b = ['<rect width="1080" height="1920" fill="#F4ECD8"/>']
b.append(P.coffee_mug(140, 300, 1.2, steam=1, t=t))
b.append(P.coffee_mug(330, 300, 1.2, fill=0, col="red"))
b.append(P.coffee_mug(520, 300, 1.2, upside=True, col="blue"))
b.append(P.glass(700, 300, 1.2, fill=.5, t=t, splash=.4))
b.append(P.glass(880, 300, 1.2, fill=1))
b.append(P.tea_cup(160, 560, 1.3, steam=1, t=t))
b.append(P.milk_saucer(440, 560, 1.0, t=t, ripple=1, lick=.5))
b.append(P.coffee_pot(680, 600, 1.0))
sx, sy = P.pot_spout(680, 600, 1.0)
b.append(P.pour_stream(sx, sy, sx + 150, 760, t))
b.append(P.jug(940, 640, .9))
lw = P.mug_cut(0, 0, 1.0, glow=.8, wave=1, t=t)
b.append(P.scales(300, 1180, 1.0, 10, left=lw, right=P.drop(0, -20, 1.4)))
b.append(P.clock(800, 900, 100, *P.clock_hm(1, 10)))
b.append(P.table_lamp(760, 1220, 1.0))
b.append(P.red_marker(200, 1320, 1.2, -30))
b.append(P.cross_stroke((300, 1260), (700, 1460), (700, 1260), (300, 1460), .8))
b.append(P.crack(100, 1560, 1.0, 0, 1))
b.append(P.evap(500, 1600, 1.0, 1, t))
b.append(P.zzz(620, 1620, 1.0, t))
b.append(P.gloom(880, 1600, 1.0, t))
b.append(P.dash_arrow([(80, 1750), (300, 1700), (500, 1760)], 1))
b.append(P.heart(700, 1780, 1.0, .4))
b.append(P.sweat(900, 1780, 1.5))
open(sys.argv[1], "w").write(lib.svg("".join(b)))
