"""Лица куклы героя: веселый (язык + звёздочки) и сон (дуги + Z). Заплатки лица — из кадров GPT-Image-2
(experiments/alive_cat/doll/faces). Без состояния face кадр куклы — байт в байт прежний."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import mascot_live as M  # noqa: E402

needs_faces = pytest.mark.skipif(not (M.available() and "sleep" in M._faces_available()),
                                 reason="рига или лица сна нет на диске")
needs_happy = pytest.mark.skipif(not (M.available() and "happy" in M._faces_available()),
                                 reason="эталона веселого лица нет (снят как брак 21.10, look/README.md)")


def _lime(r):
    return int(((r[..., 1] - r[..., 2] > 60) & (r[..., 1] > 140) & (r[..., 3] > .5)).sum())


def _rig():
    return M.rig()


def _frame(acts, t, dur=8):
    D = M._mod()
    st = D.plan(dur, acts, seed=1)(t)
    return _rig().frame_rgba(st, t), st


@needs_faces
def test_no_face_state_is_plain_cat():
    D = M._mod()
    st = D.plan(8, [], seed=1)(1.0)
    assert st["face"] is None and st["fx"] is None
    assert _rig().bb_for(st) == _rig().bb


@needs_happy
def test_happy_changes_only_mouth_and_keeps_eyes_alive():
    base, _ = _frame([], 2.0)
    happy, st = _frame([dict(t=0.3, do="face", name="happy")], 2.0)
    assert st["face"] == ("happy", 1.0)
    diff = np.abs(happy[..., :3] - base[..., :3]).sum(2) * (base[..., 3] > .9)
    ys, xs = np.nonzero(diff > 40)
    # изменилась только область рта (под носом): глаза и уши не тронуты
    assert ys.min() > 440 and ys.max() < 560 and xs.min() > 540 and xs.max() < 690
    # и взгляд живой: зрачок уходит в сторону и при веселом лице
    D = M._mod(); plan = D.plan(8, [dict(t=0.3, do="face", name="happy"), dict(t=1, do="look", x=.8, y=0, dur=2)], seed=1)
    a = _rig().frame_rgba(plan(0.9), 0.9); b = _rig().frame_rgba(plan(2.0), 2.0)
    assert np.abs(a[380:430, 440:560, :3] - b[380:430, 440:560, :3]).sum() > 1000


@needs_faces
def test_sleep_draws_arcs_and_no_green_iris():
    awake, _ = _frame([], 0.3)
    sleep, st = _frame([dict(t=0.3, do="face", name="sleep")], 2.0)
    assert st["face"][0] == "sleep" and st["face"][1] == 1.0
    def green(a):
        r = a[380:430, 440:800]
        return _lime(r)
    assert green(awake) > 5000 and green(sleep) == 0          # зелёных глаз нет совсем
    dark = (sleep[370:430, 460:770, :3].sum(2) < 90) & (sleep[370:430, 460:770, 3] > .9)
    assert dark.sum() > 2500                                    # две толстые дуги


@needs_faces
def test_sleep_closes_lids_before_arcs_appear():
    # переход: сначала веки смыкаются, потом дуги проявляются; зелёного становится монотонно меньше
    D = M._mod(); plan = D.plan(8, [dict(t=0.3, do="face", name="sleep")], seed=1)
    seq = []
    for t in np.linspace(0.3, 1.1, 9):
        a = _rig().frame_rgba(plan(t), t)[380:430, 440:800]
        seq.append(_lime(a))
    assert all(y <= x + 30 for x, y in zip(seq, seq[1:])) and seq[-1] == 0


@needs_faces
def test_fx_stars_and_zzz_only_with_face_and_window_widens():
    _, st = _frame([dict(t=0.3, do="face", name="happy")], 1.5)
    assert st["fx"][0] == "stars" and _rig().bb_for(st)[1] < _rig().bb[1] + 1
    _, st2 = _frame([dict(t=0.3, do="face", name="sleep")], 2.0)
    assert st2["fx"][0] == "zzz"
    _, st3 = _frame([dict(t=0.3, do="face", name="sleep", fx=False)], 2.0)
    assert st3["fx"] is None
    D = M._mod()
    L = D.fx_layer("stars", 1.5, 1.0, 0.3)
    assert L.shape[2] == 4 and L[..., 3].max() > 0.9 and (L[..., 3] > 0.5).sum() > 200
    # Z: первая видна не сразу, к 3 с их уже несколько
    z0 = D.fx_layer("zzz", 0.31, 1.0, 0.3)[..., 3]; z3 = D.fx_layer("zzz", 3.0, 1.0, 0.3)[..., 3]
    assert (z3 > .3).sum() > (z0 > .3).sum()


@needs_faces
def test_fx_move_between_frames():
    D = M._mod()
    a = D.fx_layer("stars", 1.0, 1.0, 0.3)[..., 3]; b = D.fx_layer("stars", 1.3, 1.0, 0.3)[..., 3]
    assert np.abs(a - b).sum() > 20                              # звёздочки мерцают и плывут, не стоят


def test_plan_actions_maps_mood_to_face(monkeypatch):
    monkeypatch.setattr(M, "_faces_available", lambda: {"happy", "sleep"})
    a = M.plan_actions(4.0, [], "x", (0, 0), mood="happy")
    assert any(x["do"] == "face" and x["name"] == "happy" for x in a)
    b = M.plan_actions(4.0, [], "x", (0, 0), mood="asleep")
    assert any(x["do"] == "face" and x["name"] == "sleep" for x in b)
    c = M.plan_actions(4.0, [], "x", (0, 0), mood="calm")
    assert not any(x["do"] == "face" for x in c)
    monkeypatch.setattr(M, "_faces_available", lambda: set())
    assert not any(x["do"] == "face" for x in M.plan_actions(4.0, [], "x", (0, 0), mood="happy"))   # нет файлов — нет лица


def test_planner_knows_asleep_mood():
    import frame_planner as fp
    assert "asleep" in fp.LIVE_MOODS and "asleep" in fp.HERO_MOODS
    assert not fp.live_emotion_blocked({"hero_mood": "asleep"}) and fp.live_emotion_blocked({"hero_mood": "sad"})


@needs_faces
def test_signature_covers_face_files():
    import inspect
    src = inspect.getsource(M.signature)
    assert "happy_mouth" in src and "sleep_eyes" in src


@needs_faces
def test_layer_composites_fx_outside_the_cat_box():
    import canvas
    L = M.Layer(dict(origin=[0.0, 0.0], scale=1.0, actions=[dict(t=0.3, do="face", name="sleep")], seed=0), 8.0)
    W, H = 1920, 1080
    f = np.empty((H, W, 3), np.float32); f[:] = canvas.CREAM
    g = L.composite(f.copy(), 3.5, (0, 0, W, H), W, H)
    lime = (g[..., 1] - g[..., 2] > 60) & (g[..., 1] > 120) & (g[..., 0] < 170)
    y0 = M.rig().bb[1]
    assert lime[:y0].sum() > 150                                  # Z поднялись выше рамки кота — окно кадра расширено
    L2 = M.Layer(dict(origin=[0.0, 0.0], scale=1.0, actions=[], seed=0), 8.0)
    g2 = L2.composite(f.copy(), 3.5, (0, 0, W, H), W, H)
    lime2 = (g2[..., 1] - g2[..., 2] > 60) & (g2[..., 1] > 120) & (g2[..., 0] < 170)
    assert lime2[:y0].sum() == 0
