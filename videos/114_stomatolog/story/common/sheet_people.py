"""Контрольный лист героев рилса 64: python3 sheet_people.py [out] — Дима (позы и мимика), Дима-школьник, учительница в двух возрастах,
психолог, участники, отец, кот (шаг, лапа, поворот, клубок)."""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
import people as P  # noqa: E402

R_JS = os.path.join(HERE, "render.js")


def build(page=0):
    lib.DEFS.clear()
    b = ['<rect width="1080" height="1920" fill="#f4efe4"/>']
    if page == 0:       # позы взрослого Димы (по пояс, сидя) — 3×4
        poses = [("card", "unsure", {}), ("pen", "pressed", {}), ("scratch", "awkward", {"shrug": 1.0}), ("behind", "glum", {}),
                 ("chest", "pressed", {}), ("write", "write", {}), ("fold", "warm", {}), ("drawer", "glum", {}),
                 ("letter", "warm", {}), ("pet", "relief64", {}), ("hand_mouth", "thoughtful", {}), (None, "breath", {})]
        for i, (pz, ex, kw) in enumerate(poses):
            r, c = divmod(i, 3)
            x, y = 150 + c * 360, 560 + r * 440
            if pz == "mobile":
                f = P.dima_mobile(x, y, .38, ex)
            else:
                f = P.dima(x, y, .38, ex, pz, **kw)
            b.append(f["svg"])
        f = P.dima_mobile(870, 1880, .38, "nervous", "mobile_letter")
        b.append(f["svg"])
    elif page == 1:     # мимика Димы + полный рост + лотос + школьник
        names = ["unsure", "awkward", "glum", "thoughtful", "pressed", "nervous", "steady", "relief64", "warm", "write", "breath"]
        for i, n in enumerate(names):
            r, c = divmod(i, 4)
            b.append(P.dima(130 + c * 270, 420 + r * 430, .36, n, layers=("body",))["svg"])
        s = .34
        x, y = 160, 1500
        b.append(P.dima(x, y, s, "nervous", "mobile_letter", **P.stand_kw(x, y, s), layers=("legs", "pelvis", "arm_f", "body", "arm_n"))["svg"])
        f = P.dima_mobile(420, 1500, s, "steady", "mobile_letter", feet=P.stand_kw(420, 1500, s)["feet"])
        b.append(f["svg"])
        b.append(P.figure("dima", 690, 1700, s, P.EXPR["dima"]["thoughtful"], **P.lotus_kw("sit", 690, 1700, s))["svg"])
        b.append(P.kid_dima(900, 1560, .5, "beam")["svg"])
        b.append(P.kid_dima(900, 1880, .5, "shy", layers=("body",))["svg"])
    elif page == 2:     # учительница: одна женщина в двух возрастах + психолог
        b.append(P.teacher("young", 260, 620, .62, "kind", layers=("body",))["svg"])
        b.append(P.teacher("old", 780, 620, .62, "listen", layers=("body",))["svg"])
        b.append(P.teacher("young", 160, 1150, .4, "praise", "lean_desk")["svg"])
        b.append(P.teacher("old", 420, 1150, .4, "moved", "hand_mouth")["svg"])
        b.append(P.teacher("old", 680, 1150, .4, "laugh", None, head_add=-.35, lean_add=-.12)["svg"])
        b.append(P.teacher("old", 940, 1150, .4, "wipe", "wipe")["svg"])
        b.append(P.psychologist(180, 1780, .4, "calm")["svg"])
        b.append(P.psychologist(530, 1780, .4, "smile", "glasses")["svg"])
        b.append(P.psychologist(820, 1780, .4, "explain", "offer")["svg"])
    else:               # участники, отец, кот
        for i, (w, a, bb) in enumerate((("curly", "serious", "happy"), ("beard", "serious", "laugh"), ("youth", "serious", "happy"))):
            b.append(P.participant(w, 130 + i * 340, 520, .36, a, layers=("body",))["svg"])
            b.append(P.participant(w, 280 + i * 340, 520, .36, bb, layers=("body",))["svg"])
        b.append(P.participant("curly", 160, 1020, .36, "cover", "hand_mouth")["svg"])
        b.append(P.old_father(420, 1020, .36, "look_up")["svg"])
        b.append(P.old_father(680, 1020, .36, "moved", "heart")["svg"])
        b.append(P.participant("curly", 930, 1020, .36, "shy", "letter")["svg"])
        b.append(P.cat_walk(150, 1440, .38, .15))
        b.append(P.cat_svg(400, 1440, .38, {"paw": 1.0, "look": (.8, .3), "perk": 1}, 0.0))
        b.append(P.cat_svg(650, 1440, .38, {"turn": .5, "look": (-.2, 0)}, 0.0))
        b.append(P.cat_svg(900, 1440, .38, {"turn": -.2, "tilt": 12, "look": (0, 0), "ear": 14}, 0.0))
        b.append(P.cat_jump((150, 1880), (300, 1760), .38, .6, 0.0))
        b.append(P.cat_curl(560, 1880, .55, {"eye": 0.0}, 0.0))
        b.append(P.cat_curl(900, 1880, .55, {"eye": 1.0, "squint": 0.0}, 1.0))
        b.append(P.cat_curl(900, 1700, .55, {"squint": 1.0, "flame_e": 1.6}, .5))
    return lib.svg("".join(b))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/people64"
    pages = [int(a) for a in sys.argv[2:]] or [0, 1, 2, 3]
    d = tempfile.mkdtemp()
    lst = []
    for pg in pages:
        open(f"{d}/a{pg}.svg", "w").write(build(pg))
        lst.append(f"{d}/a{pg}.svg\t{out}_{pg}.png")
    open(d + "/l.txt", "w").write("\n".join(lst))
    subprocess.check_call(["node", R_JS, d + "/l.txt", "png", "1", "x"])
    print("\n".join(out + f"_{p}.png" for p in pages))
