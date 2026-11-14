"""Контрольный лист героев рилса 62: python3 sheet_people.py [out] — Дима в лотосе (позы и мимика), друг с мобильником, кот."""
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


def lotus(name, x, y, s, ex, u=0.0, **kw):
    return people.figure("dima", x, y, s, E["dima"][ex], **people.lotus_kw(name, x, y, s, u, **kw))["svg"]


def build(page=0):
    lib.DEFS.clear()
    b = ['<rect width="1080" height="1920" fill="#f4efe4"/>']
    if page == 0:
        b.append(lotus("sit", 300, 700, .62, "solemn"))
        b.append(lotus("sit", 800, 700, .62, "bliss"))
        b.append(lotus("slump", 300, 1500, .62, "upset", sag=1.0))
        b.append(lotus("push", 800, 1500, .62, "soft", u=1.0))
    elif page == 1:
        for i, n in enumerate(("smack", "one_eye", "squeeze", "upset", "side_eye")):
            b.append(people.figure("dima", 110 + i * 215, 420, 0.36, E["dima"][n], layers=("body",))["svg"])
        for i, n in enumerate(("soft", "friendly", "side_smile", "solemn", "bliss")):
            b.append(people.figure("dima", 110 + i * 215, 900, 0.36, E["dima"][n], layers=("body",))["svg"])
        b.append(lotus("flick", 280, 1650, .5, "soft", u=.3))
        b.append(lotus("wave", 780, 1650, .5, "friendly", u=.25))
    else:
        # друг: стоит, держит мобильник, топает
        x, y, s = 300, 1000, .5
        f = people.figure("pal", x, y, s, E["pal"]["hurt"], feet={"n": (x + 60, y + 600 * s), "f": (x - 40, y + 610 * s)} and
                          {"n": ((x + 60, y + 600 * s), 0.0), "f": ((x - 50, y + 610 * s), 0.0)},
                          arms={"f": ("ang", 0.2, 0.2), "n": ("ik", (x + 230 * s, y - 330 * s), -1)}, hands={"n": {"kind": "none"}})
        b.append(f["svg"])
        w = f["wrist"]["n"]
        b.append(people.mobilnik(w[0] + 20, w[1] - 40, .9, 12))
        bk, fr = people.grip_svg("pal", (w[0] + 20, w[1] - 30), 30 * .9, 1, k=s * 1.03)
        b.append(fr)
        b.append(people.figure("pal", 800, 600, .42, E["pal"]["cross"], layers=("body",))["svg"])
        b.append(people.cat_walk(780, 1300, .55, 0.12))
        b.append(people.cat_svg(320, 1850, .55, {"blink": .55, "look": (.6, .3), "tail": -10}, 0.0))
        b.append(people.cat_svg(800, 1850, .55, {"blink": .0, "look": (-.6, 0), "turn": -.6}, 0.0))
    return lib.svg("".join(b))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/people62"
    d = tempfile.mkdtemp()
    lst = []
    for pg in (0, 1, 2):
        open(f"{d}/a{pg}.svg", "w").write(build(pg))
        lst.append(f"{d}/a{pg}.svg\t{out}_{pg}.png")
    open(d + "/l.txt", "w").write("\n".join(lst))
    subprocess.check_call(["node", R_JS, d + "/l.txt", "png", "1", "x"])
    print("\n".join(out + f"_{p}.png" for p in (0, 1, 2)))
