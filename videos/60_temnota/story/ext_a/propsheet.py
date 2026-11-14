import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import lib, props
from lib import svg, blob, rect_pts
def frame():
    b = blob(rect_pts(0, 0, 1080, 1920), "#20254A")
    b += blob(rect_pts(0, 1500, 1080, 1920), "#171A36")
    k = 1.4
    b += props.book_open(200, 220, k) + props.book_open(520, 220, k, flip=.4) + props.book_back(840, 220, k)
    b += props.book_closed(200, 380, k) + props.flashlight(520, 360, k, 0, 1) + props.flashlight(840, 360, k, 0, 0)
    b += props.beam(580, 360, 0, 380, 20, 1, k)
    b += props.lamp_desk(150, 640, 1.2) + props.lamp_floor(420, 700, .8) + props.wall_switch(600, 580, 1.5, 1) + props.pillow(840, 640, 1.2)
    b += props.glow(150, 520, 200)
    b += props.blanket(240, 980, 1, 360, 170) + props.blanket(700, 980, 1, 360, 170, 2, "blue")+ props.blanket(960, 980, .5, 360, 170, 3, "green")
    b += props.bed(300, 1250, .9) 
    b += props.window(800, 1380, 360, 420, "night", 0.3, far=True)
    b += props.moon(900, 1450, 30)
    return svg(b)
if __name__ == "__main__":
    open("/tmp/a60a/props.svg", "w").write(frame())
    subprocess.check_call(["node", os.path.join(HERE, "render.js"), "/tmp/a60a/pl.txt", "png", "1", "x"]) if False else None
