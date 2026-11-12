"""Превью L02, вариант 1 «телефон экраном вниз — не помогает» (владелец 12.11: генерация без текста, наш рисованный
стиль, белый фон, понятно с первого взгляда, как превью «это Даня» с ✗ и ✓). Промпт — reel_draw (образцы стиля,
герой, приметы, палитра, телефон), размер 1536×1024 под 16:9.

    REEL_DRAW_MODEL=cx/gpt-image-2.5 python videos/L02_otvlechenie/thumb/draw_thumb.py
"""
import base64, glob, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import reel_draw, env, llm_gateway  # noqa: E402

SIZE = "1536x1024"
SCENE = ("A YouTube thumbnail split into two equal halves by one thin vertical ink line, white background. "
         "LEFT half: the main character sits at a small desk with an open laptop, but its whole head is turned away from "
         "the laptop, big worried eyes glancing sideways at a smartphone lying screen-down on the desk right next to the "
         "laptop; three short motion lines between its eyes and the phone show it keeps checking; above the left half a "
         "big bold hand-painted red X mark. RIGHT half: the same character at the same desk, same angle, calmly typing "
         "on the laptop with a focused small smile and its tail flame burning bright; there is no phone on this desk; in "
         "the background an open doorway, and far away in the next room the smartphone lies on a small table; above "
         "the right half a big bold hand-painted green check mark. The only difference between the halves is where the "
         "phone is. Characters large, filling each half, bold clean outlines, readable at a very small size.")


def main():
    env.load_env()
    style = sorted(glob.glob(os.path.join(ROOT, "look", "style", "*.png")))
    hero = os.path.join(ROOT, "look", "hero.png")
    out = os.path.dirname(os.path.abspath(__file__))
    pr = reel_draw.prompt(SCENE, len(style))
    M, Q = reel_draw.MODEL, reel_draw.QUALITY
    price1 = llm_gateway.Gateway().image_cost(M, SIZE, Q)
    print(f"{M} {Q} {SIZE}: {price1}")
    if price1 > reel_draw.MAX_PRICE:
        raise SystemExit("дороже предела, не заказываю")
    G = llm_gateway.Gateway(spend_cap=int(price1 * 1.05))
    refs = ["data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode() for p in style + [hero]]
    ims, price = G.image(M, pr, SIZE, Q, images=refs, timeout=600)
    n = len(glob.glob(os.path.join(out, "v1_*.png"))) + 1
    p = os.path.join(out, f"v1_{n}.png"); open(p, "wb").write(ims[0])
    json.dump({"prompt": pr, "model": M, "size": SIZE, "price": price}, open(p[:-4] + ".json", "w", encoding="utf8"),
              ensure_ascii=False, indent=1)
    print(price, p)


if __name__ == "__main__":
    main()
