"""Вечерний план s10 рилса 25: Дима сидит на диване при торшере (герой и кот рилса 24 без изменений), берёт листок и
ручку — новая поза S: листок в левой руке на коленях, правая с ручкой опускается к листку.
Запуск: python3 heroes25e.py → heroes25e.html (анимация — template25e.html)."""
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import heroes24 as H  # noqa: E402
from heroes24 import shape, blob, line  # noqa: E402

_front24 = H.front_dima
SHEET = [(224, 1146, 1), (412, 1150, 1), (428, 1224, 1), (208, 1222, 1)]


def front25():
    s = [_front24()]
    s.append('<g id="pose_S" style="display:none">')
    s.append('<g id="sheet_g">')
    pc = H.clip_of(H.REG["plaid"])
    s.append(f'<g clip-path="url(#{pc})">' + blob([(206, 1156), (432, 1160), (440, 1236), (198, 1234)], "#0d160f", .5, H.blur(6)) + "</g>")
    s.append(shape(SHEET, "#f8f4ea", blob([(208, 1206), (428, 1208), (428, 1224), (208, 1222)], "#e2dccc", .9) +
                   line([(236, 1156), (400, 1159)], 1.4, "#d9d2c0", seed=1201, op=.8), w=3.8, seed=1200))
    s.append(H.sleeve(H.L_S, (132, 1196), (196, 1212), seed=940))
    s.append(H.hand_s(H.flat_hand, 222, 1206, 2, 950, 1.0))
    s.append("</g>")
    s.append(H.sleeve(H.R_S, (520, 1222), (430, 1196), seed=960))
    s.append('<g id="pen_hand_s">' + H.pen(462, 1128, 384, 1212, seed=970) + H.hand_s(H.fist, 432, 1162, 133, 980, 1.0) + "</g>")
    s.append("</g>")
    return "".join(s)


H.front_dima = front25

if __name__ == "__main__":
    here = __file__.rsplit("/", 1)[0]
    svg = H.build()
    html = open(f"{here}/template25e.html").read().replace("<!--SVG-->", svg)
    open(f"{here}/heroes25e.html", "w").write(html)
    print("heroes25e.html", len(html) // 1024, "KB")
