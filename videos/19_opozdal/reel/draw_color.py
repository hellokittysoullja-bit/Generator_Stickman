"""Цветные рисунки рилса 19 (владелец 04.11: «рисунки цветные — тот же рисованный стиль тушью на креме, но большая часть
рисунка раскрашена мягкой акварелью, не одноцветные и не кислотные»). Обёртка над scripts/reel_draw.py: та же модель,
референсы и порядок промпта, но палитра look/palette.txt («стены и пол серые») заменена цветной — только для этого
рилса, общие файлы не меняются. Запуск: REEL_DRAW_MODEL=cx/gpt-image-2.5 python draw_color.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import reel_draw  # noqa: E402

PALETTE = ("Colours: black ink lines on cream paper in exactly the hand-drawn style of the style references, and most of "
           "the picture is softly coloured with gentle transparent watercolour washes: walls, floor, furniture, clothes "
           "and objects each in its own natural muted colour (pale warm yellow or soft sky-blue walls, honey wooden floor, "
           "soft green, dusty pink, muted red, warm orange), light like a children's picture book; the paper texture shows "
           "through; never neon, never acid, never flat digital fill, never one single colour for everything. The main "
           "character stays black with green eyes, orange cheek marks and an orange tail flame")
_orig_open = open


def _open(p, *a, **kw):                                   # reel_draw.prompt читает look/palette.txt — подменяем только его
    if os.path.basename(str(p)) == "palette.txt":
        import io
        return io.StringIO(PALETTE)
    return _orig_open(p, *a, **kw)


reel_draw.open = _open
if __name__ == "__main__":
    reel_draw.draw(HERE, dry="--dry" in sys.argv, only=[a for a in sys.argv[1:] if not a.startswith("--")] or None)
