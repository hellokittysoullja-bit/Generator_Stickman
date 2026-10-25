"""Библиотека оригиналов (25.10, владелец): каждая генерация кладётся в library/cat байт в байт, без дублей."""
import io
import json
import os

from PIL import Image

import cat_library


def _png(color):
    b = io.BytesIO(); Image.new("RGB", (40, 30), color).save(b, "PNG"); return b.getvalue()


def test_capture_keeps_original_bytes_and_skips_duplicates(tmp_path, monkeypatch):
    monkeypatch.setattr(cat_library, "LIB", str(tmp_path))
    monkeypatch.setenv("CAT_LIBRARY", "1")
    a, b = _png((10, 20, 30)), _png((200, 100, 50))
    cat_library.capture([a, b], "cx/gpt-image-2", "кот на полу", "1536x1024", "medium", 140625)
    cat_library.capture([a], "cx/gpt-image-2", "кот на полу", "1536x1024", "medium", 140625)   # та же картинка
    cat = json.load(open(tmp_path / "catalog.json", encoding="utf8"))
    assert len(cat) == 2
    files = {r["sha256"]: r["file"] for r in cat}
    import hashlib
    assert open(tmp_path / "originals" / files[hashlib.sha256(a).hexdigest()], "rb").read() == a   # байт в байт
    assert all(os.path.exists(tmp_path / "thumbs" / (f.rsplit(".", 1)[0] + ".jpg")) for f in files.values())
    assert cat[0]["prompt"] == "кот на полу" and (tmp_path / "README.md").exists()


def test_capture_is_off_in_tests_by_default(tmp_path, monkeypatch):
    monkeypatch.setattr(cat_library, "LIB", str(tmp_path / "lib"))
    cat_library.capture([_png((1, 2, 3))], "m", "p")                  # conftest: CAT_LIBRARY=0
    assert not (tmp_path / "lib" / "catalog.json").exists()
