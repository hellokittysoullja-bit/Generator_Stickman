"""Цветные рисунки рилса 19 (владелец 04.11: «рисунки цветные — тот же рисованный стиль тушью на креме, но большая часть
рисунка раскрашена мягкой акварелью, не одноцветные и не кислотные»). Обёртка над scripts/reel_draw.py: та же модель,
референсы и порядок промпта, но палитра look/palette.txt («стены и пол серые») заменена цветной — только для этого
рилса, общие файлы не меняются. Запуск: REEL_DRAW_MODEL=cx/gpt-image-2.5 python draw_color.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import reel_draw  # noqa: E402

PALETTE = ("Colours: black ink lines on cream paper in exactly the hand-drawn style of the style references; the main "
           "character and the objects are softly painted with gentle muted watercolour, each in its own natural colour, never neon; "
           "the background is plain warm cream paper like a blank drawing sheet (владелец 04.11): no painted walls, no wall colour, "
           "no floorboards, no sky colour, only one thin ink floor line or a soft light-grey shadow under things that stand. The "
           "main character stays black with green eyes, orange cheek marks and an orange tail flame")
_orig_open = open


def _open(p, *a, **kw):                                   # reel_draw.prompt читает look/palette.txt — подменяем только его
    if os.path.basename(str(p)) == "palette.txt":
        import io
        return io.StringIO(PALETTE)
    return _orig_open(p, *a, **kw)


reel_draw.open = _open
if __name__ == "__main__":
    reel_draw.draw(HERE, dry="--dry" in sys.argv, only=[a for a in sys.argv[1:] if not a.startswith("--")] or None)
