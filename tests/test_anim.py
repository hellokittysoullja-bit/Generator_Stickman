"""Движение внутри рисунка (scripts/anim.py): кривые, пружина, слой на месте — пиксель в пиксель, сжатие без двойного
контура, рисунок на двойках."""
import os
import sys

import cv2
import pytest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import anim  # noqa: E402


def test_bezier_and_gravity_ends():
    for f in (anim.EASE_OUT, anim.EASE_IN, anim.EASE_IO, anim.SNAP, anim.gravity):
        assert abs(f(0.0)) < 1e-3 and abs(f(1.0) - 1.0) < 1e-3
    assert anim.SNAP(1 / 3) > 0.75                     # резкий наезд: больше трёх четвертей пути за первую треть
    assert anim.gravity(0.5) == 0.25                   # падение: путь как квадрат времени


def test_spring_starts_at_one_and_settles():
    assert abs(anim.spring(0.0) - 1.0) < 1e-6
    assert min(anim.spring(t / 100) for t in range(100)) < 0     # перелёт через покой — отскок
    assert abs(anim.spring(1.5)) < 0.02                           # успокоилась


def test_track_keys():
    tr = anim.Track([(0.0, 0.0), (1.0, 10.0)])
    assert tr(-1) == 0.0 and tr(0.5) == 5.0 and tr(3) == 10.0
    tv = anim.Track([(0.0, (0.0, 0.0)), (1.0, (2.0, 4.0))])
    assert tv(0.5) == (1.0, 2.0)


def test_on_twos_holds_drawing():
    assert anim.on_twos(0.0) == anim.on_twos(1 / 13) == 0.0
    assert anim.on_twos(1 / 12 + 1e-4) == 1 / 12


def test_layer_at_home_is_pixel_exact():
    rng = np.random.default_rng(0)
    img = rng.uniform(0, 255, (120, 160, 3)).astype(np.float32)
    mask = np.zeros((120, 160), bool); mask[30:80, 40:110] = True
    lay = anim.Layer.cut(img, mask, pad=6, feather=0)
    base = np.zeros_like(img)
    lay.draw(base, lay.home())
    assert np.abs(base[mask] - img[mask]).max() < 1e-3   # слой на своём месте — тот же рисунок


def test_squash_is_a_warp_not_a_blend():
    """Сжатие — смещение пикселей, а не смесь двух картинок: линия остаётся одной линией (было: двойной контур)."""
    img = np.full((200, 200, 3), 255, np.float32); img[100:104, :] = 0           # горизонтальная линия
    m = np.full((200, 200), 0.5, np.float32)                                      # «мягкая» маска посередине силы
    out = anim.squash_region(img, m, 180, 100, 0.8, 1.0)
    dark_rows = np.where(out[:, 100, 0] < 128)[0]
    assert len(dark_rows) and dark_rows.max() - dark_rows.min() <= 6              # одна линия, не две
    assert dark_rows.min() > 104                                                  # и она сдвинулась к полу


def test_smear_trails_behind_motion():
    rgb = np.zeros((60, 60, 3), np.float32); a = np.zeros((60, 60), np.float32); a[25:35, 25:35] = 1
    _, out_a = anim._smear(rgb * a[..., None], a, (0.0, 12.0))                    # движется вниз
    assert out_a[15:25, 30].sum() > 0.5 and out_a[36:46, 30].sum() < 1e-3        # след сверху, впереди чисто


def _disk_scene():
    img = np.full((400, 400, 3), 250, np.float32)
    cv2.circle(img, (200, 250), 100, (20, 20, 20), -1)                # «персонаж» стоит на полу y=350
    mask = np.zeros((400, 400), np.float32); cv2.circle(mask, (200, 250), 130, 1.0, -1)
    mask = cv2.GaussianBlur(mask, (0, 0), 6)
    return img, mask


def test_squash_follow_keeps_volume():
    """25.10: сжатие держит площадь; старое squash_region (sx = 1 + 0.5·a) теряло её — кот «худел» на ударе."""
    img, mask = _disk_scene()
    def area(x):
        return float((x[..., 0] < 128).sum())
    a0 = area(img)
    new = anim.squash_follow(img, mask, (200, 350), lambda t: 0.12, 1.0, lag=0.0)
    old = anim.squash_region(img, mask, 350, 200, 1 - 0.12, 1 + 0.06)
    assert abs(area(new) / a0 - 1) < 0.03
    assert area(old) / a0 < 0.95


def test_squash_follow_hit_answers_now_far_parts_lag():
    """Захлёст 25.10: то, куда пришёлся удар, отвечает в тот же кадр; дальнее (хвост) догоняет позже."""
    img, mask = _disk_scene()
    cv2.rectangle(img, (300, 320), (395, 345), (20, 20, 20), -1)       # «хвост» справа у пола
    cv2.rectangle(mask, (290, 310), (399, 350), 1.0, -1)

    def amount(t):                                                     # удар сверху в t = 1.0
        return 0.15 if t >= 1.0 else 0.0
    now = anim.squash_follow(img, mask, (200, 350), amount, 1.02, lag=0.12, focus=(200, 150))
    top_now = np.where((now[..., 0] < 128)[:, 150:250].any(1))[0].min()
    assert top_now > 150 + 8                                           # голова под ударом уже опустилась
    tail_now = np.where((now[..., 0] < 128)[:, 300:400].any(0))[0].max() + 300
    late = anim.squash_follow(img, mask, (200, 350), amount, 1.5, lag=0.12, focus=(200, 150))
    tail_late = np.where((late[..., 0] < 128)[:, 300:400].any(0))[0].max() + 300
    assert tail_late > tail_now + 3                                    # хвост раздаётся вширь позже


def test_squash_follow_rigid_object_does_not_bend():
    """Телефон на морде — твёрдый: сдвигается целиком, прямая остаётся прямой (лист 25.10: телефон гнулся с мордой)."""
    img, mask = _disk_scene()
    cv2.line(img, (120, 200), (280, 200), (200, 0, 0), 6)              # «телефон» поперёк морды
    rig = np.zeros((400, 400), np.float32)
    cv2.rectangle(rig, (110, 190), (290, 210), 1.0, -1)

    def amount(t):
        return 0.15
    out = anim.squash_follow(img, mask, (200, 350), amount, 1.0, lag=0.0, focus=(200, 200), rigid=[rig])
    red = (out[..., 0] > 150) & (out[..., 1] < 80)
    ys = [np.where(red[:, x])[0].mean() for x in (130, 200, 270) if red[:, x].any()]
    assert len(ys) == 3 and max(ys) - min(ys) < 1.5
    bent = anim.squash_follow(img, mask, (200, 350), amount, 1.0, lag=0.0, focus=(200, 200))
    red = (bent[..., 0] > 150) & (bent[..., 1] < 80)
    yb = [np.where(red[:, x])[0].mean() for x in (130, 200, 270) if red[:, x].any()]
    assert max(yb) - min(yb) > 1.5                                     # без rigid прямая гнётся — тест не пустой


def test_squash_follow_far_parts_lag_behind():
    """Захлёст: в момент, когда опора уже сжалась, верх (уши) ещё нет — он запаздывает на lag."""
    img, mask = _disk_scene()
    def amount(t):                                                     # удар в t = 1.0
        return 0.15 if t >= 1.0 else 0.0
    out = anim.squash_follow(img, mask, (200, 350), amount, 1.05, lag=0.12)
    rows = np.where((out[..., 0] < 128).any(1))[0]
    top_still = rows.min()                                             # верх ещё не опустился
    full = anim.squash_follow(img, mask, (200, 350), amount, 1.5, lag=0.12)
    top_full = np.where((full[..., 0] < 128).any(1))[0].min()
    assert top_still < top_full - 5                                    # потом верх догоняет
    assert abs(top_still - 150) <= 6                                   # а в 1.05 стоит почти на месте (исходный верх 150)


def test_split_part_gives_stray_whiskers_back_to_the_body():
    # рилс 13 (владелец 02.11): усы щеки, попавшие в многоугольник хвоста, висели в воздухе, когда хвост махал
    import cv2
    tail = np.zeros((200, 200), np.uint8)
    cv2.circle(tail, (60, 100), 40, 1, -1)                        # тело хвоста
    cv2.line(tail, (60, 140), (60, 160), 1, 2)                     # шерстинка на краю — своя
    cv2.line(tail, (130, 60), (180, 70), 1, 2)                     # ус в просвете, оторван от хвоста
    cv2.line(tail, (30, 75), (5, 20), 1, 2)                        # ус, касающийся шерсти хвоста, торчит наружу
    body = np.zeros_like(tail)
    own, rest = anim.split_part(tail, body)
    assert own[100, 60] and own[150, 60]                          # тело и своя шерсть — хвосту
    assert not own[65, 155] and rest[65, 155]                     # ус — телу
    assert not own[42, 15] and rest[42, 15]                        # торчащий ус — тоже телу
    assert anim.detached_share(own * 255) == 0.0
    assert anim.detached_share(tail * 255) > 0.0                  # проверка ловит прежнюю нарезку


def test_defringe_removes_paper_halo_on_layer_edge():
    # кайма: край тёмного хвоста, смешанный с белой бумагой, светится на сером фоне
    rgb = np.zeros((10, 10, 3), np.float32); a = np.zeros((10, 10), np.float32)
    rgb[:, :5] = 40; a[:, :5] = 1.0
    rgb[:, 5] = 0.5 * 40 + 0.5 * 250; a[:, 5] = 0.5               # край: полупрозрачный, наполовину бумага
    out = anim.defringe(rgb, a, paper=(250, 250, 250))
    assert abs(out[0, 5, 0] - 40) < 3                              # цвет края — цвет хвоста, а не бумаги


def test_trim_paper_edge_keeps_inner_highlights():
    img = np.full((60, 60, 3), 248, np.float32)
    img[10:50, 10:50] = 40                                         # тёмная часть
    img[28:32, 28:32] = 250                                        # блик внутри — рисунок
    mask = np.zeros((60, 60), np.uint8); mask[8:52, 8:52] = 1      # маска с захватом бумаги по краю
    out = anim.trim_paper_edge(img, mask)
    assert out[9, 30] == 0 and out[30, 9] == 0                     # бумага по краю снята
    assert out[30, 30] == 1 and out[20, 20] == 1                   # блик и тело остались


def test_keep_attached_drops_frame_bits_near_the_character():
    import cv2
    m = np.zeros((100, 100), np.uint8)
    cv2.circle(m, (40, 50), 25, 1, -1)
    cv2.line(m, (90, 10), (90, 80), 1, 1)                          # обрывок рамки двери рядом с котом
    cv2.line(m, (64, 50), (75, 50), 1, 1)                          # ус от щеки — касается тела
    out = anim.keep_attached(m)
    assert out[40, 90] == 0 and out[50, 72] == 1 and out[50, 40] == 1


def test_drop_scene_lines_removes_door_frame_through_whiskers():
    import cv2
    img = np.full((600, 600, 3), 245, np.float32)
    cv2.circle(img, (250, 300), 120, (40, 40, 40), -1)            # кот
    cv2.line(img, (420, 0), (420, 599), (60, 60, 60), 3)           # рамка двери во всю высоту
    cv2.line(img, (360, 290), (520, 250), (30, 30, 30), 2)         # ус через рамку
    mask = np.zeros((600, 600), np.uint8)
    cv2.circle(mask, (250, 300), 120, 1, -1)
    mask[200:400, 360:520] |= (img[200:400, 360:520].mean(2) < 200).astype(np.uint8)
    out = anim.drop_scene_lines(img, mask)
    assert out[350, 420] == 0                                      # рамка ниже уса — не кот
    assert out[270, 440] == 1 or out[269, 440] == 1                # ус остался
    assert out[300, 250] == 1                                      # тело не тронуто


def test_underlap_hides_the_cut_seam_between_part_and_body():
    # владелец 02.11: белая полоска между хвостом и телом — разрез встык, бумага светится сквозь оба края
    full = np.zeros((40, 80), np.uint8); full[10:30, 5:75] = 1
    tail = full.copy(); tail[:, 40:] = 0
    body = full.copy(); body[:, :40] = 0
    out = anim.underlap(tail, body, full, width=6)
    assert out[20, 44] == 1 and out[20, 50] == 0                   # хвост зашёл под тело на 6 px, дальше — нет
    assert out[5, 44] == 0                                         # только пиксели персонажа


def test_fill_hole_grain_never_wraps_the_frame_edge():
    # разбор 02.11: np.roll заворачивал край кадра — в заливке высокой дыры проступали линии с другого края
    rng = np.random.default_rng(0)
    img = np.full((300, 300, 3), 240, np.float32) + rng.normal(0, 1.5, (300, 300, 1)).astype(np.float32)
    img[280:284, :] = 30                                           # линия пола у нижнего края
    hole = np.zeros((300, 300), bool); hole[20:200, 100:200] = True   # высокая дыра у верхнего края
    out = anim.fill_hole(img, hole, feather=0)
    assert out[20:200, 100:200].min() > 200                        # линии пола в дыре нет
    sd = float(out[60:160, 120:180].std())
    assert 0.5 < sd < 4.0                                          # зерно есть, но не грязь


def test_fill_hole_noise_strength_from_clean_paper_only():
    rng = np.random.default_rng(1)
    img = np.full((200, 200, 3), 240, np.float32) + rng.normal(0, 1.0, (200, 200, 1)).astype(np.float32)
    for x in range(10, 200, 25):
        img[:, x:x + 3] = 30                                       # линии туши по фону
    hole = np.zeros((200, 200), bool); hole[80:120, 80:120] = True
    out = anim.fill_hole(img, hole, grain_from="noise", feather=0)
    assert float(out[85:115, 95:105].std()) < 3.0                  # сила шума — как у бумаги, не как у линий


def _whisker_scene():
    """Хвост — толстый круг, тело справа; ус тела идёт по краю хвоста и выходит за него (рилс 13, 02.11)."""
    img = np.full((200, 300, 3), 245, np.uint8)
    part = np.zeros((200, 300), np.uint8); cv2.circle(part, (90, 100), 45, 1, -1)
    rest = np.zeros_like(part); rest[40:180, 160:300] = 1
    img[part > 0] = 100; img[rest > 0] = 100
    cv2.line(img, (110, 95), (230, 70), (10, 10, 10), 2)               # ус: начинается на шерсти хвоста, уходит к телу
    line = np.zeros_like(part); cv2.line(line, (110, 95), (230, 70), 1, 2)
    part = (part | (line & (np.arange(300)[None, :] < 160))).astype(np.uint8)     # многоугольник хвоста забрал кусок уса
    rest = (rest | (line & (np.arange(300)[None, :] >= 160))).astype(np.uint8)
    return img, part, rest, line


def test_claim_strokes_gives_whisker_drawn_over_part_to_its_owner():
    img, part, rest, line = _whisker_scene()
    p, r, fill = anim.claim_strokes(img, part, rest)
    outside = line & (cv2.circle(np.zeros_like(line), (90, 100), 45, 1, -1) == 0)
    assert p[outside > 0].sum() <= 4                       # торчащий за хвост кусок уса — не хвосту (угол у края — пара px)
    assert (r[line > 0] == 1).mean() > 0.9                # ус целиком у хозяина
    assert fill.sum() > 0                                 # на шерсти под усом — дорисовка
    assert p.sum() > 0.95 * (cv2.circle(np.zeros_like(line), (90, 100), 45, 1, -1)).sum()   # хвост цел


def test_claim_strokes_keeps_fur_strands():
    img = np.full((200, 300, 3), 245, np.uint8)
    part = np.zeros((200, 300), np.uint8); cv2.circle(part, (120, 100), 50, 1, -1)
    for a in range(0, 360, 30):                           # короткие треугольные пряди тушью по краю
        x, y = 120 + 50 * np.cos(np.radians(a)), 100 + 50 * np.sin(np.radians(a))
        pts = np.int32([[x, y], [x + 18 * np.cos(np.radians(a + 20)), y + 18 * np.sin(np.radians(a + 20))],
                        [x + 4 * np.cos(np.radians(a + 90)), y + 4 * np.sin(np.radians(a + 90))]])
        cv2.fillPoly(part, [pts], 1)
    img[part > 0] = 30
    p, r, fill = anim.claim_strokes(img, part, np.zeros_like(part))
    assert p.sum() == part.sum() and fill.sum() == 0


def test_underlap_only_at_the_seam_and_never_takes_thin_strokes():
    part = np.zeros((200, 300), np.uint8); part[50:150, 50:120] = 1
    cover = np.zeros_like(part); cover[50:150, 120:250] = 1
    whisk = np.zeros_like(part); cv2.line(whisk, (40, 30), (125, 45), 1, 2); cover |= whisk
    full = part | cover
    u = anim.underlap(part, cover, full, around=(120, 140, 25))
    added = u & (1 - part)
    assert added.sum() > 0
    ys, xs = np.nonzero(added)
    assert ((xs - 120) ** 2 + (ys - 140) ** 2 <= 25 ** 2).all()   # только у шва
    assert (added & whisk).sum() == 0                              # ус соседа не забирается


def test_inpaint_bg_on_dark_wall_keeps_the_old_fill():
    """LaMa на тёмной стене не проверена (25.10 давала пятна): там — прежняя fill_hole, без сети."""
    img = np.full((120, 160, 3), 40, np.float32)
    hole = np.zeros((120, 160), bool); hole[40:80, 60:100] = True
    img[hole] = 200
    out = anim.inpaint_bg(img, hole)
    assert out[hole].mean() < 80


@pytest.mark.skipif(not os.path.exists(os.path.join(os.path.dirname(__file__), "..", "models", "lama_fp32.onnx")),
                    reason="нет models/lama_fp32.onnx (качается при первом запуске сцены)")
def test_inpaint_bg_continues_scene_line_and_leaves_no_silhouette(tmp_path):
    rng = np.random.default_rng(1)
    img = np.full((400, 600, 3), 238, np.float32); img[300:] = 215
    cv2.line(img, (0, 300), (599, 300), (90, 90, 90), 3)
    img += rng.normal(0, 2, img.shape)
    truth = img.copy()
    hole = np.zeros((400, 600), np.uint8); cv2.circle(hole, (300, 280), 70, 1, -1); hole = hole > 0
    img[hole] = 30                                                   # «кот»
    out = anim.inpaint_bg(img, hole, cache_dir=str(tmp_path))
    assert (out[300, 250:350].mean(1) < 150).mean() > 0.9           # плинтус продолжен сквозь дыру
    assert np.abs(out[hole] - truth[hole]).mean() < 8                # силуэта предмета нет
    again = anim.inpaint_bg(img, hole, cache_dir=str(tmp_path))
    assert np.array_equal(out, again)                                # второй раз — из кэша, то же самое


def test_whiskers_kept_outlines_and_furniture_lines_dropped():
    """Нарезка по точкам (04.11): ус — тонкий прямой штрих от контура — возвращается в слой; контур капли рядом,
    дуга мебели и длинная линия, уходящая далеко, — нет."""
    img = np.full((600, 600, 3), 245, np.uint8)
    cv2.circle(img, (300, 300), 100, (60, 60, 60), -1)                     # «кот»
    mask = np.zeros((600, 600), np.uint8); cv2.circle(mask, (300, 300), 100, 1, -1)
    cv2.line(img, (400, 300), (480, 290), (20, 20, 20), 2)                 # ус
    cv2.circle(img, (300, 160), 25, (20, 20, 20), 2)                       # контур капли у головы
    cv2.line(img, (200, 300), (0, 300), (20, 20, 20), 3)                   # линия дивана — уходит далеко
    a = anim.whisker_alpha(img, mask)
    assert a[293:297, 440:460].max() > 0.5                                 # ус есть
    assert a[130:140, 290:310].max() < 0.05                                # контура капли нет
    assert a[298:302, 120:180].max() < 0.05                                # линии дивана нет


def test_fill_small_holes_keeps_background_between_parts():
    m = np.zeros((200, 200), np.uint8); m[20:180, 20:180] = 1; m[50:60, 50:60] = 0     # дырка-экран внутри
    m[:, 100:102] = 0                                                                  # щель до края — фон
    f = anim._fill_small_holes(m)
    assert f[55, 55] == 1 and f[5, 101] == 0 and f[100, 101] == 0


def test_save_layer_keeps_soft_alpha(tmp_path):
    img = np.full((120, 120, 3), 240, np.uint8); img[30:90, 30:90] = 40
    alpha = np.zeros((120, 120), np.float32); alpha[30:90, 30:90] = 1; alpha[30:90, 90:94] = 0.4
    layers = {}
    anim.save_layer(str(tmp_path), "x", img, (alpha > 0.5).astype(np.uint8), layers, alpha=alpha)
    from PIL import Image
    a = np.asarray(Image.open(tmp_path / "x.png"))[..., 3]
    x0, y0 = layers["x"]["xy"]
    assert 60 < a[60 - y0, 91 - x0] < 140                                   # мягкий край сохранён, а не размыт заново


def test_plate_fused_only_in_hole_and_toned_to_drawing():
    """Чистая подложка (04.11): вне дыры кадр — исходный рисунок; внутри — подложка, тон подтянут к рисунку (подложка
    с другим оттенком стены не даёт пятна), сдвиг подложки на пару пикселей снимается совмещением."""
    rgb = np.full((400, 300, 3), 240, np.float32); cv2.line(rgb, (0, 200), (299, 200), (20, 20, 20), 3)
    plate = rgb.copy() * 0.95                                          # подложка темнее на 5 %
    plate = np.roll(plate, 2, axis=1)
    hole = np.zeros((400, 300), bool); hole[150:250, 100:200] = True
    out = anim._fuse_plate(rgb, plate.astype(np.uint8), hole)
    assert np.abs(out[20:60, 20:60] - rgb[20:60, 20:60]).max() < 1     # вне дыры — рисунок
    assert abs(out[170, 150].mean() - 240) < 4                         # внутри — тон стены рисунка
    assert out[200, 150].mean() < 120                                   # линия внутри дыры на месте
