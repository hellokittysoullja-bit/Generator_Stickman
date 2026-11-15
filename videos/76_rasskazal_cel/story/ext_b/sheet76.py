"""Контрольный лист поз рилса 76 (группа B): python3 sheet76.py OUT [страницы] — Дима в пижаме и в худи, толпа, кухня, студенты, кот."""
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
    s = .34
    if page == 0:       # Дима в пижаме на матрасе
        cells = [("chips76", "chew76", "mat"), ("chew76", "bored76", "mat"), ("shrug76", "shrug76", "mat"), ("spread76", "brow76", "mat"),
                 ("pinned76", "pinned76", "mat"), ("boast76", "boast76", "sit"), ("horn76", "blow76", "sit"), ("shh76", "puffed76", "sit"),
                 ("laptop_lap76", "laugh76", "sit")]
        for i, (pz, ex, leg) in enumerate(cells):
            r, c = divmod(i, 3)
            x, y = 120 + c * 340, 520 + r * 560
            kw = P.mattress_kw(x, y, s) if leg == "mat" else P.sit_mat_kw(x, y, s)
            if pz == "shh76":
                f = P.dima_pj(x, y, s, ex, pz, arms={"n": ("ik", P.lips76(x, y, s, 0.02, 0.0, "dima_pj"), -1)}, **kw)
            else:
                f = P.dima_pj(x, y, s, ex, pz, **kw)
            b.append(f["svg"])
            m = P.mouth_pt(f, P.POSE[pz][0], P.POSE[pz][1])
            b.append(f'<circle cx="{m[0]:.0f}" cy="{m[1]:.0f}" r="5" fill="red"/>')
    elif page == 1:     # Дима в худи стоя + встаёт + толпа
        for i, (pz, ex) in enumerate((("tell76", "tell76"), ("point_up76", "dream76"), ("trophy_up76", "beam76"), ("shh76", "shh76"))):
            x, y = 140 + i * 260, 900
            kw = P.stand_kw(x, y, s)
            if pz == "shh76":
                f = P.dima(x, y, s, ex, pz, arms={"n": ("ik", P.lips76(x, y, s), -1)}, **kw)
            elif pz == "tell76":
                f = P.dima(x, y, s, ex, pz, arms=P.rect_hands(.5, x, y, s), **kw)
            else:
                f = P.dima(x, y, s, ex, pz, **kw)
            b.append(f["svg"])
        for i, u in enumerate((0, .35, .7, 1.0)):
            x, y = 120 + i * 250, 1400
            hy, kw = P.rise_kw(u, x, y, s)
            b.append(P.dima_pj(x, hy, s, "bored76", "rest", **kw)["svg"])
        b.append(P.crowd_backs(0, 1940, 1080, 0.3, n=4, k=.9))
    elif page == 2:     # кухня: мама, бабушка, друг хлопают; студенты
        for i, w in enumerate(("mama", "granny", "friend")):
            x, y = 160 + i * 340, 640
            a, h = P.clap_arms(.9, x, y, s, w)
            b.append(P.person(w, x, y, s, "cheer76", None, arms=a, hands=h)["svg"])
        for i, w in enumerate(P.STUDENTS76):
            r, c = divmod(i, 3)
            x, y = 150 + c * 330, 1180 + r * 440
            pz = ("gesture76", "relax76", "thumb76", "write76", "write76", "shh76")[i]
            ex = ("tell_s76", "smug_s76", "proud76", "write_s76", "write_s76", "shh_s76")[i]
            kw = {}
            if pz == "shh76":
                kw["arms"] = {"n": ("ik", P.lips76(x, y, s, 0.02, 0.0, w), -1)}
            if pz == "relax76":
                kw["layers"] = P.LAYERS_BEHIND
            b.append(P.person(w, x, y, s, ex, pz, **kw)["svg"])
    else:               # кот
        b.append(P.cat_clap76(180, 600, .5, 0, 0.0))
        b.append(P.cat_clap76(520, 600, .5, 0, 1.0))
        b.append(P.cat_shh76(860, 600, .5, 0, 1.0))
        for i, nm in enumerate(("sniff", "no", "cam_paw", "sad", "poke", "sill", "watch", "wow")):
            r, c = divmod(i, 4)
            b.append(P.cat_svg(140 + c * 260, 1100 + r * 500, .42, P.CAT_ST76[nm], 0.0))
    return lib.svg("".join(b))


if __name__ == "__main__":
    out = sys.argv[1]
    pages = [int(a) for a in sys.argv[2:]] or [0, 1, 2, 3]
    d = tempfile.mkdtemp()
    lst = []
    for pg in pages:
        open(f"{d}/a{pg}.svg", "w").write(build(pg))
        lst.append(f"{d}/a{pg}.svg\t{out}_{pg}.png")
    open(d + "/l.txt", "w").write("\n".join(lst))
    subprocess.check_call(["node", os.path.join(COMMON, "render.js"), d + "/l.txt", "png", "1", "x"])
    print("\n".join(out + f"_{p}.png" for p in pages))
