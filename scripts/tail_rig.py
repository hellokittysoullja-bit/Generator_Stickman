"""Гибкая часть персонажа (хвост, ухо) для сцен на HyperFrames: сетка с цепочкой костей и физика.

Владелец 02.11 (было/стало хвоста рилса 13: «стало лучше»): хвост не поворачивается палкой, а гнётся дугой — сетка
из треугольников, веса по длине хвоста, цепочка из 8 костей (линейный скиннинг); углы суставов считает физика pymunk:
основание машет и хлещет на ударе, остальные звенья висят на пружинах и догоняют с запаздыванием, движение тела кота
входит как сила инерции. Рисует сетку на холсте композиции scripts/hf_lib/mesh_part.js, размытие движения — своё
(HyperFrames содержимое холста не размывает, проверено 02.11).

Шаги: split_flame (огонёк отдельно: иначе цепочка уходит в него) → build_mesh → extract_motion (как тело несёт часть:
мировая матрица родителя по таймлайну композиции, Chromium) → simulate (углы на 240 Гц) → JSON в assets композиции."""
import collections
import json
import math
import os
import subprocess

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
HZ = 240
# физика, подобранная на хвосте рилса 13 (02.11): при ходьбе ≤ 7° на сустав, на ударе хлёст без поломки суставов
PHYS = dict(stiff=1e7, damp=1.5e5, limit_deg=18.0, inertia=0.4, wag_deg=7.0, wag_period=0.72, whip_deg=12.0,
            whip_decay=0.22, whip_period=0.45)


def split_flame(rgba, sat_min=60, bright_min=120):
    """Огонёк на кончике отдельно от хвоста: (хвост RGBA, огонёк RGBA, {xy: левый верх огонька, base: основание})."""
    import cv2
    im = np.asarray(rgba, np.float32)
    rgb, a = im[..., :3], im[..., 3]
    fl = (((rgb.max(2) - rgb.min(2)) > sat_min) & (rgb.mean(2) > bright_min) & (a > 30)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(fl)
    if n <= 1:
        return np.asarray(rgba), None, None
    fl = (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    ys, xs = np.where(fl)
    y_base = int(ys.max()); x0, x1 = int(xs.min()) - 12, int(xs.max()) + 12
    reg = np.zeros_like(fl); reg[:max(0, y_base - 4), max(0, x0):x1] = 1
    m = cv2.GaussianBlur(((a > 8) & (reg > 0)).astype(np.float32), (0, 0), 1.0)
    tail = np.dstack([rgb, a * (1 - m)]).clip(0, 255).astype(np.uint8)
    flame = np.dstack([rgb, a * m]).clip(0, 255).astype(np.uint8)[:y_base + 4, max(0, x0):x1]
    return tail, flame, dict(xy=[max(0, x0), 0], base=[int((xs.min() + xs.max()) / 2), y_base])


def build_mesh(rgba, attach, bones=8, step=8):
    """Сетка и веса части: ось — самый длинный путь скелета силуэта, основание — конец ближе к attach (x, y);
    параметр длины разносится по маске поиском в ширину (не перескакивает через просвет завитка), ячейки через
    просвет отбрасываются. Возвращает {W, H, bones: [опоры], tip, verts: [x, y, b0, b1, w0, w1], idx}."""
    from skimage.morphology import skeletonize
    im = np.asarray(rgba)
    H, W = im.shape[:2]
    a = im[..., 3]
    mask = ndi.binary_opening(a > 40, iterations=2)
    lab, n = ndi.label(mask)
    mask = lab == (1 + int(np.argmax(ndi.sum(mask, lab, range(1, n + 1)))))
    sk = skeletonize(ndi.gaussian_filter(mask.astype(float), 6) > 0.5)
    pts = set(zip(*np.nonzero(sk)))

    def nb(p):
        y, x = p
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                q = (y + dy, x + dx)
                if q != p and q in pts:
                    yield q

    def bfs(s):
        d, par, Q = {s: 0}, {s: None}, collections.deque([s])
        while Q:
            p = Q.popleft()
            for q in nb(p):
                if q not in d:
                    d[q] = d[p] + 1; par[q] = p; Q.append(q)
        return max(d, key=d.get), par

    e1, _ = bfs(min(pts))
    e2, par = bfs(e1)
    path, p = [], e2
    while p is not None:
        path.append(p); p = par[p]
    path = np.array(path, float)
    ax, ay = attach
    if math.hypot(path[0][1] - ax, path[0][0] - ay) > math.hypot(path[-1][1] - ax, path[-1][0] - ay):
        path = path[::-1]
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(path, axis=0).T))]
    L = seg[-1]
    S = -np.ones((H, W)); Q = collections.deque()
    for (y, x), s in zip(path.astype(int), seg / L):
        S[y, x] = s; Q.append((y, x))
    while Q:
        y, x = Q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and mask[yy, xx] and S[yy, xx] < 0:
                S[yy, xx] = S[y, x]; Q.append((yy, xx))
    _, (iy, ix) = ndi.distance_transform_edt(S < 0, return_indices=True)
    Sf = S[iy, ix]
    piv = [path[np.searchsorted(seg / L, s)][::-1].tolist() for s in np.linspace(0, 1, bones + 1)[:-1]]

    def weights(s):
        k = min(int(s * bones), bones - 1); t = s * bones - k
        return [(k, 1.0)] if k == bones - 1 else [(k, 1 - t), (k + 1, t)]

    occ = ndi.binary_dilation(a > 2, iterations=step)
    gx = np.arange(0, W + step, step); gy = np.arange(0, H + step, step)
    vid, V, idx = {}, [], []

    def v(i, j):
        if (i, j) not in vid:
            x, y = min(gx[j], W - 1), min(gy[i], H - 1)
            vid[(i, j)] = len(V); V.append((float(gx[j]), float(gy[i]), float(Sf[y, x])))
        return vid[(i, j)]
    for i in range(len(gy) - 1):
        for j in range(len(gx) - 1):
            if not occ[gy[i]:gy[i + 1], gx[j]:gx[j + 1]].any():
                continue
            q = [v(i, j), v(i, j + 1), v(i + 1, j), v(i + 1, j + 1)]
            ss = [V[k][2] for k in q]
            if max(ss) - min(ss) > 1.5 / bones:                 # ячейка через просвет завитка соединяла бы разные витки
                continue
            idx += [q[0], q[1], q[2], q[1], q[3], q[2]]
    verts = []
    for x, y, s in V:
        w = weights(s) + [(0, 0.0)]
        verts.append([x, y, w[0][0], w[1][0], w[0][1], w[1][1]])
    return dict(W=W, H=H, bones=piv, tip=path[-1][::-1].tolist(), verts=verts, idx=idx)


def extract_motion(project_dir, element_id, dur, hz=HZ):
    """Мировая матрица РОДИТЕЛЯ элемента по таймлайну композиции (как тело несёт часть): [[a, b, c, d, e, f], …] на hz.
    Композиция открывается в Chromium (Playwright из Node), таймлайн перематывается (window.__timelines.main)."""
    project_dir = os.path.abspath(project_dir)                      # file:// нужен абсолютный путь (сборщик даёт относительный)
    out = os.path.join(project_dir, ".motion.json")
    env = dict(os.environ, NODE_PATH=os.environ.get("NODE_PATH", "/opt/node22/lib/node_modules"))
    r = subprocess.run(["node", os.path.join(HERE, "hf_lib", "extract_motion.js"), os.path.join(project_dir, "index.html"),
                    element_id, out, str(hz), str(dur)], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"движение части не снялось: {(r.stdout + r.stderr)[-800:]}")
    m = json.load(open(out)); os.remove(out)
    return m


def wag(t, hit, p=PHYS):
    """Мах основания (рад): ровный мах плюс хлёст на ударе с затуханием."""
    w = math.radians(p["wag_deg"]) * math.sin(2 * math.pi * t / p["wag_period"])
    if hit is not None and t >= hit:
        u = t - hit
        w += math.radians(p["whip_deg"]) * math.exp(-u / p["whip_decay"]) * math.sin(2 * math.pi * u / p["whip_period"] + 0.5)
    return w


def simulate(mesh, motion, offset, hit, dur, p=PHYS, hz=HZ, sub=8):
    """Углы суставов (локальные, рад) на hz. Цепочка живёт в системе слоя части, основание неподвижно и машет пружиной;
    движение тела входит силой инерции (−ускорение точки крепления). offset — место слоя части в слое родителя."""
    import pymunk
    piv = [tuple(q) for q in mesh["bones"]] + [tuple(mesh["tip"])]
    OX, OY = offset

    def M(i):
        return motion[min(len(motion) - 1, max(0, i))]

    def world(i):
        a, b, c, d, e, f = M(i); x, y = piv[0][0] + OX, piv[0][1] + OY
        return (a * x + c * y + e, b * x + d * y + f)

    def acc_local(i):
        ax = ay = 0.0
        for j in range(i - 2, i + 3):
            p0, p1, p2 = world(j - 1), world(j), world(j + 1)
            ax += (p2[0] - 2 * p1[0] + p0[0]) * hz * hz / 5; ay += (p2[1] - 2 * p1[1] + p0[1]) * hz * hz / 5
        a, b, c, d, _, _ = M(i); det = a * d - b * c
        return ((d * ax - c * ay) / det, (-b * ax + a * ay) / det)

    space = pymunk.Space(); space.damping = 0.5
    anchor = pymunk.Body(body_type=pymunk.Body.STATIC)
    bodies, rest = [], []
    for k in range(len(piv) - 1):
        (x0, y0), (x1, y1) = piv[k], piv[k + 1]
        L = math.hypot(x1 - x0, y1 - y0); mass = L / 60 * (1.2 - 0.08 * k)
        b = pymunk.Body(mass, pymunk.moment_for_segment(mass, (-L / 2, 0), (L / 2, 0), 6))
        b.position = ((x0 + x1) / 2, (y0 + y1) / 2); b.angle = math.atan2(y1 - y0, x1 - x0)
        sh = pymunk.Segment(b, (-L / 2, 0), (L / 2, 0), 4); sh.filter = pymunk.ShapeFilter(group=1)
        space.add(b, sh); bodies.append(b); rest.append(b.angle)
    space.add(pymunk.PivotJoint(anchor, bodies[0], piv[0]))
    base = pymunk.DampedRotarySpring(anchor, bodies[0], -rest[0], p["stiff"] * 1.5, p["damp"] * 1.5)
    space.add(base)
    lim = math.radians(p["limit_deg"])
    for k in range(1, len(bodies)):
        a, b = bodies[k - 1], bodies[k]
        space.add(pymunk.PivotJoint(a, b, piv[k]))
        r = rest[k - 1] - rest[k]                          # у пружины chipmunk угол a − b, у предела — b − a
        space.add(pymunk.DampedRotarySpring(a, b, r, p["stiff"] * (1 - 0.07 * k), p["damp"] * (1 - 0.05 * k)))
        space.add(pymunk.RotaryLimitJoint(a, b, -r - lim, -r + lim))
    out = []
    for i in range(int(dur * hz) + 1):
        t = i / hz
        ax, ay = acc_local(i)
        space.gravity = (-p["inertia"] * ax, -p["inertia"] * ay)
        base.rest_angle = -(rest[0] + wag(t, hit, p))
        out.append([round(bodies[0].angle - rest[0], 5)] +
                   [round((bodies[k].angle - bodies[k - 1].angle) - (rest[k] - rest[k - 1]), 5) for k in range(1, len(bodies))])
        for _ in range(sub):
            space.step(1 / hz / sub)
    return dict(hz=hz, angles=out)


def prepare_part(layer_png, attach, out_dir, name="tail", bones=8):
    """Слой части → в out_dir: <name>_body.png, <name>_flame.png (если есть), <name>_mesh.json. Возвращает мету."""
    rgba = np.asarray(Image.open(layer_png).convert("RGBA"))
    body, flame, fl = split_flame(rgba)
    Image.fromarray(body).save(os.path.join(out_dir, f"{name}_body.png"))
    meta = dict(flame=None)
    if flame is not None:
        Image.fromarray(flame).save(os.path.join(out_dir, f"{name}_flame.png"))
        meta["flame"] = fl
    mesh = build_mesh(body, attach, bones=bones)
    json.dump(dict(mesh, flame=meta["flame"]), open(os.path.join(out_dir, f"{name}_mesh.json"), "w"))
    return mesh
