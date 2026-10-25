"""Свои рисунки рилса — недостающие кадры к фразам (23.10, владелец: рилс не должен быть нарезкой одних и тех же
кадров эпизода; новые картинки — GPT-Image-2 medium через шлюз, 140 625 баланса за кадр 1536×1024).

    python scripts/reel_draw.py videos/NN/reel              # рисует то, чего ещё нет в reel/gen/, по reel/draw.json
    python scripts/reel_draw.py videos/NN/reel --dry        # только промпты и цена, без вызова

reel/draw.json:
    {"style_refs": ["../frames/004.png"],                 # необязательно: кадр эпизода как ещё один образец стиля
     "jobs": {"r1_phone": "medium shot: the main character sits ..., LAYOUT: ..."}}

Промпт — тот же порядок, что у кадров длинных роликов (CLAUDE.md, «Промпт картинки»): роли референсов первыми
(образцы — только стиль, последний — главный герой), приметы героя (look/hero_marks.txt), `SCENE:`, `LAYOUT:` от
автора, фон, палитра (look/palette.txt), «каждая поверхность чистая» вместо списка запретов, стиль — короткой ссылкой
в конце. Рисунок с готовым файлом не перерисовывается (деньги). Рядом с картинкой — .json с промптом и ссылками.
После — посмотреть глазами: буквы на поверхностях, тот ли кот (ухо, полоски, огонёк), стиль как у кадров эпизода.
Строка в reel_script.txt: `@f6 = gen/r1_phone.png`.
"""
import argparse
import base64
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL, SIZE, QUALITY, PRICE = "cx/gpt-image-2", "1024x1792", "medium", 164063   # 9:16 — рисунки рилсов вертикальные (владелец 26.10)


def data_url(p):
    return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()


def prompt(scene, n_style):
    marks = open(os.path.join(ROOT, "look", "hero_marks.txt"), encoding="utf8").read().strip()
    palette = open(os.path.join(ROOT, "look", "palette.txt"), encoding="utf8").read().strip()
    return (f"Reference images 1-{n_style} show only the drawing style: take from them the line work, colors, shading and "
            f"simplicity, never their content or characters. Reference image {n_style + 1} is the main character: keep "
            "exactly its head, face, colors, markings, body proportions; change only pose, action and expression. "
            f"{marks}. SCENE: {scene} If the picture has no specific place, its background is plain near-white paper, "
            f"even and untinted. {palette}. Every surface is clean and unmarked: blank paper, blank screens, plain "
            "envelopes, plain walls, unprinted floor. Keep the main subject well inside the frame, away from the edges. "
            "Draw everything in exactly the drawing style of the style references.")


def draw(reel_dir, dry=False):
    cfg = json.load(open(os.path.join(reel_dir, "draw.json"), encoding="utf8"))
    style = sorted(glob.glob(os.path.join(ROOT, "look", "style", "*.png")))
    style += [os.path.normpath(os.path.join(reel_dir, p)) for p in cfg.get("style_refs", [])]
    hero = os.path.join(ROOT, "look", "hero.png")
    out = os.path.join(reel_dir, "gen"); os.makedirs(out, exist_ok=True)
    todo = {k: v for k, v in cfg["jobs"].items() if not os.path.exists(os.path.join(out, k + ".png"))}
    print(f"рисунков к заказу {len(todo)} из {len(cfg['jobs'])}, цена {PRICE * len(todo):_} баланса".replace("_", " "))
    if dry or not todo:
        for k, v in todo.items(): print(f"--- {k}\n{prompt(v, len(style))}")
        return []
    import env; env.load_env()
    import llm_gateway
    G = llm_gateway.Gateway(spend_cap=int(PRICE * len(todo) * 1.05))
    refs = [data_url(p) for p in style + [hero]]
    made = []
    for k, scene in todo.items():
        pr = prompt(scene, len(style))
        ims, price = G.image(MODEL, pr, SIZE, QUALITY, images=refs, timeout=600)
        p = os.path.join(out, k + ".png"); open(p, "wb").write(ims[0]); made.append(p)
        json.dump({"prompt": pr, "model": MODEL, "quality": QUALITY, "size": SIZE, "price": price,
                   "refs": [os.path.relpath(x, ROOT) for x in style + [hero]]},
                  open(os.path.join(out, k + ".json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
        print(f"  {k}: {price:_}".replace("_", " ") + f" -> {os.path.relpath(p, ROOT)}")
    print(json.dumps(G.summary(), ensure_ascii=False))
    return made


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("reel_dir"); ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    draw(a.reel_dir, a.dry)
