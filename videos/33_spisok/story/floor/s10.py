"""s10 (14.24–15.72, клип 14.04–15.92): вечер, пол комнаты Димы, свиток раскатан по полу от стола к зрителю; кот спит
на нём калачиком (огонёк притушен), бока дышат; на «спит» (14.56) над ним поднимаются Z-Z-Z. Медленный наезд."""
import math

import numpy as np

import cat_curl
import lib
import ribbon
from floorbg import Room
from lib import blob, clamp, ease_io

T_A, T_B = 14.04, 15.92
T_SPIT = 14.56
FY, DT, DZ = 60.0, -15.0, 200.0
X_P, W_P = 2.0, 30.0
CAT_Z = 108.0


def strip():
    pts = [np.array([X_P, DT - .5, DZ - 3]), np.array([X_P, DT - .2, DZ - .3])]
    n = 80
    for i in range(1, n + 1):
        u = i / n
        Y = DT + (FY - .2 - DT) * u
        Z = DZ - .3 + 2.5 * math.sin(math.pi * u) - 4 * u ** 3
        pts.append(np.array([X_P, Y, Z]))
    z0 = pts[-1][2]
    zz = z0
    while zz > 66:
        zz -= .8
        lift = 2.2 * max(0.0, math.sin((z0 - zz) * .11 - .6)) ** 2 * (zz > 130)
        pts.append(np.array([X_P + 2.0 * math.sin(zz * .045), FY - .2 - lift, zz]))
    return np.array(pts)


def frame(t):
    lib.DEFS.clear()
    u = clamp((t - T_A) / (T_B - T_A))
    z = 1.28 + 0.12 * (0.4 * u + 0.6 * ease_io(u))
    cam = ribbon.Cam(f=1100, cx=540, cy=470)
    room = Room(cam, floor_y=FY, desk_top=DT, desk_z=DZ, desk_x=(-60.0, 140.0), ped_x=70.0, mode="evening")
    bg = [room.wall(t), room.window(t, X0=-120, X1=-58, Y0=-150, Y1=-50), room.floor(z_near=20), room.desk(t)]
    P = ribbon.resample(strip(), .5)
    items = ribbon.pieces(cam, P, W_P, seed=7100, s_offset=0)
    roll_C = np.array([X_P, FY - 4.2, 64.0])
    items.append((float(np.linalg.norm(roll_C)) - 4.5, ribbon.roll(cam, roll_C, 4.2, W_P, 0.6, seed=7600, cap_side=-1)))
    items.sort(key=lambda q: -q[0])
    k = cam.k(CAT_Z)
    s = k * 46 / 430
    x, y = cam.p((X_P - 1, FY - .3, CAT_Z))
    cat = cat_curl.draw(x, y, s, t)
    hx, hy = cat_curl.head_top(x, y, s, t)
    zz = cat_curl.zzz(hx, hy, s * 1.3, t, T_SPIT)
    world = "".join(bg) + "".join(q[1] for q in items) + cat + room.light(t) + zz
    return lib.svg(f'<g transform="translate(540 930) scale({z:.4f}) translate(-540 -960)">{world}</g>')


_ = blob
