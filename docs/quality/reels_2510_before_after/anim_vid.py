"""Видео было | стало удара: старая сцена слева, новая справа, замедление 2×, подписи."""
import sys, os, json, importlib.util, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/user/Generator_Stickman/scripts")
D = os.path.dirname(os.path.abspath(__file__)); R = "/home/user/Generator_Stickman/videos"
B = "/tmp/claude-0/-home-user-Generator-Stickman/7605bd81-268a-5536-b1b7-f9696ca784cb/scratchpad/before"
F = ImageFont.truetype(sys.argv[1], 34)
def load(path, name, reel_dir):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.REEL_DIR = reel_dir; return m
CASES = [("03_lenivyi", "hands_poke", (820, 700, 2220, 1900)), ("04_noch", "phone_fall", (640, 250, 1840, 1300)),
         ("05_ustal", "envelope_fall", (300, 600, 2400, 1900))]
for reel, name, (x0, y0, x1, y1) in CASES:
    rd = f"{R}/{reel}/reel"
    rep = json.load(open(f"{B}/{reel}/reel_report.json"))
    ctx = dict(words=[(w["start"], w["end"]) for w in rep["words"][:3]])
    old = load(f"{D}/old/{name}.py", f"old_{name}", rd); new = load(f"{rd}/anim/{name}.py", f"new_{name}", rd)
    W = 540; H = int(W * (y1 - y0) / (x1 - x0)); H += H % 2
    out = f"{D}/anim_{reel}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{2 * W}x{H + 50}", "-r", "15",
                           "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for k in range(int(1.6 * 30)):
        t = k / 30
        tiles = []
        for lab, m in (("было", old), ("стало", new)):
            img, _ = m.frame(t, ctx)
            c = np.clip(img[y0:y1, x0:x1], 0, 255).astype(np.uint8)
            tiles.append(cv2.resize(c, (W, H), interpolation=cv2.INTER_AREA))
        fr = np.full((H + 50, 2 * W, 3), 255, np.uint8); fr[50:] = np.concatenate(tiles, 1)
        im = Image.fromarray(fr); dr = ImageDraw.Draw(im)
        dr.text((12, 6), "было", fill=(150, 30, 30), font=F); dr.text((W + 12, 6), "стало", fill=(20, 110, 40), font=F)
        dr.text((2 * W - 260, 10), f"{t:.2f} с  ×0.5", fill=(90, 90, 90), font=F.font_variant(size=26))
        ff.stdin.write(np.asarray(im).tobytes())
    ff.stdin.close(); ff.wait()
    print(out)
