"""Рендер клипов группы рилса 74: python3 make.py s13 [s14 ...] — clips/<id>.mp4 (1080×1920, 30 к/с, CRF 16, клип = t0−0.2…t1+0.2),
один процесс; после рендера — лист кадров 6×2 (fps=2) в TMP/sheets/<id>_contact.jpg.
python3 make.py s13 --sheet [t1,t2,...] — PNG на эти моменты (по умолчанию 6 равномерно) в TMP/sheets/<id>/.
Модуль сцены — s74<буква группы>.py рядом (frame(sid, t) -> SVG). TMP — /tmp/claude-0/.../scratchpad/<группа>74."""
import importlib
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
GRP = os.path.basename(HERE)[-1]                     # e / f
MOD = "s74" + GRP
BASE_TMP = os.path.join("/tmp/claude-0/-home-user/7605bd81-268a-5536-b1b7-f9696ca784cb/scratchpad", GRP + "74")


def span(sid):
    s = SHOTS[sid]
    a = max(0.0, s["t0"] - SH["pad"])
    b = s["t1"] + SH["pad"]
    return a, int(round((b - a) * 30))


def main():
    m = importlib.import_module(MOD)
    args = sys.argv[1:]
    sheet = "--sheet" in args
    ids = [a for a in args if a.startswith("s") and a[1:].isdigit()]
    tl = [a for a in args if "," in a or a.replace(".", "").isdigit()]
    os.makedirs(BASE_TMP, exist_ok=True)
    os.makedirs(os.path.join(STORY, "clips"), exist_ok=True)
    cs = os.path.join(BASE_TMP, "sheets")
    os.makedirs(cs, exist_ok=True)
    for sid in ids:
        a, n = span(sid)
        tmp = tempfile.mkdtemp(dir=BASE_TMP, prefix=sid + "_")
        t0 = time.time()
        if sheet:
            times = [float(x) for x in tl[0].split(",")] if tl else [a + (n - 1) / 30 * k / 5 for k in range(6)]
        else:
            times = [a + k / 30 for k in range(n)]
        svgs = []
        for i, t in enumerate(times):
            p = os.path.join(tmp, f"f{i:04d}.svg")
            open(p, "w").write(m.frame(sid, t))
            svgs.append(p)
        t1 = time.time()
        if sheet:
            outd = os.path.join(cs, sid)
            shutil.rmtree(outd, ignore_errors=True)
            os.makedirs(outd, exist_ok=True)
            pngs = [os.path.join(outd, f"{sid}_{t:.2f}.png") for t in times]
            open(os.path.join(tmp, "list.txt"), "w").write("\n".join(f"{s}\t{p}" for s, p in zip(svgs, pngs)))
            subprocess.check_call(["node", os.path.join(STORY, "common", "render.js"), os.path.join(tmp, "list.txt"), "png", "1", "x"])
            jl = os.path.join(cs, f"{sid}_sheet.jpg")
            subprocess.call(["ffmpeg", "-y", "-loglevel", "error", "-pattern_type", "glob", "-i", os.path.join(outd, "*.png"),
                             "-vf", "scale=360:-1,tile=6x1", "-frames:v", "1", jl])
            print(sid, "sheet", jl)
        else:
            open(os.path.join(tmp, "list.txt"), "w").write("\n".join(svgs))
            pre = os.path.join(tmp, "seg")
            subprocess.check_call(["node", os.path.join(STORY, "common", "render.js"), os.path.join(tmp, "list.txt"), "mp4", "1", pre])
            segs = sorted(x for x in os.listdir(tmp) if x.startswith("seg_") and x.endswith(".mp4"))
            open(os.path.join(tmp, "concat.txt"), "w").write("".join(f"file '{os.path.join(tmp, s)}'\n" for s in segs))
            out = os.path.join(STORY, "clips", f"{sid}.mp4")
            subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "concat.txt"),
                                   "-c", "copy", "-movflags", "+faststart", out])
            nf = int(subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                                              "stream=nb_read_frames", "-of", "csv=p=0", out]).decode().strip())
            print(f"{sid}: {out} frames {nf}/{n}  svg {t1 - t0:.0f}s render {time.time() - t1:.0f}s")
            subprocess.call(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-vf", "fps=2,scale=270:-1,tile=6x2", "-frames:v", "1",
                             os.path.join(cs, f"{sid}_contact.jpg")])
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
