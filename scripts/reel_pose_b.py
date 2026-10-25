"""Рисунок-поза Б для движения внутри рисунка (25.10): та же сцена, что рисунок А, меняется только поза или лицо —
кадр «после удара», в который сцена anim.py переходит на ударе (скилл reel-anim). GPT-Image-2 medium, 140 625 за
рисунок; новые платные рисунки — только со слова владельца.

    python scripts/reel_pose_b.py videos/NN/reel          # рисует то, чего нет, по reel/pose_b.json
    python scripts/reel_pose_b.py videos/NN/reel --dry    # только промпты и цена

reel/pose_b.json:  {"gen/n6_phone_fell.png": {"from": "gen/n5_bed_side.png", "change": "the phone has slipped ..."}}

`change` — одно изменение по-английски, видимым состоянием («lies flat on its face, covering its eyes»), а не
глаголом действия. После — проверить совмещение с А: cv2.phaseCorrelate по краю рисунка, сдвиг ≤ 2 px (иначе на
ударе прыгнет весь фон), и глазами — тот ли кот (ухо, полоски, огонёк).
"""
import argparse
import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL, SIZE, QUALITY, PRICE = "cx/gpt-image-2", "1536x1024", "medium", 140625


def data_url(p):
    return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()


def prompt(change):
    marks = open(os.path.join(ROOT, "look", "hero_marks.txt"), encoding="utf8").read().strip()
    return ("Image 1 is a finished frame of an animation. Draw the very next key frame of the same shot: exactly the same camera angle, "
            "framing, scale, room, bed or floor, background, colors, line work, paper and lighting as image 1, and the same main character "
            "in the same place and size. Image 2 is the main character's reference: keep exactly its head, face, colors and markings. "
            + marks + " The only change from image 1: " + change + " Everything else stays exactly as in image 1. Every surface is clean "
            "and unmarked: blank paper, blank screens, plain envelopes.")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("reel_dir"); ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    jobs = json.load(open(os.path.join(a.reel_dir, "pose_b.json"), encoding="utf8"))
    todo = {k: v for k, v in jobs.items() if not os.path.exists(os.path.join(a.reel_dir, k))}
    for out, j in todo.items():
        print(out, "<-", j["from"], "\n ", prompt(j["change"])[:300], "…")
    print(f"рисунков: {len(todo)}, цена ≈ {PRICE * len(todo)}")
    if a.dry or not todo:
        return
    import env; env.load_env()
    import llm_gateway
    G = llm_gateway.Gateway(spend_cap=int(PRICE * len(todo) * 1.05))
    hero = os.path.join(ROOT, "look", "hero.png")
    for out, j in todo.items():
        p = prompt(j["change"])
        ims, price = G.image(MODEL, p, SIZE, QUALITY, images=[data_url(os.path.join(a.reel_dir, j["from"])), data_url(hero)], timeout=600)
        dst = os.path.join(a.reel_dir, out)
        open(dst, "wb").write(ims[0])
        json.dump({"prompt": p, "model": MODEL, "quality": QUALITY, "size": SIZE, "price": price,
                   "refs": [j["from"], "look/hero.png"], "pose_of": j["from"]},
                  open(dst[:-4] + ".json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
        print(out, price)


if __name__ == "__main__":
    main()
