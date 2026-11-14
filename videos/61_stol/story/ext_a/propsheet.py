"""Лист предметов common/props.py рилса 61 (проверка глазами): python3 propsheet.py → /tmp/a61a/props.png"""
import os
import subprocess
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "common")
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import props  # noqa: E402
from lib import blob, rect_pts, svg  # noqa: E402


def frame(t=0.4):
    b = blob(rect_pts(0, 0, 1080, 1920), "#EFE6D2")
    b += props.desk(540, 560, 1000, 1.0, 230, True, "wood", leg_h=140)
    b += props.paper_pile(300, 520, 1.0, 1) + props.mug(560, 500, 1.0, 0, "red", steam=1, t=t) + props.mug(660, 470, .9, 8, "blue", handle=-1)
    b += props.coffee_ring(760, 520, 1) + props.cable_tangle(850, 470, .9, 2, t, 0) + props.charger(960, 470, 1, 20)
    b += props.lamp_desk(150, 470, 1.0) + props.laptop_closed(560, 380, 1.0)
    b += props.fan_sheets(540, 900, .6, 1.0, 8, 3)
    b += props.idea_bulb(130, 1000, 1.2, 1, t) + props.idea_bulb(300, 1000, 1.2, .0, t)
    b += props.sticky(450, 1020, 1.2, -8, "yellow", 1, "lines") + props.sticky(560, 1020, 1.2, 6, "pink", 2, "star") + props.sticky(670, 1020, 1.2, 0, "blue", 3, "arrow")
    b += props.wall_sketch(850, 1000, 1.0, 4, 1, "house") + props.wall_sketch(990, 1180, .7, -6, 2, "spiral")
    b += props.checklist(130, 1300, 1.0, -4, 2, .6) + props.paper(330, 1300, 1, 6, kind="sketch", seed=4) + props.paper(500, 1300, 1, -5, kind="grid", seed=5)
    b += props.flying_sheet(680, 1280, 1, 20, 7, "lines", 1.0)
    b += props.tray(800, 1460, 1.0, 360) + props.apple(730, 1426, 1.2, 0, 0) + props.apple(820, 1426, 1.2, 0, 1) + props.chocolate(930, 1410, 1, -6)
    b += props.cup_plain(140, 1600, 1.2) + props.cup_spiky(320, 1600, 1.2)
    b += props.pencil(520, 1560, 1, -20) + props.marker(540, 1630, 1, 10) + props.marker(720, 1580, 1, -30, "#C8553D", True)
    b += props.thought_cloud(200, 1780, .8, 260, 170, 1, 1) + props.question_mark(480, 1780, 1, 1) + props.z_mark(600, 1760, 1)
    b += props.check_mark(700, 1780, 1.6, 1) + props.clink(860, 1760, 1, .4) + props.paper_ball(980, 1760, 1.5) + props.paper_stack(960, 1880, .8, 6, 2, .5)
    b += props.window(900, 760, 260, 300, "snow", t)
    return svg(b)


if __name__ == "__main__":
    os.makedirs("/tmp/a61a", exist_ok=True)
    open("/tmp/a61a/props.svg", "w").write(frame())
    open("/tmp/a61a/pl.txt", "w").write("/tmp/a61a/props.svg\t/tmp/a61a/props.png")
    subprocess.check_call(["node", os.path.join(COMMON, "render.js"), "/tmp/a61a/pl.txt", "png", "1", "x"])
