"""Какой модуль рисует какой план (комнатные и схемные сцены рилса 48)."""
import importlib

MODS = {"s01": "scene_desk", "s02": "scene_desk", "s06": "scene_desk", "s14": "scene_desk",
        "s05": "scene_diag", "s07": "scene_diag", "s08": "scene_diag", "s09": "scene_diag", "s10": "scene_diag", "s11": "scene_diag",
        "s12": "scene_diag", "s13": "scene_diag", "s15": "scene_diag",
        "s16": "scene_bed", "s17": "scene_bed", "s18": "scene_bed"}


def load(sid):
    return importlib.import_module(MODS[sid])
