"""Контрольный лист героев рилса 60: python3 sheet_people.py [out.png] — взрослый Дима, маленький Дима (стойка, мимика), мама, кот, кисти."""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
import people  # noqa: E402

R_JS = os.path.join(HERE, "render.js")


def _legs(x, y, k, kid=False):
    lk = people.KID_LEG_K if kid else 1.0
    a = (x + 60 * k, y + 598 * k * lk)
    b = (x - 50 * k, y + 598 * k * lk)
    return {"n": (a, 0.0), "f": (b, 0.0)}


def build():
    lib.DEFS.clear()
    b = ['<rect width="1080" height="1920" fill="#f4efe4"/>']
    # ряд 1: взрослый Дима (стойка), мама (стойка), маленький Дима (стойка)
    f = people.figure("dima", 190, 420, 0.42, {"mouth": "talk", "open": .4, "lid": .7, "brows": "calm"}, feet=_legs(190, 420, .42))
    b.append(f["svg"])
    f = people.figure("mama", 540, 420, 0.42, {"mouth": "smile", "smile": .8, "lid": .7, "brows": "calm"}, feet=_legs(540, 420, .42))
    b.append(f["svg"])
    f = people.figure("kid", 880, 560, 0.5, {"mouth": "grin", "lid": .9, "brows": "up"}, feet=_legs(880, 560, .5 * .66, True))
    b.append(f["svg"])
    # ряд 2: лица маленького Димы: азарт, зевота, боль, красные глаза
    ex = [{"mouth": "grin", "lid": .95, "brows": "up", "look": (.5, .3)},
          {"mouth": "yawn", "open": .9, "lid": .35, "brows": "sleepy", "redeye": .6},
          {"mouth": "wince", "lid": .3, "brows": "worry", "closed": .6, "redeye": 1.0},
          {"mouth": "smile", "smile": 1, "lid": .55, "brows": "calm"}]
    for i, e in enumerate(ex):
        f = people.figure("kid", 130 + i * 270, 1180, 0.55, e)
        b.append(f["svg"])
    # ряд 3: мама строгая/улыбка, Дима взрослый усталый, кот, кисти
    b.append(people.figure("mama", 150, 1650, 0.45, {"mouth": "talk", "open": .5, "lid": .8, "brows": "frown"})["svg"])
    b.append(people.figure("mama", 420, 1650, 0.45, {"mouth": "smile", "smile": 1, "lid": .6, "brows": "up"})["svg"])
    b.append(people.figure("dima", 690, 1650, 0.45, {"mouth": "flat", "lid": .45, "brows": "tired"})["svg"])
    b.append(people.cat_svg(940, 1830, 0.45, {"smile": 1}, 0.4))
    return lib.svg("".join(b))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/people_sheet.png"
    d = tempfile.mkdtemp()
    open(d + "/a.svg", "w").write(build())
    open(d + "/l.txt", "w").write(f"{d}/a.svg\t{out}")
    subprocess.check_call(["node", R_JS, d + "/l.txt", "png", "1", "x"])
    print(out)
