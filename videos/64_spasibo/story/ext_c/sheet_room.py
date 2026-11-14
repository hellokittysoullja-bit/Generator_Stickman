"""Лист проверки common/room.py: python3 sheet_room.py — PNG видов комнаты (стол вечер/день трёх камер, окно, диван) с сидящим Димой."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import lib  # noqa: E402
import people  # noqa: E402
import room as R  # noqa: E402

OUT = "/tmp/claude-0/-home-user/7605bd81-268a-5536-b1b7-f9696ca784cb/scratchpad/c64/room"


def seated(x, y, bs=1.0, lean=.08):
    sc = bs * people.HEIGHT["dima"]
    arms = {"f": ("ik", (x + 200 * sc, R.DESK_TOP - 80), -1), "n": ("ik", (x + 260 * sc, R.DESK_TOP - 70), -1)}
    feet = {"n": ((x + 300 * bs, R.FL - 52), 0.0), "f": ((x + 250 * bs, R.FL - 50), 0.0)}
    return people.draw(dict(hip=(x, y), scale=sc, lean=lean, feet=feet, arms=arms, hands={}, head_ang=0.0, expr=people.EXPR["dima"]["calm_smile"],
                            torso_k=1.0, hood=0.0, head_off=(0, 0)), "dima")


def desk_frame(mode, camv):
    lib.dyn_begin()
    sc = R.desk_scene(0.3, mode, drawer=.0 if camv != R.CAM_DESK_LOW else 1.0)
    fu = seated(*R.SIT)
    body = [sc["bg"], sc["chair_back"], fu["legs"], sc["chair_seat"], fu["arm_f"], fu.get("pelvis", ""), fu["body"], sc["desk"], sc["pool"], fu["arm_n"], sc["lamp"]]
    return lib.svg(f'<g transform="{lib.cam(*camv)}">{"".join(body)}</g>')


def other(kind):
    lib.dyn_begin()
    if kind == "win":
        sc = R.window_scene(0.5, "day")
        fu = people.figure("dima", R.STAND[0], R.FL - (people.LEG_LEN - 12) * 1.0, 1.0, people.EXPR["dima"]["calm_smile"], **people.stand_kw(R.STAND[0], R.FL - (people.LEG_LEN - 12), 1.0))
        return lib.svg(f'<g transform="{lib.cam(*R.CAM_WIN)}">{sc["bg"]}{fu["svg"]}</g>')
    sc = R.sofa_scene(0.5, "day")
    x, y = R.SOFA_DIMA
    fu = people.draw(dict(hip=(x, y), scale=1.0, lean=-.05, feet={"n": ((x + 290, R.FL - 52), 0.0), "f": ((x + 240, R.FL - 50), 0.0)},
                          arms={"f": ("ang", 0.3, 0.3), "n": ("ik", (x + 230, y - 60), -1)}, hands={}, head_ang=0.0, expr=people.EXPR["dima"]["calm_smile"],
                          torso_k=1.0, hood=0.0, head_off=(0, 0)), "dima")
    cw = R.CLEAN_WALL
    box = f'<rect x="{cw[0]}" y="{cw[1]}" width="{cw[2]-cw[0]}" height="{cw[3]-cw[1]}" fill="none" stroke="red" stroke-width="4" stroke-dasharray="20 10"/>'
    cat = people.cat_svg(R.ARM_TOP[0], R.ARM_TOP[1], .9, {}, 0.5)
    body = sc["bg"] + sc["sofa"] + fu["legs"] + fu["arm_f"] + fu.get("pelvis", "") + fu["body"] + fu["arm_n"] + sc["front"] + cat + box
    return lib.svg(f'<g transform="{lib.cam(*R.CAM_SOFA)}">{body}</g>')


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = [("ev_close", lambda: desk_frame("evening", R.CAM_DESK_CLOSE)), ("ev_mid", lambda: desk_frame("evening", R.CAM_DESK_MID)),
            ("ev_low", lambda: desk_frame("evening", R.CAM_DESK_LOW)), ("day_close", lambda: desk_frame("day", R.CAM_DESK_CLOSE)),
            ("win", lambda: other("win")), ("sofa", lambda: other("sofa"))]
    lst = []
    for name, fn in jobs:
        p = os.path.join(OUT, name + ".svg")
        open(p, "w").write(fn())
        lst.append(f"{p}\t{p[:-4]}.png")
    open(os.path.join(OUT, "list.txt"), "w").write("\n".join(lst))
    subprocess.check_call(["node", os.path.join(STORY, "common", "render.js"), os.path.join(OUT, "list.txt"), "png", "1", "x"])
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error"] + sum([["-i", l.split("\t")[1]] for l in lst], []) +
                          ["-filter_complex", "".join(f"[{i}]scale=360:-1[v{i}];" for i in range(6)) + "".join(f"[v{i}]" for i in range(6)) + "hstack=6",
                           os.path.join(OUT, "room_sheet.jpg")])
    print(os.path.join(OUT, "room_sheet.jpg"))


if __name__ == "__main__":
    main()
