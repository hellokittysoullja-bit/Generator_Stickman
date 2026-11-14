"""Рендер клипов группы D рилса 64: python3 make.py s02 [s09 s16] — clips/<id>.mp4 (1080×1920, 30 к/с, CRF 16, клип = t0−0.2…t1+0.2),
один процесс; после рендера — контактный лист 6×2 в TMP/sheets/<id>_contact.jpg.
python3 make.py s02 --sheet [t1,t2,...] — PNG на эти моменты (по умолчанию 6 равномерно) + лист.
TMP — переменная окружения D64_TMP (по умолчанию /tmp/claude-0/-home-user/7605bd81-268a-5536-b1b7-f9696ca784cb/scratchpad/d64)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOTS = {s["id"]: s for s in SH["shots"]}
BASE_TMP = os.environ.get("D64_TMP", "/tmp/claude-0/-home-user/7605bd81-268a-5536-b1b7-f9696ca784cb/scratchpad/d64")


def span(sid):
    s = SHOTS[sid]
    a = max(0.0, s["t0"] - SH["pad"])
    b = min(s["t1"] + SH["pad"], SH["end"])
    return a, int(round((b - a) * 30))


def main():
    import s64d as s63a
    args = sys.argv[1:]
    sheet = "--sheet" in args
    ids = [a for a in args if a.startswith("s") and a[1:].isdigit()]
    tl = [a for a in args if "," in a]
    os.makedirs(BASE_TMP, exist_ok=True)
    os.makedirs(os.path.join(STORY, "clips"), exist_ok=True)
    cs = os.path.join(BASE_TMP, "sheets")
    os.makedirs(cs, exist_ok=True)
    for sid in ids:
        a, n = span(sid)
        tmp = tempfile.mkdtemp(dir=BASE_TMP, prefix=sid + "_")
        t0 = time.time()
        times = [float(x) for x in tl[0].split(",")] if (sheet and tl) else ([a + (n - 1) / 30 * k / 11 for k in range(12)] if sheet else
                                                                             [a + k / 30 for k in range(n)])
        svgs = []
        for i, t in enumerate(times):
            p = os.path.join(tmp, f"f{i:04d}.svg")
            open(p, "w").write(s63a.frame(sid, t))
            svgs.append(p)
        t1 = time.time()
        if sheet:
            pngs = [os.path.join(tmp, f"p{i:04d}.png") for i in range(len(times))]
            open(os.path.join(tmp, "list.txt"), "w").write("\n".join(f"{s}\t{p}" for s, p in zip(svgs, pngs)))
            subprocess.check_call(["node", os.path.join(STORY, "common", "render.js"), os.path.join(tmp, "list.txt"), "png", "1", "x"])
            out = os.path.join(cs, f"{sid}_sheet.jpg")
            subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "1", "-i", os.path.join(tmp, "p%04d.png"), "-vf",
                                   "scale=270:-1,tile=6x2", "-frames:v", "1", out])
            print(sid, "sheet", out, " ".join(f"{t:.2f}" for t in times))
        else:
            open(os.path.join(tmp, "list.txt"), "w").write("\n".join(svgs))
            pre = os.path.join(tmp, "seg")
            subprocess.check_call(["node", os.path.join(STORY, "common", "render.js"), os.path.join(tmp, "list.txt"), "mp4", "1", pre])
            out = os.path.join(STORY, "clips", f"{sid}.mp4")
            subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", pre + "_0.mp4", "-c", "copy", "-movflags", "+faststart", out])
            nf = int(subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                                              "stream=nb_read_frames", "-of", "csv=p=0", out]).decode().strip())
            print(f"{sid}: {out} frames {nf}/{n}  svg {t1 - t0:.0f}s render {time.time() - t1:.0f}s")
            subprocess.call(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-vf", "fps=3,scale=270:-1,tile=6x2", "-frames:v", "1",
                             os.path.join(cs, f"{sid}_contact.jpg")])
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
