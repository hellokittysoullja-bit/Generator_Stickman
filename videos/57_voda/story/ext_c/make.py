"""Рендер клипов группы C рилса 57: python3 make.py s10 [s11 ...]  — clips/<id>.mp4 (1080×1920, 30 к/с, клип = t0−0.2…t1+0.2);
python3 make.py s10 --sheet [t1,t2,...] — PNG на эти моменты (по умолчанию 6 равномерно) в /tmp/a57c/sheets/<id>/ + лист jpg;
python3 make.py s10 --contact — контактный лист 12 кадров из готового клипа."""
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
os.makedirs(os.path.join(STORY, "clips"), exist_ok=True)
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOTS = {s["id"]: s for s in SH["shots"]}
BASE_TMP = "/tmp/a57c"


def span(sid):
    s = SHOTS[sid]
    a = max(0.0, s["t0"] - SH["pad"])
    b = min(s["t1"] + SH["pad"], SH["end"])
    return a, int(round((b - a) * 30))


def _job(args):
    sid, t, path = args
    m = importlib.import_module("s57")
    open(path, "w").write(m.frame(sid, t))
    return path


def build_svgs(sid, times, tmp):
    jobs = [(sid, t, os.path.join(tmp, f"f{i:04d}.svg")) for i, t in enumerate(times)]
    with Pool(2) as p:
        return p.map(_job, jobs, chunksize=4)


def main():
    sys.path.insert(0, HERE)
    args = sys.argv[1:]
    sheet = "--sheet" in args
    ids = [a for a in args if a.startswith("s") and a[1:].isdigit()]
    tl = [a for a in args if "," in a or a.replace(".", "").isdigit()]
    os.makedirs(BASE_TMP, exist_ok=True)
    for sid in ids:
        a, n = span(sid)
        tmp = tempfile.mkdtemp(dir=BASE_TMP, prefix=sid + "_")
        t0 = time.time()
        if sheet:
            times = [float(x) for x in tl[0].split(",")] if tl else [a + (n - 1) / 30 * k / 5 for k in range(6)]
            svgs = build_svgs(sid, times, tmp)
            outd = os.path.join(BASE_TMP, "sheets", sid)
            os.makedirs(outd, exist_ok=True)
            pngs = [os.path.join(outd, f"{sid}_{t:.2f}.png") for t in times]
            open(os.path.join(tmp, "list.txt"), "w").write("\n".join(f"{s}\t{p}" for s, p in zip(svgs, pngs)))
            subprocess.check_call(["node", os.path.join(HERE, "render.js"), os.path.join(tmp, "list.txt"), "png", str(min(2, len(times))), "x"])
            print(sid, "sheet", " ".join(pngs))
        else:
            times = [a + k / 30 for k in range(n)]
            svgs = build_svgs(sid, times, tmp)
            t1 = time.time()
            open(os.path.join(tmp, "list.txt"), "w").write("\n".join(svgs))
            pre = os.path.join(tmp, "seg")
            subprocess.check_call(["node", os.path.join(HERE, "render.js"), os.path.join(tmp, "list.txt"), "mp4", "2", pre])
            segs = sorted(x for x in os.listdir(tmp) if x.startswith("seg_") and x.endswith(".mp4"))
            open(os.path.join(tmp, "concat.txt"), "w").write("".join(f"file '{os.path.join(tmp, s)}'\n" for s in segs))
            out = os.path.join(STORY, "clips", f"{sid}.mp4")
            subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "concat.txt"),
                                   "-c", "copy", "-movflags", "+faststart", out])
            nf = int(subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                                              "stream=nb_read_frames", "-of", "csv=p=0", out]).decode().strip())
            print(f"{sid}: {out} frames {nf}/{n}  svg {t1 - t0:.0f}s render {time.time() - t1:.0f}s")
            if "--contact" in args or True:
                cs = os.path.join(BASE_TMP, "sheets")
                os.makedirs(cs, exist_ok=True)
                subprocess.call(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-vf", "fps=6,scale=270:-1,tile=6x2", "-frames:v", "1",
                                 os.path.join(cs, f"{sid}_contact.jpg")])
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
