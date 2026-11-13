"""Рендер клипов сцен floor (s04, s10) и cat (s17, s18) рилса 33: python3 make.py s04 [s10 ...] → ../clips/<id>.mp4
по контракту брифа (1080×1920, 30 к/с, H.264 CRF 16, yuv420p, без звука; кадр k = max(0, t0−0.2) + k/30, до t1+0.2,
s18 — до 29.3). SVG — Python (2 процесса), растр — Chromium (render.js, 2 процесса), PNG потоком в ffmpeg."""
import importlib, json, os, shutil, subprocess, sys, tempfile, time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOTS = {s["id"]: s for s in SH["shots"]}
TMP = "/tmp/claude-0/-home-user-Generator-Stickman/3278a4d9-cb41-5e94-b012-deb7a6d0155a/scratchpad/s33/floor_tmp"
NP = 2


def span(sid):
    s = SHOTS[sid]
    a = max(0.0, s["t0"] - SH["pad"])
    b = min(s["t1"] + SH["pad"], SH["end"])
    return a, int(round((b - a) * 30))


def _job(args):
    sys.path.insert(0, HERE)
    sid, t, path = args
    open(path, "w").write(importlib.import_module(sid).frame(t))
    return path


def make(sid):
    a, n = span(sid)
    os.makedirs(TMP, exist_ok=True)
    tmp = tempfile.mkdtemp(dir=TMP, prefix=sid + "_")
    t0 = time.time()
    jobs = [(sid, a + k / 30, os.path.join(tmp, f"f{k:04d}.svg")) for k in range(n)]
    with Pool(NP) as p:
        svgs = p.map(_job, jobs, chunksize=2)
    t1 = time.time()
    open(os.path.join(tmp, "list.txt"), "w").write("\n".join(svgs))
    pre = os.path.join(tmp, "seg")
    subprocess.check_call(["node", os.path.join(HERE, "render.js"), os.path.join(tmp, "list.txt"), "mp4", str(NP), pre])
    segs = sorted(x for x in os.listdir(tmp) if x.startswith("seg_") and x.endswith(".mp4"))
    open(os.path.join(tmp, "concat.txt"), "w").write("".join(f"file '{os.path.join(tmp, s)}'\n" for s in segs))
    os.makedirs(os.path.join(STORY, "clips"), exist_ok=True)
    out = os.path.join(STORY, "clips", f"{sid}.mp4")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "concat.txt"),
                           "-c", "copy", "-movflags", "+faststart", out])
    nf = subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                                  "stream=nb_read_frames", "-of", "csv=p=0", out]).decode().strip()
    print(f"{sid}: {out} frames {nf}/{n} svg {t1 - t0:.0f}s render {time.time() - t1:.0f}s", flush=True)
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    for sid in sys.argv[1:]:
        make(sid)
