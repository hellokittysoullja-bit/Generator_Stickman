"""Цвета субтитров — опция reel.json "caption_colors" (эксперимент владельца 04.11, рилс 20): красный вместо жёлтого
активного и оранжевого ключевого слова; без опции — прежние цвета у всех рилсов."""
import numpy as np

import reel


def _colors(spec):
    reel.apply_caption_colors(spec)
    img = np.asarray(reel.render_chunk(["Купил", "*абонемент*"], [0, 1], 1, fade_ahead=False))
    return img


def test_default_caption_colors_unchanged():
    assert reel.apply_caption_colors({}) == {"active": reel.ACTIVE, "key": reel.KEY}
    assert reel.ACTIVE == (255, 210, 63) and reel.KEY == (255, 138, 31)


def test_red_caption_colors_only_for_own_reel():
    red = _colors({"caption_colors": "red"})
    assert reel.CAP_COLORS["key"] == (235, 45, 45) and reel.CAP_COLORS["active"] == (235, 45, 45)
    px = red[..., :3][red[..., 3] == 255].reshape(-1, 3).astype(int)
    assert ((px[:, 0] > 200) & (px[:, 1] < 80) & (px[:, 2] < 80)).any()       # ключевое слово красное
    assert ((px > 245).all(1)).any()                                            # базовые буквы белые
    dflt = _colors({})
    px = dflt[..., :3][dflt[..., 3] == 255].reshape(-1, 3).astype(int)
    assert not ((px[:, 0] > 200) & (px[:, 1] < 80) & (px[:, 2] < 80)).any()   # без опции красного нет
    assert reel.CAP_COLORS == {"active": reel.ACTIVE, "key": reel.KEY}


def test_caption_colors_reach_spawned_render_workers():
    """Живой промах 04.11: рилс 20 отрисовал часть планов жёлтым — процессы spawn начинали с цветов по умолчанию, а
    ключ кэша плана цвета не знал. Цвет передаётся в процесс (_init_job) и входит в ключ, только если он свой."""
    reel.apply_caption_colors({})
    job = tuple(range(13)) + ({"active": (235, 45, 45), "key": (235, 45, 45)},)
    reel._init_job(job)
    assert reel.CAP_COLORS["active"] == (235, 45, 45)
    shots = [dict(t0=0.0, t1=1.0, src="f1")]
    k_red = reel.segment_key(".", 30, 0, 30, 0, shots, [], [], [], [], None, 1.0, "x")
    reel.apply_caption_colors({})
    k_def = reel.segment_key(".", 30, 0, 30, 0, shots, [], [], [], [], None, 1.0, "x")
    assert k_red != k_def
