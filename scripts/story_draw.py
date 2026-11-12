"""Рисунки рилса-истории (формат «история человека», владелец 12.11: цветной мультяшный мир на весь экран, герой —
человек, наш кот дополнительно). Не reel_draw: там кремовая бумага и тушь, здесь — цветной рисунок с контуром.

    python scripts/story_draw.py videos/NN/story [--only sheet] [--dry]

<dir>/draw.json:
    {"jobs": {"sheet": {"scene": "...", "refs": ["cat"]},
              "s1_night": {"scene": "...", "refs": ["sheet", "cat"]}}}
refs: "style:<путь>" — образец стиля (только манера рисунка), "cat" — эталон кота (look/hero.png), "sheet" или любое имя готового рисунка из gen/ — лист персонажей и сцены,
путь — любой файл. Рисунок с готовым файлом не перерисовывается (деньги); каждый — в library/cat через шлюз.
"""
import argparse
import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import reel_draw  # noqa: E402  (цена, модель, предел цены, телефон — общие с рилсами)

STYLE = ("Style: modern adult animated TV series look, flat 2D cel animation, clean confident black outlines of even "
         "weight, simple flat colours with one soft cel shadow tone, expressive cartoon faces with big white eyes and small "
         "pupils, slightly tired relatable characters; backgrounds are richly detailed and lived-in, painted with soft "
         "texture and warm natural light, believable everyday objects. Full-bleed vertical frame filled edge to edge, no "
         "border, no paper margin.")
CLEAN = ("Every surface is clean and unmarked: no letters, numbers, logos or writing anywhere — blank screens, blank "
         "clock faces, blank book covers, plain walls.")


def cat_marks():
    marks = open(os.path.join(ROOT, "look", "hero_marks.txt"), encoding="utf8").read().strip()
    return ("The black cat is the cat from its reference image, redrawn in this cartoon style: same black fur, big green "
            "eyes, orange stripes on the cheeks, a small orange flame burning on the tip of its curled tail. " + marks)


def ref_path(d, r):
    if r == "cat":
        return os.path.join(ROOT, "look", "hero.png")
    if r.startswith("style:"):
        return r[6:]
    p = os.path.join(d, "gen", r + ".png")
    return p if os.path.exists(p) else os.path.normpath(os.path.join(d, r))


def prompt(job, refs):
    scene = job["scene"]
    if "phone" in scene.lower():
        scene = scene.rstrip() + " " + reel_draw.PHONE
    roles = []
    for i, r in enumerate(refs, 1):
        if r.startswith("style:"):
            roles.append(f"Reference image {i} shows only the drawing style: copy its line work, flat colours, cel "
                         "shading, way of drawing faces and eyes, textured detailed backgrounds and lighting; never its "
                         "characters, people, objects, writing or layout.")
        elif r == "cat":
            roles.append(f"Reference image {i} is the black cat character: keep its identity, change only style, pose "
                         "and expression.")
        elif r == "sheet":
            roles.append(f"Reference image {i} is the character sheet: draw every character exactly as designed there "
                         "(faces, hair, clothes, proportions, colours) and in exactly that drawing style.")
        else:
            roles.append(f"Reference image {i} is an earlier frame of the same film: keep its drawing style and "
                         "characters.")
    cat = (" " + cat_marks()) if "cat" in scene.lower() else ""
    return " ".join(roles) + f" SCENE: {scene}{cat} {STYLE} {CLEAN} Keep the main subject well inside the frame."


def draw(d, dry=False, only=None, max_price=None):
    cfg = json.load(open(os.path.join(d, "draw.json"), encoding="utf8"))
    out = os.path.join(d, "gen"); os.makedirs(out, exist_ok=True)
    todo = {k: v for k, v in cfg["jobs"].items()
            if not os.path.exists(os.path.join(out, k + ".png")) and (not only or k in only)}
    M, SIZE, Q = reel_draw.MODEL, reel_draw.SIZE, reel_draw.QUALITY
    import env; env.load_env()
    import llm_gateway
    try:
        price1 = llm_gateway.Gateway().image_cost(M, SIZE, Q)
    except Exception as e:
        print(f"  цена из каталога недоступна ({e})"); price1 = reel_draw.PRICE
    print(f"рисунков к заказу {len(todo)}, {M} {Q} {SIZE}: {price1:_} за рисунок, всего {price1 * len(todo):_}"
          .replace("_", " "))
    if dry or not todo:
        for k, v in todo.items():
            print(f"--- {k}\n{prompt(v, v.get('refs', []))}")
        return []
    if price1 > (max_price or reel_draw.MAX_PRICE):
        raise SystemExit(f"не заказываю: {price1} за рисунок выше предела — другая модель или --max-price со словом владельца")
    G = llm_gateway.Gateway(spend_cap=int(price1 * len(todo) * 1.05))
    for k, job in todo.items():
        refs = job.get("refs", [])
        paths = [ref_path(d, r) for r in refs]
        imgs = ["data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode() for p in paths]
        pr = prompt(job, refs)
        ims, price = G.image(M, pr, SIZE, Q, images=imgs or None, timeout=600)
        p = os.path.join(out, k + ".png"); open(p, "wb").write(ims[0])
        json.dump({"prompt": pr, "model": M, "quality": Q, "size": SIZE, "price": price,
                   "refs": [os.path.relpath(x, ROOT) for x in paths]},
                  open(os.path.join(out, k + ".json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
        print(f"  {k}: {price:_}".replace("_", " ") + f" -> {os.path.relpath(p, ROOT)}")
    print(json.dumps(G.summary(), ensure_ascii=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dir"); ap.add_argument("--dry", action="store_true")
    ap.add_argument("--only", nargs="*"); ap.add_argument("--max-price", type=int)
    a = ap.parse_args()
    draw(a.dir, a.dry, a.only, a.max_price)
