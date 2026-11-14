"""Лист предметов common/props.py рилса 62 (проверка глазами): python3 propsheet.py OUTDIR → OUTDIR/props.png"""
import os
import subprocess
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "common")
sys.path.insert(0, COMMON)
import props  # noqa: E402
from lib import blob, rect_pts, svg  # noqa: E402


def frame(t=0.4):
    b = blob(rect_pts(0, 0, 1080, 1920), "#EFE6D2")
    b += props.torch(130, 520, 1.0, 1, "#EFE6D2")
    sx, sy = props.pop(1.08, 1.0)
    b += props.cloud(420, 330, 300, 190, sx, sy, 1, dots=(-70, 130))
    b += props.cloud(800, 330, 300, 190, 1, 1, 2, dots=(60, 130), inner=props.plate_soup(0, 60, .7, 1, t))
    b += props.storm(560, 700, 560, 250, 1, 1, 3, flash=0) + props.bolt(470, 690, 560, 1000, .6)
    b += props.rain(760, 690, 200, 1.0, .5, 5, 1, floor=1000)
    b += props.hourglass(150, 860, 1.0, 0, 1, .55, t) + props.hourglass(330, 900, .8, 30, 0, .2, t)
    b += props.plate_soup(150, 1180, 1.0, 1, t) + props.cutlet_fork(400, 1110, 1.0, -15)
    b += props.ironing_board(780, 1110, .9, 520) + props.iron(760, 1092, .9, 0, 1, t)
    b += props.mobilnik(560, 1160, 1.0, 10) + props.sweat(620, 1060) + props.drop(660, 1060)
    b += props.mat(300, 1500, .7, 500) + props.cushion(300, 1500, .9, 1.0)
    b += props.cushion(700, 1500, .9, .6)
    b += props.balloon(150, 1700, 1, "red", t, string=120) + props.balloon(300, 1700, 1, "blue", t, 1, string=120)
    b += props.att_flame(470, 1780, 1.2, t, 1, halo=.5) + props.mote(560, 1720, 7, 1)
    b += props.breath_wave(620, 1040, 1720, 26, t) + props.dash_path([(620, 1850), (800, 1800), (1040, 1860)], .8)
    b += props.legs_run(920, 1560, 1, t)
    return svg(b)


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    open(f"{out}/props.svg", "w").write(frame())
    open(f"{out}/pl.txt", "w").write(f"{out}/props.svg\t{out}/props.png")
    subprocess.check_call(["node", os.path.join(COMMON, "render.js"), f"{out}/pl.txt", "png", "1", "x"])
