"""Монтаж длинного ролика 15.11 (владелец: единый вид, переходы, направление камеры и взгляд).

Приёмка меряет бумагу, а не глаза кота; кот-ведущий и сцена на бумаге — не ход камеры; переходы по смыслу — только
по полю "transition" (без него план и клип прежние), склейка остаётся на своём кадре; подсказки стыков — по окнам."""
import json
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import long_edit  # noqa: E402
import long_montage  # noqa: E402
import long_transitions as lt  # noqa: E402
import montage_qc as mq  # noqa: E402

WORDS = [{"word": "раз", "start": 0.0, "end": 0.3}, {"word": "два", "start": 1.5, "end": 1.8},
         {"word": "три", "start": 3.0, "end": 3.3}]
FR = {"off": (0, 0), "SW": 1600, "SH": 900}
FPS, W, H = 24, 320, 180


def test_paper_mask_takes_cream_not_the_green_eyes():
    """L03 15.11: ΔE 20 «тона бумаги» на склейке «морда крупно → общий план» — маска L*>85 брала светло-зелёную радужку
    (L* 89, a* −19, b* +40). Бумага канала — крем C* ≈ 4–6."""
    from skimage import color
    cream = color.rgb2lab(np.full((4, 4, 3), [250, 247, 240], np.float32)/255)
    iris = color.rgb2lab(np.full((4, 4, 3), [205, 230, 120], np.float32)/255)
    assert iris[0, 0, 0] > mq.PAPER_L_MIN                      # по одной светлоте радужка — «бумага»
    assert mq.paper_mask(cream).all() and not mq.paper_mask(iris).any()


def _sc(zoom_signs):
    """Скан с окнами зума по 0,25 с: знак каждого окна задан."""
    return dict(fps=FPS, zoom=[1.002 if s > 0 else 0.998 for s in zoom_signs], n=len(zoom_signs)*6)


def test_direction_ignores_narrator_and_splits_on_stage():
    """L03: два из трёх «переворотов» — кот-ведущий растёт поверх размытой сцены, третий — стикеры → рисунок."""
    signs = [1]*8 + [-1]*8 + [1]*8                              # три плана по 2 с: наезд, «отъезд», наезд
    plans = [(0.0, 2.0), (2.0, 4.0), (4.0, 6.0)]
    assert mq.direction_metrics(_sc(signs), plans, [0.0], 6.0)["direction_flips_excess"] == 2
    assert mq.direction_metrics(_sc(signs), plans, [0.0], 6.0, narrator=[(2.0, 4.0)])["direction_flips_excess"] == 0
    plans5 = [(0.0, 1.0), (1.0, 2.0), (2.0, 4.0), (4.0, 5.0), (5.0, 6.0)]          # сцена на бумаге — 2–4 с
    assert mq.direction_metrics(_sc(signs), plans5, [0.0], 6.0)["direction_flips_excess"] == 2
    assert mq.direction_metrics(_sc(signs), plans5, [0.0], 6.0, stages=[(2.0, 4.0)])["direction_flips_excess"] == 0
    r = mq.direction_metrics(_sc(signs), plans, [0.0], 6.0)
    assert [f["plan_at"] for f in r["direction_flips"]] == [2.0, 4.0]          # где — в отчёте


def test_stage_windows_from_report(tmp_path):
    mp = tmp_path / "media_plan"; mp.mkdir()
    (mp / "shots_report.json").write_text(json.dumps({"clips": [
        {"index": 0, "duration": 2.0}, {"index": 1, "duration": 6.0, "stage": [[1.0, 3.0]]}]}), encoding="utf-8")
    assert mq.stage_windows(str(tmp_path)) == [(pytest.approx(3.0), pytest.approx(5.0))]


def test_without_transition_plan_is_unchanged():
    """Правило владельца 15.11: без поля сборка прежняя — в сегментах нет новых ключей (подпись клипа та же)."""
    shots = [{"win": [800, 450, 1600], "why": "общий вид комнаты"}, {"at": "два", "win": [400, 300, 600], "why": "морда"}]
    segs = long_edit.segments(FR, shots, WORDS, 5.0)
    assert not any(k in s for s in segs for k in ("trans", "trans_out", "light_from", "light_to"))


def test_transition_goes_to_both_sides_of_the_cut():
    shots = [{"win": [800, 450, 1600], "why": "общий вид комнаты"},
             {"at": "два", "win": [400, 300, 600], "why": "морда", "sound": "swoosh",
              "transition": {"kind": "move", "dir": "right", "why": "камера едет дальше к морде"}}]
    segs = long_edit.segments(FR, shots, WORDS, 5.0)
    assert segs[1]["trans"]["kind"] == "move" and segs[0]["trans_out"] == segs[1]["trans"]
    assert segs[1]["t0"] == 1.5                                   # склейка на своём слове
    with pytest.raises(ValueError):
        lt.spec({"transition": {"kind": "dissolve"}})
    with pytest.raises(ValueError):
        lt.spec({"transition": {"kind": "move", "dir": "diagonal"}})


def _seg(t0, t1, **kw):
    return dict(t0=t0, t1=t1, **kw)


def test_light_meets_in_the_middle_and_keeps_the_cut_frame():
    """Чёрный кот крупно (40) → бумага (230): на стыке средняя яркость одна, шаг кадр-в-кадр — шестая часть
    перепада, а не весь; вне окна перехода кадры нетронуты."""
    tr = {"kind": "light", "v": lt.VERSION}
    a, b = _seg(0.0, 1.0, trans_out=tr), _seg(1.0, 2.0, trans=tr)
    dark, light = np.full((H, W, 3), 40.0, np.float32), np.full((H, W, 3), 230.0, np.float32)
    seq = [lt.apply(dark, a, k/FPS, FPS, (0, 0, W, H), (0, 0), [230.0]*3) for k in range(FPS)] + \
          [lt.apply(light, b, 1.0 + k/FPS, FPS, (0, 0, W, H), (0, 0), [40.0]*3) for k in range(FPS)]
    m = [float(f.mean()) for f in seq]
    assert m[FPS - 1] == pytest.approx(m[FPS], abs=0.01)          # у стыка — один тон с обеих сторон
    assert max(abs(x - y) for x, y in zip(m, m[1:])) <= (230 - 40)/6 + 0.5
    assert m[0] == 40.0 and m[-1] == 230.0
    assert sum(abs(x - y) > 0.01 for x, y in zip(m, m[1:])) == 2*lt.LIGHT_FRAMES       # 3 + 3 кадра


def test_move_continues_in_one_direction_through_the_cut():
    """Переход по движению: по обе стороны стыка картинка едет в одну сторону (камера вправо — картинка влево),
    быстрее всего у стыка."""
    tr = {"kind": "move", "dir": "right", "v": lt.VERSION}
    a, b = _seg(0.0, 1.0, trans_out=tr), _seg(1.0, 2.0, trans=tr)
    img = np.full((H, W, 3), 240.0, np.float32)
    img[:, W//2 - 4:W//2 + 4] = 0.0                                # вертикальная линия по центру

    def x_of(f):
        col = f.mean((0, 2))
        return float(np.argmin(col))
    xs = [x_of(lt.apply(img, a, k/FPS, FPS, (0, 0, W, H), (0, 0))) for k in range(FPS - 5, FPS)] + \
         [x_of(lt.apply(img, b, 1.0 + k/FPS, FPS, (0, 0, W, H), (0, 0))) for k in range(0, 5)]
    out, inn = xs[:5], xs[5:]
    assert all(y <= x + 1 for x, y in zip(out, out[1:]))           # уходящий: линия уезжает влево
    assert all(y <= x + 1 for x, y in zip(inn, inn[1:]))            # входящий: приезжает справа, едет туда же
    assert out[-1] < W/2 - 20 and inn[0] > W/2 + 20 and inn[-1] == pytest.approx(W/2, abs=3)


def test_transition_checks(tmp_path):
    (tmp_path / "edit.json").write_text(json.dumps({"frames": {"2": {"shots": [
        {"win": [1, 1, 100], "why": "общий вид комнаты", "transition": {"kind": "move", "dir": "left", "why": "переход"}},
        {"at": "x", "win": [1, 1, 50], "why": "морда крупно", "whip": "left", "sound": "swoosh",
         "transition": {"kind": "through", "why": "волна уходит в морду котика"}},
        {"at": "y", "win": [1, 1, 50], "why": "морда крупно", "transition": {"kind": "light", "why": "день в ночь мягче"}},
        {"at": "z", "win": [1, 1, 50], "why": "морда крупно", "transition": {"kind": "fade", "why": "день в ночь мягче"}},
    ]}}}), encoding="utf-8")
    err = long_montage.transition_checks(str(tmp_path))
    assert any("план 1" in e and "why" in e for e in err)                 # «переход» — не смысл
    assert any("план 1" in e and "sound" in e for e in err)               # движение без звука
    assert any("план 2" in e and "whip" in e for e in err)                # один переход на стык
    assert any("план 4" in e and "kind" in e for e in err)
    assert not any("план 3" in e for e in err)                            # свет без звука — можно


def test_hints_catch_light_jump_and_attention_jump_and_respect_transition(tmp_path):
    cv = np.full((900, 1600, 3), 240, np.uint8)
    cv[100:800, 100:500] = 20                                              # чёрный кот слева, крупно
    cv[400:450, 1300:1400] = 30                                            # мелкий предмет справа
    shots = [{"win": [400, 450, 900], "why": "морда крупно"}, {"at": "a", "win": [1200, 450, 900], "why": "предмет справа"}]
    (tmp_path / "edit.json").write_text(json.dumps({"frames": {"1": {"shots": shots}}}), encoding="utf-8")
    hs = long_montage.hints(str(tmp_path), screens={"1": (cv, (0, 0))})
    assert any(h.startswith("LUMA") for h in hs) and any(h.startswith("ATTENTION") for h in hs)
    shots[1]["transition"] = {"kind": "light", "why": "с морды на бумагу мягче"}
    (tmp_path / "edit.json").write_text(json.dumps({"frames": {"1": {"shots": shots}}}), encoding="utf-8")
    assert not long_montage.hints(str(tmp_path), screens={"1": (cv, (0, 0))})


def test_hint_on_zoom_out_among_push_ins(tmp_path):
    cv = np.full((900, 1600, 3), 240, np.uint8)
    cv[300:600, 600:1000] = 30
    shots = [{"win": [800, 450, 1000], "why": "котик целиком"},
             {"at": "a", "win": [800, 450, 600], "to": [800, 450, 900], "why": "отъезд от морды"},
             {"at": "b", "win": [800, 450, 900], "why": "котик целиком"}]
    (tmp_path / "edit.json").write_text(json.dumps({"frames": {"1": {"shots": shots}}}), encoding="utf-8")
    hs = [h for h in long_montage.hints(str(tmp_path), screens={"1": (cv, (0, 0))}) if h.startswith("DIRECTION")]
    assert len(hs) == 2


def test_hint_on_picture_not_on_paper_unless_dark_on_purpose(tmp_path):
    cv = np.full((900, 1600, 3), 40, np.uint8)
    shots = [{"win": [800, 450, 1000], "why": "ночь в кровати"}]
    (tmp_path / "edit.json").write_text(json.dumps({"frames": {"1": {"shots": shots}}}), encoding="utf-8")
    assert any(h.startswith("PAPER") for h in long_montage.hints(str(tmp_path), screens={"1": (cv, (0, 0), False)}))
    (tmp_path / "edit.json").write_text(json.dumps({"frames": {"1": {"shots": shots, "dark_why": "ночь: котик не спит"}}}),
                                        encoding="utf-8")
    assert not any(h.startswith("PAPER") for h in long_montage.hints(str(tmp_path), screens={"1": (cv, (0, 0), False)}))


def test_move_and_through_move_the_camera_in_the_world():
    """move/through сдвигают окно камеры по миру рисунка (въезжает соседний рисунок, за краем — бумага), а не готовый
    кадр с повтором крайнего столбца (L03 15.11, фраза 47: полосы через экран)."""
    win = (100.0, 100.0, 900.0, 550.0)
    mv = {"kind": "move", "dir": "right", "v": lt.VERSION}
    a, b = _seg(0.0, 1.0, trans_out=mv), _seg(1.0, 2.0, trans=mv)
    wa = lt.camera_window(a, 1.0 - 1/FPS, FPS, win, (0, 0))
    wb = lt.camera_window(b, 1.0, FPS, win, (0, 0))
    assert wa[0] > win[0] + 300 and wb[0] < win[0] - 300                  # уходит вправо, приходит слева
    assert lt.camera_window(a, 0.2, FPS, win, (0, 0)) is None             # вне перехода — окно плана
    th = {"kind": "through", "point": [700, 300], "v": lt.VERSION}
    wt = lt.camera_window(_seg(1.0, 2.0, trans=th), 1.0, FPS, win, (0, 0))
    assert (wt[0] + wt[2])/2 == pytest.approx(700) and (wt[2] - wt[0]) == pytest.approx(800/lt.THROUGH_ZOOM)


def test_screen_pad_is_paper_outside_the_canvas():
    import canvas
    import frame_clip
    world = np.zeros((200, 400, 3), np.uint8)
    f = frame_clip._screen_pad(world, (-200.0, 0.0, 200.0, 225.0), 1)
    assert f[500, 100] == pytest.approx(canvas.CREAM) and f[500, 1800].max() == 0
