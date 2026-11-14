"""Контрольный лист героев рилса 61: python3 sheet_people.py [out.png] — Дима (мимика и позы), мама, участница (bob), бородач (beard), кот."""
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


def build(page=0):
    lib.DEFS.clear()
    b = ['<rect width="1080" height="1920" fill="#f4efe4"/>']
    if page == 0:
        # ряд 1: пять лиц Димы
        for i, n in enumerate(("guilty", "gloom", "zeal", "focus", "calm_smile")):
            b.append(people.figure("dima", 110 + i * 215, 420, 0.36, E["dima"][n])["svg"])
        # ряд 2: позы Димы
        for i, n in enumerate(("sit_desk", "slump", "draw")):
            x, y = 150 + i * 340, 1050
            b.append(f'<rect x="{x - 60}" y="{y - 0.4 * 200}" width="330" height="14" fill="#a07a52"/>')
            b.append(people.figure("dima", x, y, 0.4, E["dima"][["guilty", "gloom", "focus"][i]], **people.pose_kw(n, x, y, 0.4))["svg"])
        # ряд 3: tick, arms_wide; мама sweep/cross
        x, y = 150, 1700
        b.append(people.figure("dima", x, y, 0.4, E["dima"]["focus"], **people.pose_kw("tick", x, y, 0.4))["svg"])
        x = 470
        b.append(people.figure("dima", x, y, 0.4, E["dima"]["calm_smile"], **people.pose_kw("arms_wide", x, y, 0.4))["svg"])
        b.append(people.figure("mama", 760, y, 0.4, E["mama"]["talk"], **people.pose_kw("sweep", 760, y, 0.4, "mama"))["svg"])
        b.append(people.figure("mama", 980, y, 0.4, E["mama"]["pursed"], **people.pose_kw("cross", 980, y, 0.4, "mama"))["svg"])
    else:
        # ряд 1: мама — 4 лица
        for i, n in enumerate(("brow_up", "pursed", "talk", "sigh")):
            b.append(people.figure("mama", 140 + i * 265, 430, 0.42, E["mama"][n])["svg"])
        # ряд 2: участница — 4 лица
        for i, n in enumerate(("calm", "think", "bite", "pleased")):
            b.append(people.figure("bob", 140 + i * 265, 960, 0.42, E["bob"][n])["svg"])
        # ряд 3: бородач — 3 лица, кот сидит/шаг
        for i, n in enumerate(("think", "idea", "calm")):
            b.append(people.figure("beard", 130 + i * 250, 1480, 0.4, E["beard"][n])["svg"])
        b.append(people.cat_walk(900, 1380, 0.32, 0.12))
        # ряд 4: кот прыгает (присед, толчок, полёт), кот спит
        for i, u in enumerate((0.25, 0.38, 0.6)):
            b.append(people.cat_jump((140 + i * 250, 1880), (300 + i * 250, 1780), 0.3, u, 0.3))
        b.append(people.cat_svg(900, 1880, 0.32, {"sleep": 1.0, "blink": 1.0}, 0.5))
    return lib.svg("".join(b))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/people_sheet"
    d = tempfile.mkdtemp()
    lst = []
    for pg in (0, 1):
        open(f"{d}/a{pg}.svg", "w").write(build(pg))
        lst.append(f"{d}/a{pg}.svg\t{out}_{pg}.png")
    open(d + "/l.txt", "w").write("\n".join(lst))
    subprocess.check_call(["node", R_JS, d + "/l.txt", "png", "1", "x"])
    print(out)
