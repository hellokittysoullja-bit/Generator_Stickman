"""Костюм кота-детектива рилса 129 (владелец: «логично… без артефактов»): коричневый плащ, чёрная шляпа, чёрные очки, лупа.
Всё рисуется ВНУТРИ рисунка кота (common/cat.py: wear_body — в группе тела, под лапами; wear_head — в группе головы;
paw_item — в правой лапе), поэтому дышит, наклоняется, прыгает и поворачивается вместе с котом и ни на кадр не висит в воздухе.
Морда открыта: шляпа выше глаз (поля на y 958, глаза 1034–1110), стёкла очков тонированные на 35 % — глаза видны сквозь них."""
import math

import lib
from lib import blob, line, shape
from ink import ellipse_pts

COAT, COAT_SH, COAT_HI, BELT = "#8a5a32", "#6a4224", "#a8743f", "#4a2e18"
HAT, HAT_SH, BAND = "#1e1f24", "#0d0e11", "#5a4a3a"


def coat():
    """Плащ на туловище (координаты рисунка кота: шея (836, 1150), низ 1306)."""
    o = []
    body = [(784, 1140), (888, 1140), (922, 1180), (940, 1244), (930, 1302, 1), (742, 1302, 1), (732, 1244), (750, 1180)]
    inner = blob([(868, 1150), (930, 1190), (940, 1300), (880, 1300), (890, 1220)], COAT_SH, .9)
    inner += line([(836, 1150), (836, 1300)], 3.2, BELT, taper=0, wmin=1, seed=12901)
    o.append(shape(body, COAT, inner, w=4.6, seed=12900))
    # пояс с пряжкой
    o.append(shape(lib.rect_pts(738, 1228, 936, 1252), BELT, "", w=3.2, seed=12902))
    o.append(shape(lib.rect_pts(818, 1222, 854, 1258), "#c9a24a", blob(lib.rect_pts(826, 1230, 846, 1250), BELT), w=3.0, seed=12903))
    # лацканы: светлые клинья от шеи вниз
    for sx, sd in ((-1, 12904), (1, 12905)):
        lap = [(836, 1214), (836 + sx * 6, 1150), (836 + sx * 52, 1146), (836 + sx * 40, 1186)]
        o.append(shape(lap, COAT_HI, "", w=3.4, seed=sd))
    # поднятый воротник за головой (голова рисуется поверх и закрывает его середину)
    for sx, sd in ((-1, 12906), (1, 12907)):
        col = [(836 + sx * 30, 1150), (836 + sx * 74, 1104), (836 + sx * 96, 1150), (836 + sx * 64, 1172)]
        o.append(shape(col, COAT_HI, "", w=3.6, seed=sd))
    # пуговицы
    for j, y in enumerate((1196, 1276)):
        for sx in (-1, 1):
            o.append(shape(ellipse_pts(836 + sx * 22, y, 6, 6, 8), "#3a2412", "", w=1.8, seed=12910 + j * 2 + sx))
    return "".join(o)


def hat_and_shades(st):
    """Шляпа-федора и круглые чёрные очки в координатах головы; черты морды сдвигаются с turn — очки тоже."""
    turn = st.get("turn", 0.0)
    FX = 22 * turn
    o = []
    # очки: тонкая чёрная оправа, дужки к ушам, стёкла 35 % — глаза видны
    for nm, ex in (("L", 836 + FX - 44 - 4 * turn), ("R", 836 + FX + 44 - 4 * turn)):
        sq = 1.0 - .22 * max(0.0, turn if nm == "R" else -turn)
        rx, ry = 42 * sq, 36
        lens = ellipse_pts(ex, 1074, rx, ry, 22)
        o.append(f'<path d="M{" L".join(f"{p[0]:.1f} {p[1]:.1f}" for p in lens)} Z" fill="#14161c" opacity=".35"/>')
        o.append(blob(ellipse_pts(ex - rx * .45, 1060, rx * .22, 7, 8, rot=-30), "#ffffff", .35))
        o.append(line([tuple(p) for p in lens] + [tuple(lens[0])], 7.5, "#0d0e11", taper=0, wmin=1, seed=12920 + (nm == "R")))
    o.append(line([(836 + FX - 6, 1066), (836 + FX + 6, 1066)], 6, "#0d0e11", taper=0, wmin=1, seed=12922))
    o.append(line([(836 + FX - 86, 1068), (762, 1062)], 5, "#0d0e11", taper=0, wmin=1, seed=12923))
    o.append(line([(836 + FX + 86, 1068), (912, 1062)], 5, "#0d0e11", taper=0, wmin=1, seed=12924))
    # шляпа: чуть набекрень, поля выше глаз, тулья закрывает верх ушей
    h = []
    crown = [(772, 962, 1), (776, 922), (792, 892), (836, 902), (880, 890), (898, 920), (902, 962, 1)]
    h.append(shape(crown, HAT, blob([(860, 892), (902, 900), (906, 962), (868, 962)], HAT_SH, .9)
                   + line([(808, 900), (836, 914), (866, 900)], 3, "#3a3c44", seed=12931, op=.8), w=4.6, seed=12930))
    h.append(shape(lib.rect_pts(774, 938, 900, 960), BAND, "", w=3.2, seed=12932))
    brim = ellipse_pts(836, 964, 128, 20, 26)
    h.append(shape(brim, HAT, blob(ellipse_pts(860, 970, 90, 10, 16), HAT_SH, .9), w=4.4, seed=12933))
    o.append(f'<g transform="rotate(-7 836 964)">{"".join(h)}</g>')
    return "".join(o)


def loupe(rot=-20.0, glint=0.0):
    """Лупа: хват в (0, 0) (лапа), ручка вверх к линзе."""
    o = [shape(lib.rrect(-9, -70, 9, 18, 8), "#6b3f20", line([(-3, -60), (-3, 8)], 2, "#9a6a3c", seed=12941, op=.8), w=3.2, seed=12940)]
    o.append(shape(lib.rect_pts(-12, -86, 12, -66), "#b8a26a", "", w=2.6, seed=12942))
    ring = ellipse_pts(0, -150, 62, 62, 30)
    o.append(f'<path d="M{" L".join(f"{p[0]:.1f} {p[1]:.1f}" for p in ring)} Z" fill="#cfe8f5" opacity=".45"/>')
    o.append(blob(ellipse_pts(-22, -172, 16, 9, 10, rot=-35), "#ffffff", .7 + .3 * glint))
    o.append(line([tuple(p) for p in ring] + [tuple(ring[0])], 11, "#2a2c30", taper=0, wmin=1, seed=12943))
    return f'<g transform="rotate({rot:.2f})">{"".join(o)}</g>'


def dress(st, paw=None, loupe_on=True, loupe_rot=-20.0, glint=0.0):
    """Добавить костюм в st кота. paw — насколько левая лапа с лупой поднята (по умолчанию 0.55)."""
    st = dict(st or {})
    st["wear_body"] = coat()
    st["wear_head"] = hat_and_shades
    st["sleeve"] = (COAT, COAT_SH)      # рукава плаща: лапы выходят из манжет
    if loupe_on:      # лупа в левой (от зрителя) лапе: линза уходит влево от морды, хвост с огоньком справа не мешает
        st["paw_l"] = .55 if paw is None else paw
        st.setdefault("paw_l_dx", 40.0)
        st["paw_item"] = loupe(loupe_rot, glint)
    return st
