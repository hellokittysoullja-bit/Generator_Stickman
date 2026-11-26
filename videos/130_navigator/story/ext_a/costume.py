"""Костюм кота рилса 130: кепка водителя. Рисуется ВНУТРИ рисунка кота (common/cat.py: wear_head — в группе головы),
поэтому наклоняется и прыгает вместе с головой. Козырёк выше глаз (низ козырька y 990, глаза 1034–1110) — морда открыта.
Подменяет CT.draw: кот в кепке во всех планах, включая призыв story_cta_tg (он рисует кота через cat.draw)."""
import lib
from lib import blob, line, shape
from ink import ellipse_pts

CAP, CAP_SH, VISOR, BADGE = "#2c3e66", "#1d2a48", "#14161c", "#e8c25a"


def cap(st):
    h = []
    crown = [(764, 958, 1), (758, 924), (780, 896), (836, 884), (892, 894), (914, 922), (908, 958, 1)]
    h.append(shape(crown, CAP, blob([(870, 890), (914, 920), (910, 958), (872, 958)], CAP_SH, .9)
                   + line([(790, 904), (836, 896), (884, 904)], 3, "#4a5c86", seed=13010, op=.8), w=4.6, seed=13011))
    h.append(shape(lib.rect_pts(770, 940, 904, 962), "#14161c", "", w=3.2, seed=13012))
    h.append(shape(ellipse_pts(836, 922, 16, 14, 12), BADGE, blob(ellipse_pts(832, 918, 6, 5, 8), "#fff1b0"), w=2.6, seed=13013))
    visor = [(772, 962, 1), (790, 984), (836, 992), (882, 984), (900, 962, 1)]
    h.append(shape(visor, VISOR, blob([(800, 966), (870, 966), (860, 978), (812, 978)], "#3a3c44", .7), w=4.0, seed=13014))
    return f'<g transform="rotate(-4 836 960)">{"".join(h)}</g>'


def install(CT):
    if getattr(CT, "_capped", False):
        return
    raw = CT.draw

    def draw(x, y, k, st, t):
        st = dict(st or {})
        st["wear_head"] = cap
        return raw(x, y, k, st, t)
    CT.draw = draw
    CT._capped = True
