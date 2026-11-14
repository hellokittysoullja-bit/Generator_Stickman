import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "common")
sys.path.insert(0, HERE); sys.path.insert(0, COMMON)
import lib, people, props
import base_d as D, s56 as S
from lib import *
def frame(sid, t):
    if not D._ST: D.static_all()
    lib.dyn_begin()
    d = D.dima(.08, {"n": ("ik", (700, 1130)), "f": ("ik", (680, 1140))}, {"n": D.fist(.4), "f": D.fist(.4)}, dict(lid=.8, look=(.8,0), brows="calm", mouth="flat"))
    body = D.world(t, d, dict(look=(-1,0)), (548,1185,1.2,0))
    return svg(f'<rect width="1920" height="1920" fill="#2a1f2a"/>{body}')
if __name__=="__main__":
    open("/tmp/a59a/t.svg","w").write(frame("s01",1.0))
