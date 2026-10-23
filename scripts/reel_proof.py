"""Лист проверки рилса — ОДНА картинка вместо десятка кадров (23.10, решение владельца: экономить токены без потери
качества). Кадры готового reel.mp4 с субтитрами: 0.0 / 0.5 / 1.0 с хука, кадр за 2 кадра до первой склейки и сразу
после неё, середина каждого плана; на каждом — время и линии безопасных зон (верх 14% — шапка Reels, низ 400 px —
подпись и кнопки, Restream/Meta). Смотреть глазами один этот лист, а не кадры по одному: ~1.5 тыс. токенов против ~15.

    python scripts/reel_proof.py videos/NN/reel        # -> videos/NN/reel/proof.jpg (reel.py делает его сам)
"""
import json
import os
import subprocess
import sys

import cv2
import numpy as np

TILE_W, TILE_H, COLS = 180, 320, 9
TOP_SAFE, BOTTOM_UI, RIGHT_UI, SIDE = 0.14, 400 / 1920, 930 / 1080, 70 / 1080


def frame_at(video, t):
    out = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0.0, t):.3f}", "-i", video, "-frames:v", "1",
                          "-vf", f"scale={TILE_W}:{TILE_H}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    if len(out) != TILE_W * TILE_H * 3:
        return np.full((TILE_H, TILE_W, 3), 40, np.uint8)
    return np.frombuffer(out, np.uint8).reshape(TILE_H, TILE_W, 3).copy()


def moments(report):
    shots = report["shots"]
    ts = [(0.0, "0.0 хук"), (0.5, "0.5"), (1.0, "1.0")]
    if len(shots) > 1:
        c = shots[1]["t0"]; ts += [(c - 2 / 30, f"{c:.2f}-"), (c + 1 / 30, f"{c:.2f} склейка")]
    for i, s in enumerate(shots):
        m = (s["t0"] + s["t1"]) / 2
        ts.append((m, f"{i + 1}: {s['t0']:.1f}-{s['t1']:.1f} {s.get('src') or s.get('kind')}"))
    return ts


def seam(video, t, ph):
    """Шов картинки и полосы субтитров: перепад средней яркости строк над и под границей (код сводит их мягким краем)."""
    out = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", "-vf", "format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    if len(out) != 1080 * 1920:
        return None
    a = np.frombuffer(out, np.uint8).reshape(1920, 1080).astype(np.float32)
    return round(float(abs(a[ph - 10:ph].mean() - a[ph:ph + 10].mean())), 1)


def proof(reel_dir):
    report = json.load(open(os.path.join(reel_dir, "reel_report.json"), encoding="utf8"))
    video = os.path.join(reel_dir, "reel.mp4")
    ph = report.get("picture_h", 1380)
    tiles = []
    # без текста и в сером (план 04 п.1.7): хук работает одной картинкой; движение хука читается без цвета
    im = frame_at(video, 0.5); im[int(TILE_H * ph / 1920):] = im[int(TILE_H * ph / 1920) - 2:int(TILE_H * ph / 1920) - 1].mean(axis=(0, 1))
    cv2.rectangle(im, (0, TILE_H - 18), (TILE_W, TILE_H), (0, 0, 0), -1)
    cv2.putText(im, "0.5 без субтитра", (3, TILE_H - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (255, 255, 255), 1, cv2.LINE_AA)
    extra = [im]
    for t in (0.0, 0.5, 1.0, 1.5):
        g = cv2.cvtColor(cv2.cvtColor(frame_at(video, t), cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
        cv2.rectangle(g, (0, TILE_H - 18), (TILE_W, TILE_H), (0, 0, 0), -1)
        cv2.putText(g, f"{t:.1f} серый", (3, TILE_H - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (255, 255, 255), 1, cv2.LINE_AA)
        extra.append(g)
    for t, label in moments(report):
        im = frame_at(video, t)
        y0, y1 = int(TILE_H * TOP_SAFE), int(TILE_H * (1 - BOTTOM_UI))
        for y in (y0, y1):
            for x in range(0, TILE_W, 8): cv2.line(im, (x, y), (x + 4, y), (60, 60, 230), 1)
        for x in (int(TILE_W * SIDE), int(TILE_W * (1 - SIDE))):    # боковые поля 70 px (Restream)
            for y in range(y0, y1, 8): cv2.line(im, (x, y), (x, y + 3), (60, 160, 60), 1)
        xr = int(TILE_W * RIGHT_UI)                     # правая колонка кнопок Reels (лайк, комментарий, «отправить»)
        for y in range(int(TILE_H * 0.45), y1, 8): cv2.line(im, (xr, y), (xr, y + 4), (60, 60, 230), 1)
        cv2.rectangle(im, (0, TILE_H - 18), (TILE_W, TILE_H), (0, 0, 0), -1)
        cv2.putText(im, label[:30], (3, TILE_H - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (255, 255, 255), 1, cv2.LINE_AA)
        tiles.append(im)
    tiles += extra
    while len(tiles) % COLS: tiles.append(np.full((TILE_H, TILE_W, 3), 40, np.uint8))
    rows = [np.hstack(tiles[i:i + COLS]) for i in range(0, len(tiles), COLS)]
    sheet = np.vstack([np.vstack([r, np.full((4, r.shape[1], 3), 20, np.uint8)]) for r in rows])
    # шапка листа: цель рилса из паспорта (п.1.29) и шов картинки (п.1.7) — латиница/кириллица через PIL
    spec_p = os.path.join(reel_dir, "reel.json")
    goal = (json.load(open(spec_p, encoding="utf8")).get("passport") or {}).get("goal", {}) if os.path.exists(spec_p) else {}
    sm = [seam(video, (sh["t0"] + sh["t1"]) / 2, ph) for sh in report["shots"]]
    sm = [x for x in sm if x is not None]
    lines = [f"Вопрос зрителя: {goal.get('question', '—')}", f"Эмоция: {goal.get('emotion', '—')}",
             f"Шов картинки и субтитров (перепад яркости, макс по планам): {max(sm) if sm else '—'}"]
    from PIL import Image, ImageDraw, ImageFont
    head = Image.new("RGB", (sheet.shape[1], 30 * len(lines) + 10), (20, 20, 20)); d = ImageDraw.Draw(head)
    try:
        f = ImageFont.truetype("DejaVuSans.ttf", 20)
    except OSError:
        f = ImageFont.load_default()
    for i, ln in enumerate(lines): d.text((10, 6 + 30 * i), ln, fill=(240, 240, 240), font=f)
    sheet = np.vstack([np.asarray(head)[:, :, ::-1], sheet])
    out = os.path.join(reel_dir, "proof.jpg")
    cv2.imwrite(out, sheet, [cv2.IMWRITE_JPEG_QUALITY, 82])
    return out


if __name__ == "__main__":
    print(proof(sys.argv[1]))
