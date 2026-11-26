"""python3 scripts/story_reel_lowmem.py videos/NNN/story — story_reel.py с ленивой загрузкой клипов (в памяти не больше 3 клипов): тот же вывод, меньше памяти."""
import collections
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import story_reel as SR  # noqa: E402

_CACHE = collections.OrderedDict()


class LazyClip:
    def __init__(self, path, start, fps):
        self.path, self.start, self.fps = path, start, fps

    @property
    def frames(self):
        if self.path in _CACHE:
            _CACHE.move_to_end(self.path)
            return _CACHE[self.path]
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", self.path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
        fr = np.frombuffer(p.stdout, np.uint8).reshape(-1, SR.H, SR.W, 3)
        _CACHE[self.path] = fr
        while len(_CACHE) > 3:
            _CACHE.popitem(last=False)
        return fr

    def at(self, t):
        fr = self.frames
        k = int(round((t - self.start) * self.fps))
        return fr[min(max(k, 0), len(fr) - 1)]


SR.Clip = LazyClip
SR.build(sys.argv[1])
