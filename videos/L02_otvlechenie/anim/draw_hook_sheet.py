"""Лист слоёв для хука L02 (владелец 28.10: «+1 рисунок в хуке»): кот за столом, кот у холодильника оглядывается,
телефон — отдельными кусками на чистой бумаге, чтобы HyperFrames двигал чистые слои без дыр в фоне. Тот же промпт и
модель, что у scripts/reel_draw.py, только горизонтально 1536×1024 (та же цена 140 625)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import reel_draw  # noqa: E402

reel_draw.SIZE = "1536x1024"
reel_draw.draw(HERE, dry="--dry" in sys.argv)
