"""Гибкий хвост (scripts/tail_rig.py, владелец 02.11): сетка по силуэту, огонёк отдельно, физика устойчива."""
import math
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import tail_rig  # noqa: E402


def _c_tail():
    a = np.zeros((400, 300), np.uint8)
    cv2.ellipse(a, (150, 200), (110, 150), 0, 60, 300, 255, 40)          # «C» с завитком
    rgba = np.dstack([np.full((400, 300, 3), 40, np.uint8), a])
    cv2.circle(rgba, (205, 70), 18, (250, 170, 60, 255), -1)            # огонёк на кончике
    return rgba


def test_split_flame_and_mesh_follow_the_silhouette():
    rgba = _c_tail()
    body, flame, fl = tail_rig.split_flame(rgba)
    assert flame is not None and fl["base"][1] > 60
    assert body[70, 205, 3] < 30                                         # огонёк ушёл из тела хвоста
    mesh = tail_rig.build_mesh(body, attach=(210, 330), bones=6)
    base, tip = mesh["bones"][0], mesh["tip"]
    assert math.hypot(base[0] - 210, base[1] - 330) < math.hypot(tip[0] - 210, tip[1] - 330)   # основание у крепления
    assert len(mesh["idx"]) % 3 == 0 and len(mesh["verts"]) > 50
    # ячейки через просвет «C» отброшены: ни один треугольник не соединяет витки с разной долей длины
    assert all(max(abs(mesh["verts"][i][4]) for i in mesh["idx"][k:k + 3]) <= 1.0 for k in range(0, len(mesh["idx"]), 3))


def test_physics_is_stable_and_whips_on_the_hit():
    rgba = _c_tail()
    body, _, _ = tail_rig.split_flame(rgba)
    mesh = tail_rig.build_mesh(body, attach=(210, 330), bones=6)
    still = [[1, 0, 0, 1, 0.0, 0.0]] * int(1.6 * tail_rig.HZ + 10)
    ang = tail_rig.simulate(mesh, still, (0, 0), hit=0.8, dur=1.6)["angles"]
    mx = max(abs(v) for row in ang for v in row)
    assert mx < math.radians(tail_rig.PHYS["limit_deg"] + 25)             # без раскрутки звеньев (ошибка знака 02.11)
    before = max(abs(row[-1]) for row in ang[:int(0.75 * tail_rig.HZ)])
    after = max(abs(row[-1]) for row in ang[int(0.85 * tail_rig.HZ):int(1.3 * tail_rig.HZ)])
    assert after > before                                                # на ударе кончик хлещет сильнее, чем при махе
