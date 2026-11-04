"""Рисунки рилса 21 цветными (владелец 04.11: «рисунки — цветные: тот же рисованный стиль тушью на креме, но большая
часть рисунка раскрашена мягкой акварелью — стены, пол, предметы; не одноцветные и не кислотные»).
Общий scripts/reel_draw.py кладёт в промпт look/palette.txt («стены и пол — тушь и серое»), что спорит с этим словом
владельца; здесь — тот же reel_draw, только с цветной палитрой этого рилса. Запуск: python draw_color.py"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
os.environ.setdefault("REEL_DRAW_MODEL", "cx/gpt-image-2.5")      # 197 550 за рисунок, не дороже 200 000
import reel_draw  # noqa: E402

COLOR = ("Colours: black ink lines on cream paper in exactly the hand-drawn style of the style references, and most of "
         "the picture is gently coloured with soft transparent watercolour: the walls, the floor, the furniture and "
         "every object each get their own natural muted colour (warm beige walls, honey wooden floor, a soft blue sofa, "
         "pale yellow and white notes, cream mugs with brown coffee stains, a sage green kettle), light and airy, with "
         "the cream paper still glowing through; never neon, never acid-bright, never flat digital fills, never a "
         "single-colour picture. The main character stays black with green eyes, orange cheek marks and an orange "
         "tail flame")
_orig = reel_draw.prompt


def prompt(scene, n_style):
    pal = open(os.path.join(reel_draw.ROOT, "look", "palette.txt"), encoding="utf8").read().strip()
    out = _orig(scene, n_style)
    assert pal in out
    return out.replace(pal, COLOR)


reel_draw.MODEL = os.environ["REEL_DRAW_MODEL"]
reel_draw.prompt = prompt
if __name__ == "__main__":
    reel_draw.draw(HERE, dry="--dry" in sys.argv)
