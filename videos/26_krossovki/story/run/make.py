"""Рендер клипа s16 (сцена run): python3 make.py → ../clips/s16.mp4 по контракту брифа
(1080×1920, 30 к/с, H.264 CRF 16, yuv420p; кадр k = max(0, t0−0.2) + k/30, до t1+0.2).
SVG — Python (4 процесса), растр — Chromium (render.js, 4 процесса), PNG потоком в ffmpeg."""
import json, os, shutil, subprocess, sys, tempfile, time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOTS = {s["id"]: s for s in SH["shots"]}
TMP = "/tmp/claude-0/-home-user/7605bd81-268a-5536-b1b7-f9696ca784cb/scratchpad/run26/tmp"
SID = "s16"


def span():
    s = SHOTS[SID]
    a = max(0.0, s["t0"] - SH["pad"])
    b = s["t1"] + SH["pad"]
    return a, int(round((b - a) * 30))


def _job(args):
    sys.path.insert(0, HERE)
    import scene
    t, path = args
    open(path, "w").write(scene.frame(t))
    return path


def main():
    a, n = span()
    os.makedirs(TMP, exist_ok=True)
    tmp = tempfile.mkdtemp(dir=TMP, prefix=SID + "_")
    t0 = time.time()
    jobs = [(a + k / 30, os.path.join(tmp, f"f{k:04d}.svg")) for k in range(n)]
    with Pool(4) as p:
        svgs = p.map(_job, jobs, chunksize=2)
    t1 = time.time()
    open(os.path.join(tmp, "list.txt"), "w").write("\n".join(svgs))
    pre = os.path.join(tmp, "seg")
    subprocess.check_call(["node", os.path.join(HERE, "render.js"), os.path.join(tmp, "list.txt"), "mp4", "4", pre])
    segs = sorted(x for x in os.listdir(tmp) if x.startswith("seg_") and x.endswith(".mp4"))
    open(os.path.join(tmp, "concat.txt"), "w").write("".join(f"file '{os.path.join(tmp, s)}'\n" for s in segs))
    os.makedirs(os.path.join(STORY, "clips"), exist_ok=True)
    out = os.path.join(STORY, "clips", f"{SID}.mp4")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "concat.txt"),
                           "-c", "copy", "-movflags", "+faststart", out])
    nf = subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                                  "stream=nb_read_frames", "-of", "csv=p=0", out]).decode().strip()
    print(f"{SID}: {out} frames {nf}/{n} svg {t1 - t0:.0f}s render {time.time() - t1:.0f}s", flush=True)
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
