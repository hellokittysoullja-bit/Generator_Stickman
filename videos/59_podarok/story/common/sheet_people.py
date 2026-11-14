"""Контрольный лист героев рилса 59: python3 sheet_people.py [out.png] — все герои по пояс, в разных выражениях, кот, кисти."""
import os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib, people  # noqa: E402

R_JS = os.path.join(os.path.dirname(HERE), "ext_b", "render.js")


def build():
    lib.DEFS.clear()
    b = ['<rect width="1080" height="1920" fill="#f4efe4"/>']
    row = [("dima", {"mouth": "talk", "open": .5, "lid": .7, "brows": "worry", "look": (.5, 0)}),
           ("mama", {"mouth": "smile", "smile": 1, "lid": .6, "brows": "up", "laugh": .85, "tears": .8}),
           ("girl", {"mouth": "grin", "lid": .8, "brows": "up", "look": (.4, 0)})]
    row2 = [("bald", {"mouth": "talk", "open": .4, "lid": .7, "brows": "calm"}),
            ("cap", {"mouth": "grin", "lid": .7, "brows": "up"}),
            ("dima", {"mouth": "grin", "laugh": .9, "lid": .6, "brows": "up"})]
    for r, (y, rr) in enumerate(((560, row), (1160, row2))):
        for i, (w, e) in enumerate(rr):
            f = people.figure(w, 190 + i * 350, y, 0.5, e, head_ang=0.0)
            b.append(f["svg"])
    b.append(people.cat_svg(540, 1860, 0.55, {"smile": 1}, 0.4))
    h = people.hand_svg("dima", (120, 1700), (1, 0), .8, curl=(.7, .7, .7, .7), thumb=.7)
    b.append(h)
    return lib.svg("".join(b))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/people_sheet.png"
    d = tempfile.mkdtemp()
    open(d + "/a.svg", "w").write(build())
    open(d + "/l.txt", "w").write(f"{d}/a.svg\t{out}")
    subprocess.check_call(["node", R_JS, d + "/l.txt", "png", "1", "x"])
    print(out)
