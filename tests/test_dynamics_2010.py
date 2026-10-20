"""Защита от трёх жалоб владельца 20.10 (эп.02): серая надпись, медленное письмо, статичные планы."""
import inspect
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))


def test_pencil_ink_is_black_not_graphite():
    import frame_clip
    assert frame_clip.INK.max() <= 30           # было (52, 50, 56): серая надпись


def test_pencil_stroke_is_nearly_opaque():
    import writeon
    assert inspect.signature(writeon.Ink.__init__).parameters['tone'].default >= 0.95      # tone: доля чернил в штрихе (было 0.86)


def test_writing_speed_not_slower_than_owner_limit():
    import writeon
    assert writeon.SPEED_PER_SIZE >= 9.0        # было 7.0 (1.1 с на слово), владелец: «чуть быстрее»


def test_objects_use_model_that_obeys_no_reasoning():
    import objects
    assert not objects.OBJECTS_MODEL.startswith("qwen/")     # qwen3.7-plus на рамках игнорирует reasoning=False


def test_static_plans_are_reported_loudly():
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts",
                            "assemble_frames.py"), encoding="utf-8").read()
    assert "MAX_AVG_VIEW_SEC" in src and "ролик будет статичным" in src


def test_doll_finds_spot_on_full_width_diagram_without_covering_the_line():
    import mascot_live
    SW, SH = 1152, 648
    busy = np.zeros((SH, SW), np.float32)
    busy[int(0.62*SH):int(0.62*SH) + 3, 40:SW - 40] = 1.0          # линия схемы на всю ширину
    busy[int(0.82*SH):int(0.82*SH) + 20, 150:SW - 150] = 1.0       # строка подписи
    class R:                                                       # окно куклы 300x400 в координатах рига
        tight = (0, 0, 300, 400)
    spot = mascot_live._free_spot(dict(SW=SW, SH=SH, busy=busy), R, (0, 0, SW, SH))
    assert spot is not None
    share, v, side, x, floor = spot
    ch = share*SH
    assert floor - 0.015*SH <= 0.62*SH or floor - ch >= 0.62*SH + 3     # линия либо под котом, либо над ним, не сквозь
