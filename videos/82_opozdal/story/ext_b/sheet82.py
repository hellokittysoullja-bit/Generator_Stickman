"""Лист людей рилса 82 (группа B): python3 sheet82.py OUT [страницы 0 1 2] — позы Димы, бег, учёные, горожане, кот."""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "common")
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import people as P  # noqa: E402


def build(page):
    lib.DEFS.clear()
    b = ['<rect width="1080" height="1920" fill="#f4efe4"/>']
    if page == 0:
        s = .3
        cells = [("run", 0.0), ("run", .25), ("run", .5), ("run", .75), ("walk", 0.0), ("walk", .5), ("temple", 1), ("onefoot", 0),
                 ("pose", "d82_shrug"), ("pose", "d82_hold"), ("pose", "d82_one"), ("pose", "d82_press")]
        for i, (kind, a) in enumerate(cells):
            r, c = divmod(i, 4)
            x, y = 150 + c * 260, 300 + r * 600
            if kind == "run":
                f = P.dima82_run(x, y, s, a, t=a)
            elif kind == "walk":
                f = P.dima82_walk(x, y, s, a, t=a)
            elif kind == "temple":
                f = P.dima82_temple(x, y, s, 1.0, feet="stand")
            elif kind == "onefoot":
                f = P.dima82_onefoot(x, y, s)
            else:
                f = P.dima82(x, y, s, "calm82", a, feet="stand", socks=("sock", "bare") if a == "d82_shrug" else None)
            b.append(f["svg"])
    elif page == 1:
        s = .3
        b.append(P.dima82(150, 300, s, "panic82", "d82_shrug", feet="stand", brush=True)["svg"])
        b.append(P.dima82(420, 300, s, "panic82", "d82_rest", feet="stand", inside_out=True)["svg"])
        b.append(P.dima82(690, 300, s, "panic82", "d82_rest", feet="stand", towel=True)["svg"])
        b.append(P.dima82_run(930, 300, s, .3, trip=1.0)["svg"])
        for i, kd in enumerate("abc"):
            b.append(P.scientist82(kd, 150 + i * 260, 900, s, "show", expr="talk")["svg"])
        b.append(P.subject82(930, 900, s, expr="wow")["svg"])
        for i, kd in enumerate(("student", "elder", "mom", "courier")):
            b.append(P.townsman82(kd, 150 + i * 260, 1500, s, "ribbon" if i % 2 == 0 else "rest")["svg"])
    else:
        b.append(P.cat_boot82(250, 600, .5, {"walk": .3}, t=.2))
        b.append(P.cat_bench82(750, 600, .5, t=.3, squint=1.0))
        b.append(P.boot82(250, 1100, .6, t=.4))
        b.append(P.sandwich82(700, 1050, 1.0))
        b.append(P.dima82(350, 1500, .5, "rush82", "d82_rest", sandwich=True, layers=("body",))["svg"])
        b.append(P.dima82(800, 1500, .5, "panic82", "d82_rest", brush=True, layers=("body",))["svg"])
    return lib.svg("".join(b))


if __name__ == "__main__":
    out = sys.argv[1]
    pages = [int(a) for a in sys.argv[2:]] or [0, 1, 2]
    d = tempfile.mkdtemp()
    lst = []
    for pg in pages:
        open(f"{d}/a{pg}.svg", "w").write(build(pg))
        lst.append(f"{d}/a{pg}.svg\t{out}_{pg}.png")
    open(d + "/l.txt", "w").write("\n".join(lst))
    subprocess.check_call(["node", os.path.join(COMMON, "render.js"), d + "/l.txt", "png", "1", "x"])
    print("\n".join(out + f"_{p}.png" for p in pages))
