"""Движение внутри рисунка (scripts/anim.py): кривые, пружина, слой на месте — пиксель в пиксель, сжатие без двойного
контура, рисунок на двойках."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import anim  # noqa: E402


def test_bezier_and_gravity_ends():
    for f in (anim.EASE_OUT, anim.EASE_IN, anim.EASE_IO, anim.SNAP, anim.gravity):
        assert abs(f(0.0)) < 1e-3 and abs(f(1.0) - 1.0) < 1e-3
    assert anim.SNAP(1 / 3) > 0.75                     # резкий наезд: больше трёх четвертей пути за первую треть
    assert anim.gravity(0.5) == 0.25                   # падение: путь как квадрат времени


def test_spring_starts_at_one_and_settles():
    assert abs(anim.spring(0.0) - 1.0) < 1e-6
    assert min(anim.spring(t / 100) for t in range(100)) < 0     # перелёт через покой — отскок
    assert abs(anim.spring(1.5)) < 0.02                           # успокоилась


def test_track_keys():
    tr = anim.Track([(0.0, 0.0), (1.0, 10.0)])
    assert tr(-1) == 0.0 and tr(0.5) == 5.0 and tr(3) == 10.0
    tv = anim.Track([(0.0, (0.0, 0.0)), (1.0, (2.0, 4.0))])
    assert tv(0.5) == (1.0, 2.0)


def test_on_twos_holds_drawing():
    assert anim.on_twos(0.0) == anim.on_twos(1 / 13) == 0.0
    assert anim.on_twos(1 / 12 + 1e-4) == 1 / 12


def test_layer_at_home_is_pixel_exact():
    rng = np.random.default_rng(0)
    img = rng.uniform(0, 255, (120, 160, 3)).astype(np.float32)
    mask = np.zeros((120, 160), bool); mask[30:80, 40:110] = True
    lay = anim.Layer.cut(img, mask, pad=6, feather=0)
    base = np.zeros_like(img)
    lay.draw(base, lay.home())
    assert np.abs(base[mask] - img[mask]).max() < 1e-3   # слой на своём месте — тот же рисунок


def test_squash_is_a_warp_not_a_blend():
    """Сжатие — смещение пикселей, а не смесь двух картинок: линия остаётся одной линией (было: двойной контур)."""
    img = np.full((200, 200, 3), 255, np.float32); img[100:104, :] = 0           # горизонтальная линия
    m = np.full((200, 200), 0.5, np.float32)                                      # «мягкая» маска посередине силы
    out = anim.squash_region(img, m, 180, 100, 0.8, 1.0)
    dark_rows = np.where(out[:, 100, 0] < 128)[0]
    assert len(dark_rows) and dark_rows.max() - dark_rows.min() <= 6              # одна линия, не две
    assert dark_rows.min() > 104                                                  # и она сдвинулась к полу


def test_smear_trails_behind_motion():
    rgb = np.zeros((60, 60, 3), np.float32); a = np.zeros((60, 60), np.float32); a[25:35, 25:35] = 1
    _, out_a = anim._smear(rgb * a[..., None], a, (0.0, 12.0))                    # движется вниз
    assert out_a[15:25, 30].sum() > 0.5 and out_a[36:46, 30].sum() < 1e-3        # след сверху, впереди чисто
