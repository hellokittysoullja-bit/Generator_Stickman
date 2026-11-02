"""Увеличение рисунка: с 02.11 — waifu2x по выбору владельца (лист «исходник / наше / waifu2x»)."""
import os
import sys

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import upscale  # noqa: E402

HAS = os.path.exists(upscale.W2X_PATH)


def test_default_method_is_waifu2x(monkeypatch):
    monkeypatch.delenv("UPSCALE_METHOD", raising=False)
    assert upscale.method() == "waifu2x"


@pytest.mark.skipif(not HAS, reason="нет models/waifu2x (качается при первом запуске)")
def test_waifu2x_keeps_the_drawing_and_leaves_paper_to_lanczos(monkeypatch):
    monkeypatch.delenv("UPSCALE_METHOD", raising=False); monkeypatch.setenv("UPSCALE_NEURAL", "1")
    upscale._SESSION = None
    a = np.full((300, 300, 3), 240, np.uint8)
    a[100:200, 148:152] = 20                                     # штрих туши
    out = upscale.upscale(a, 2)
    L = np.asarray(Image.fromarray(a).resize((600, 600), Image.LANCZOS))
    assert np.array_equal(out[:150, :150], L[:150, :150])         # пустой кусок — Lanczos как есть
    small = np.asarray(Image.fromarray(out).resize((300, 300), Image.LANCZOS)).astype(float)
    assert 10 * np.log10(255 ** 2 / ((small - a) ** 2).mean()) > 35   # рисунок верен исходнику (не «обводка маркером»)
