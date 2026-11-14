"""Рендер клипов сцены dima рилса 35: python3 make.py s05 s06 s14 s16 → ../clips/<id>.mp4 по контракту брифа
(1080×1920, 30 к/с, H.264 CRF 16, yuv420p; кадр k = max(0, t0−0.2) + k/30, до t1+0.2).
Лист кадров: python3 make.py --sheet SID t1,t2,... [out.jpg] [crop x0,y0,x1,y1|-] [scale].
SVG — Python, растр — Chromium (render.js), PNG потоком в ffmpeg. NP процессов (по умолчанию 1: ядра делят агенты).
Временные файлы — EXT_TMP (по умолчанию скретчпад сессии)."""
import json, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOTS = {s["id"]: s for s in SH["shots"]}
TMP = os.environ.get("EXT_TMP", "/tmp/claude-0/-home-user-Generator-Stickman/0eafb5b9-7bf4-521b-b107-93aaca4e7865/scratchpad/desk_tmp")
NP = int(os.environ.get("NP", "1"))
sys.path.insert(0, HERE)


def span(sid):
    s = SHOTS[sid]
    a = max(0.0, s["t0"] - SH["pad"])
    b = min(s["t1"] + SH["pad"], SH["end"])
    return a, int(round((b - a) * 30))


def render(sid):
    import scene
    a, n = span(sid)
    os.makedirs(TMP, exist_ok=True)
    tmp = tempfile.mkdtemp(dir=TMP, prefix=sid + "_")
    t0 = time.time()
    svgs = []
    for k in range(n):
        p = os.path.join(tmp, f"f{k:04d}.svg")
        open(p, "w").write(scene.frame(sid, a + k / 30))
        svgs.append(p)
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


def sheet(argv):
    from PIL import Image
    import importlib
    mod = importlib.import_module(os.environ.get("SCENE", "scene"))
    sid = argv[0]
    times = [float(x) for x in argv[1].split(",")]
    os.makedirs(TMP, exist_ok=True)
    out = argv[2] if len(argv) > 2 else os.path.join(TMP, f"sheet_{sid}.jpg")
    crop = argv[3] if len(argv) > 3 and argv[3] != "-" else None
    sc = float(argv[4]) if len(argv) > 4 else (1.0 if crop else 0.36)
    d = tempfile.mkdtemp(dir=TMP)
    lst = []
    for i, t in enumerate(times):
        p = os.path.join(d, f"f{i}.svg")
        open(p, "w").write(mod.frame(sid, t))
        lst.append(f"{p}\t{os.path.join(d, f'f{i}.png')}")
    open(os.path.join(d, "l.txt"), "w").write("\n".join(lst))
    subprocess.check_call(["node", os.path.join(HERE, "render.js"), os.path.join(d, "l.txt"), "png", "1", "x"])
    ims = [Image.open(os.path.join(d, f"f{i}.png")).convert("RGB") for i in range(len(times))]
    if crop:
        x0, y0, x1, y1 = map(int, crop.split(","))
        ims = [im.crop((x0, y0, x1, y1)) for im in ims]
    ims = [im.resize((int(im.width * sc), int(im.height * sc))) for im in ims]
    n = len(ims)
    cols = min(n, 6)
    rows = (n + cols - 1) // cols
    W, H = ims[0].width, ims[0].height
    o = Image.new("RGB", (W * cols, H * rows), "white")
    for i, im in enumerate(ims):
        o.paste(im, ((i % cols) * W, (i // cols) * H))
    o.save(out, quality=90)
    shutil.rmtree(d)
    print(out)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--sheet"]:
        sheet(sys.argv[2:])
    else:
        for sid in (sys.argv[1:] or ["s05", "s06", "s14", "s16"]):
            render(sid)
