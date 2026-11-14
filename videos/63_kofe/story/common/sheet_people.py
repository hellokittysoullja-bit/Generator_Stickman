"""Контрольный лист героев рилса 63: python3 sheet_people.py [out] — Дима стоит, идёт, жонглирует, держит кружку за ручку; мимика; кот."""
import math
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
import people  # noqa: E402

R_JS = os.path.join(HERE, "render.js")
E = people.EXPR


def mug(cx, cy, k=1.0, side=1, col="#4a2c1c"):
    """Кружка-заглушка листа (настоящая — props.py группы A): корпус, ручка сбоку, кофе сверху."""
    w, h = 62 * k, 80 * k
    body = [(cx - w, cy - h), (cx + w, cy - h), (cx + w * .92, cy + h), (cx - w * .92, cy + h)]
    hx = cx + side * (w + 22 * k)
    handle = lib.ellipse_pts(hx, cy - 6 * k, 26 * k, 38 * k, 16)
    o = lib.shape(handle, "#e9e3d6", lib.blob(lib.ellipse_pts(hx, cy - 6 * k, 12 * k, 22 * k, 12), "#f4efe4"), w=4, seed=5)
    o += lib.shape(body, "#e9e3d6", lib.blob(lib.ellipse_pts(cx, cy - h, w * .9, 12 * k, 14), col), w=4.4, seed=6)
    return o, (hx, cy - 6 * k)


def held(fig, side, k, mside=1, col="#4a2c1c", far=False):
    w = fig["wrist"][side]
    cx = w[0] - mside * 70 * k
    back, front = people.handle_grip("dima", (w[0] - mside * 6 * k, w[1]), k=k, side=mside, far=far)
    m, _ = mug(cx, w[1] + 6 * k, k * 1.0, mside, col)
    return back + m + front


def build(page=0):
    lib.DEFS.clear()
    b = ['<rect width="1080" height="1920" fill="#f4efe4"/>']
    if page == 0:
        s = .6
        x, y = 270, 900
        f = people.figure("dima", x, y, s, E["dima"]["relief"], **people.stand_kw(x, y, s),
                          arms={"f": ("ik", (x + 200 * s, y - 260 * s), -1), "n": ("ik", (x + 260 * s, y - 200 * s), -1)},
                          hands={"f": {"kind": "none"}, "n": {"kind": "none"}})
        b.append(f["svg"] + held(f, "n", s, 1) + held(f, "f", s, 1, "#9fd0ee", True))
        x = 780
        wk = people.walk_kw(x, y, s, .2)
        f = people.figure("dima", wk["hip"][0], wk["hip"][1], s, E["dima"]["grimace_ok"], feet=wk["feet"],
                          arms={"f": ("ang", -1.9, .6), "n": ("ang", -2.4, .3)}, hands={"f": {"spread": .4, "curl": (.2, .2, .3, .3)},
                                                                                       "n": {"spread": .4, "curl": (.2, .2, .3, .3)}})
        b.append(f["svg"])
        for i, ph in enumerate((0, .25, .5, .75)):
            wk = people.walk_kw(140 + i * 270, 1560, .32, ph)
            b.append(people.figure("dima", wk["hip"][0], wk["hip"][1], .32, E["dima"]["doubt"], feet=wk["feet"])["svg"])
    elif page == 1:
        names = ["scared", "wince", "relief", "doubt", "surprise", "smug", "dull", "saucer", "zombie", "cheerful", "laugh", "grimace_ok",
                 "shrug", "friendly", "upset"]
        for i, n in enumerate(names):
            r, c = divmod(i, 5)
            b.append(people.figure("dima", 110 + c * 215, 420 + r * 520, 0.36, E["dima"][n], layers=("body",))["svg"])
    else:
        s = .62
        x, y = 330, 900
        f = people.figure("dima", x, y, s, E["dima"]["smug"], layers=("pelvis", "arm_f", "body", "arm_n"),
                          arms={"f": ("ik", (x + 190 * s, y - 210 * s), -1), "n": ("ik", (x + 250 * s, y - 330 * s), -1)},
                          hands={"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"kind": "none"}})
        b.append(f["svg"] + held(f, "n", s, 1))
        b.append(people.cat_svg(320, 1850, .55, {"blink": .3, "look": (.6, .3), "tail": -10}, 0.0))
        b.append(people.cat_svg(800, 1850, .55, {"blink": .0, "look": (-.6, 0), "turn": -.6, "tongue": 1.0}, 0.0))
        b.append(people.cat_walk(800, 1250, .5, .15))
    return lib.svg("".join(b))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/people63"
    d = tempfile.mkdtemp()
    lst = []
    for pg in (0, 1, 2):
        open(f"{d}/a{pg}.svg", "w").write(build(pg))
        lst.append(f"{d}/a{pg}.svg\t{out}_{pg}.png")
    open(d + "/l.txt", "w").write("\n".join(lst))
    subprocess.check_call(["node", R_JS, d + "/l.txt", "png", "1", "x"])
    print("\n".join(out + f"_{p}.png" for p in (0, 1, 2)))
