"""Движение внутри рисунка на HyperFrames — общий модуль для сцен рилсов и хуков длинных роликов.

Решение владельца 28.10: «гиперфреймс по КД везде используем»; 02.11: «чтобы все последующие Reels уже на автомате
делались… через гиперфреймс». Сравнение движков (videos/13_dver/reel/anim/ENGINES.md): HyperFrames размывает поворот
и масштаб, побайтно повторяется, не зависает; лицензия Apache-2.0.

Сцена — папка-проект HyperFrames (index.html с таймлайном GSAP в window.__timelines.main) и её слои (PNG). Источник
времени один — озвучка: сцена получает свои моменты (удар, смена, хлёст) как JSON в атрибуте data-vars корня
композиции; по умолчанию в index.html стоит пример, модуль подменяет его на время из слов фразы. Кадры — PNG без
потерь в кэше, ключ — проект, слои, время, версия движка и частота; поменялось что-то — кадры пересоберутся сами.

Использование в сцене (videos/NN/reel/anim/<имя>.py или videos/NN/anim/<имя>.py):
    import anim_hf
    hf = anim_hf.Scene(project_dir, assets_dir, fps=30, duration=1.5, cache_dir=...)
    frames = hf.render({"hit": 0.94})          # список PNG
    img = hf.frame(t)                           # uint8 RGB кадр в момент t (кэш на 3 кадра)
Камера хука (anim.hook_cam), тряска, субтитры и звук остаются у сборщика."""
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess

import numpy as np
from PIL import Image

HF = "hyperframes@0.8.214"            # версия закреплена: смена — только после побайтного сравнения кадров
VARS_RE = re.compile(r"data-vars='(\{.*?\})'", re.S)
MIN_FREE_GB = 1.5                      # HyperFrames отказывает при нехватке места; проверяем заранее, с понятной ошибкой


def default_vars(project_dir):
    """Пример времени из index.html (data-vars) — то, что сцена получит, если слов нет."""
    s = open(os.path.join(project_dir, "index.html"), encoding="utf-8").read()
    m = VARS_RE.findall(s)
    if len(m) != 1:
        raise ValueError(f"{project_dir}/index.html: нужен ровно один data-vars='{{…}}' на корне композиции")
    return json.loads(m[0])


LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hf_lib")     # общие скрипты композиций (lib/ проекта)


def signature(project_dir, assets_dir, variables, fps, version=1, extra=()):
    h = hashlib.md5()
    for p in sorted(glob.glob(os.path.join(LIB, "*"))) + [f for f in extra]:          # общая библиотека и код подготовки
        h.update(os.path.basename(p).encode()); h.update(open(p, "rb").read())
    for p in sorted(glob.glob(os.path.join(project_dir, "*.html")) + glob.glob(os.path.join(project_dir, "*.json"))):
        h.update(os.path.basename(p).encode()); h.update(open(p, "rb").read())
    for p in sorted(glob.glob(os.path.join(assets_dir, "*"))):
        h.update(os.path.basename(p).encode()); h.update(open(p, "rb").read())
    h.update(f"{json.dumps(variables, sort_keys=True)}|{fps}|{HF}|{version}".encode())
    return h.hexdigest()[:12]


class Scene:
    def __init__(self, project_dir, assets_dir, fps, duration, cache_dir, name=None, version=1, workers=2,
                 prepare=None, extra=()):
        """prepare(proj, variables) — шаг перед рендером в копии проекта (например, физика хвоста пишет углы в
        assets/); extra — файлы его кода: входят в ключ кэша."""
        self.project, self.assets, self.fps, self.dur = project_dir, assets_dir, fps, duration
        self.prepare, self.extra = prepare, tuple(extra)
        self.cache_dir, self.name = cache_dir, name or os.path.basename(os.path.normpath(project_dir))
        self.version, self.workers = version, workers
        self.frames, self._mem = [], {}

    def render(self, variables=None):
        """Кадры композиции с этим временем (dict, сливается с примером из index.html); список путей к PNG."""
        v = dict(default_vars(self.project))
        v.update(variables or {})
        out = os.path.join(self.cache_dir, f"{self.name}_{signature(self.project, self.assets, v, self.fps, self.version, self.extra)}")
        need = int(round(self.dur * self.fps))
        frames = sorted(glob.glob(os.path.join(out, "frames", "*.png")))
        if len(frames) >= need:
            self.frames, self._mem = frames, {}
            return frames
        free = shutil.disk_usage(os.path.dirname(os.path.abspath(out)) if os.path.exists(os.path.dirname(os.path.abspath(out)))
                                 else "/").free / 1e9
        if free < MIN_FREE_GB:
            raise RuntimeError(f"HyperFrames: на диске {free:.1f} ГБ, нужно хотя бы {MIN_FREE_GB} — освободите место "
                               "(кэши рендера пересобираются сами)")
        proj = os.path.join(out, "proj")
        shutil.rmtree(out, ignore_errors=True)
        shutil.copytree(self.project, proj, ignore=shutil.ignore_patterns("assets", "node_modules", "frames", "renders"))
        shutil.copytree(self.assets, os.path.join(proj, "assets"))
        shutil.copytree(LIB, os.path.join(proj, "lib"))
        html = os.path.join(proj, "index.html")
        s = open(html, encoding="utf-8").read()
        s = VARS_RE.sub(lambda _m: f"data-vars='{json.dumps(v, ensure_ascii=False)}'", s, count=1)
        open(html, "w", encoding="utf-8").write(s)
        if self.prepare is not None:
            self.prepare(proj, v)
        env = dict(os.environ, HYPERFRAMES_TELEMETRY="0", DO_NOT_TRACK="1")
        r = subprocess.run(["npx", "--yes", HF, "render", "--format", "png-sequence", "--fps", str(self.fps),
                            "--workers", str(self.workers), "-o", "frames", "--quiet"],
                           cwd=proj, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"HyperFrames: рендер {self.name} не удался:\n{(r.stdout + r.stderr)[-1500:]}")
        shutil.move(os.path.join(proj, "frames"), os.path.join(out, "frames"))    # путь вывода — относительный (CLI)
        shutil.rmtree(proj)
        frames = sorted(glob.glob(os.path.join(out, "frames", "*.png")))
        if len(frames) < need:
            raise RuntimeError(f"HyperFrames отдал {len(frames)} кадров из {need}: {out}")
        self.frames, self._mem = frames, {}
        return frames

    def frame(self, t):
        """RGB uint8 кадр композиции в момент t (за концом — последний). Держит в памяти не больше трёх кадров:
        клипы рендерятся в нескольких процессах, кадр хука ×2 весит десятки мегабайт."""
        if not self.frames:
            raise RuntimeError("сначала render()")
        i = min(len(self.frames) - 1, max(0, int(round(t * self.fps))))
        if i not in self._mem:
            if len(self._mem) > 2:
                self._mem.clear()
            self._mem[i] = np.asarray(Image.open(self.frames[i]).convert("RGB"))
        return self._mem[i]
