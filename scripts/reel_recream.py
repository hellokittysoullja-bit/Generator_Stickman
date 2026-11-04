"""Цветной рисунок рилса → тот же рисунок на кремовой бумаге (владелец 04.11: «фон должен быть как везде — кремовый,
бумага»; цветными остаются кот и предметы, а не стены и пол). Модель получает сам рисунок (образец кадра) и героя и
перерисовывает тот же кадр: та же композиция, крупность и место каждого предмета (окна монтажа и слои хука уже
рассчитаны по нему), а комнатная заливка стен и пола уходит в чистую кремовую бумагу.

    python scripts/reel_recream.py videos/NN/reel gen/d1_clock.png [ещё…] [--dry]

Исходник с цветной стеной сохраняется в gen/room/<имя>.png (в кадр он больше не идёт), новый ложится на его место;
оригиналы модели и так лежат в library/cat/originals. Модель и предел цены — как у reel_draw.py (REEL_DRAW_MODEL,
REEL_DRAW_MAX_PRICE)."""
import argparse
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reel_draw  # noqa: E402

ROOT = reel_draw.ROOT
BACKGROUND = ("Background: plain warm cream paper (#FAF7F0) everywhere around the figures, exactly like a blank sheet of "
              "drawing paper: no painted wall, no wall colour, no wallpaper, no floorboards or wood grain, no room corners; "
              "where something stands on the floor there is only one thin simple ink floor line or a soft light-grey shadow "
              "under it, the rest of the floor area is the same blank cream paper.")
COLOURS = ("Colours: black ink lines on cream paper in exactly the hand-drawn style of image 1; the main character and the "
           "objects (furniture, clock, clothes, shoes, bags, door, things in the paws) keep their soft watercolour colours "
           "from image 1, gentle and muted, never neon; only the background is uncoloured cream paper. The main character "
           "stays black with green eyes, orange cheek marks and an orange tail flame.")


def prompt(extra=""):
    marks = open(os.path.join(ROOT, "look", "hero_marks.txt"), encoding="utf8").read().strip()
    return ("Image 1 is a finished drawing. Redraw exactly the same drawing: the same composition, framing, camera angle, "
            "scale, and the same position, size, pose and expression of the main character and of every object, the same "
            "line work. Image 2 is the main character's reference: keep exactly its head, face, colours and markings. "
            + marks + " The only change from image 1: " + BACKGROUND + " " + (extra + " " if extra else "") + COLOURS + " Every surface is clean and "
            "unmarked: blank paper, blank screens, blank clock faces, no letters or numbers anywhere.")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("reel_dir"); ap.add_argument("files", nargs="+")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--extra", default="", help="уточнение к фону для этого рисунка (что ещё убрать: пол, окно…)")
    a = ap.parse_args()
    import env; env.load_env()
    import llm_gateway
    G = llm_gateway.Gateway(spend_cap=int(reel_draw.MAX_PRICE * len(a.files) * 1.05))
    price = G.image_cost(reel_draw.MODEL, reel_draw.SIZE, reel_draw.QUALITY)
    print(f"{reel_draw.MODEL} {reel_draw.QUALITY} {reel_draw.SIZE}: {price} за рисунок, рисунков {len(a.files)}")
    if price > reel_draw.MAX_PRICE:
        raise SystemExit(f"цена {price} > {reel_draw.MAX_PRICE}")
    if a.dry:
        print(prompt(a.extra)); return
    hero = os.path.join(ROOT, "look", "hero.png")
    for rel in a.files:
        src = os.path.join(a.reel_dir, rel)
        keep = os.path.join(a.reel_dir, "gen", "room", os.path.basename(rel))
        os.makedirs(os.path.dirname(keep), exist_ok=True)
        if not os.path.exists(keep):
            shutil.copy2(src, keep)
        p = prompt(a.extra)
        ims, paid = G.image(reel_draw.MODEL, p, reel_draw.SIZE, reel_draw.QUALITY,
                            images=[reel_draw.data_url(keep), reel_draw.data_url(hero)], timeout=600)
        open(src, "wb").write(ims[0])
        json.dump({"prompt": p, "model": reel_draw.MODEL, "quality": reel_draw.QUALITY, "size": reel_draw.SIZE,
                   "price": paid, "refs": [os.path.relpath(keep, a.reel_dir), "look/hero.png"], "recream_of": rel},
                  open(src[:-4] + ".json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
        print(rel, paid, flush=True)


if __name__ == "__main__":
    main()
