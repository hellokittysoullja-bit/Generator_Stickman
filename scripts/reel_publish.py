"""Комплект публикации рилса — знания маркетинга и бренда в готовом виде к каждому рилсу (23.10, владелец: «не вижу,
чтобы во всех новых рилсах автоматически использовались все эти знания»). reel.py зовёт его сам после рендера.

    python scripts/reel_publish.py videos/NN/reel     # -> publish.md и cover.jpg рядом с reel.mp4

Что внутри и откуда (docs/reels_knowledge/07_marketing_brand_persuasion_production.md, раздел 8):
- обложка = первый рисунок + короткий текст шрифтом субтитров, в зоне, которую видно в сетке профиля 3:4 (п.11);
- подпись с ключевой фразой ниши в первых 125 знаках и 3–5 хэштегами (п.24);
- ссылка с UTM-меткой этого рилса — сравнивать рилсы по переходам на 1 000 просмотров, а не по просмотрам (п.7);
- закреплённый комментарий: опрос «1 — диагноз, 2 — нет» и причина перейти (п.26);
- варианты хука для пробных Reels и как их сравнивать (п.3), второй финал (п.10);
- таблица «знание → где в рилсе» из passport.knowledge (docs/reels_knowledge/apply_checklist.json);
- профиль канала (п.23) — из docs/reels_brand.json, один раз на канал, но рядом с каждым рилсом, чтобы не забыть.
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reel        # noqa: E402
import reel_rules  # noqa: E402

GRID_Y0, GRID_Y1 = 240, 1680   # сетка профиля показывает центр 1080×1440 (3:4) — текст обложки внутри


def utm_link(brand, reel_dir, version):
    ep = os.path.basename(os.path.dirname(os.path.abspath(reel_dir))) or "reel"
    q = f"utm_source=instagram&utm_medium=reels&utm_campaign={ep}&utm_content={version or 'v'}"
    base = brand.get("site_url") or "<адрес сайта — впишите в docs/reels_brand.json>"
    return f"{base}{'&' if '?' in base else '?'}{q}"


def open_counters(t):
    """Обводка жирного шрифта заливает узкие внутренние просветы букв («в» в «висит» — две чёрные точки, обложка эп.01).
    Просвет, залитый обводкой целиком (внутри белой буквы, без прозрачных точек), снова делается прозрачным; просвет, где
    обводка оставила дырку («о», «е» на обложке v15), не трогается — обложка эталона та же байт в байт."""
    import cv2
    a = np.asarray(t).copy()
    fill = (a[..., 3] > 128) & (a[..., :3].min(axis=2) > 200)
    n, lab = cv2.connectedComponents((~fill).astype(np.uint8), connectivity=4)
    edge = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    for i in range(1, n):
        if i in edge: continue
        m = lab == i
        if a[..., 3][m].min() > 200: a[..., 3][m] = 0
    return Image.fromarray(a)


def cover(reel_dir, text, out):
    """Первый кадр рилса без субтитра (полоса закрыта бумагой) + текст обложки шрифтом субтитров в зоне сетки."""
    video = os.path.join(reel_dir, "reel.mp4")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "0.05", "-i", video, "-frames:v", "1", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    if len(raw) != 1080 * 1920 * 3:
        return None
    a = np.frombuffer(raw, np.uint8).reshape(1920, 1080, 3).copy()
    rep = json.load(open(os.path.join(reel_dir, "reel_report.json"), encoding="utf8"))
    ph = rep.get("picture_h", 1380)
    a[ph:] = a[ph - 3:ph - 1].mean(axis=(0, 1)).astype(np.uint8)
    im = Image.fromarray(a).convert("RGBA")
    size = 130
    while True:                                    # текст в ширину кадра с боковыми зонами (рилс эп.01: «Письмо висит 3 дня»
        f = reel.font(reel.CAP_FONT, size, reel.CAP_AXES, raqm=True)       # на 130 вылез за оба края)
        t = reel.text_img(text, f, reel.WHITE, stroke=9, stroke_fill=(0, 0, 0), pad=20)
        if t.width <= 1080 - 2 * reel_rules.SAFE_SIDE or size <= 70: break
        size -= 6
    t = open_counters(t)
    y = min(ph + 40, GRID_Y1 - t.height - 20)
    im.alpha_composite(t, ((1080 - t.width) // 2, y))
    im.convert("RGB").save(out, quality=92)
    return out


def publish(reel_dir):
    spec = json.load(open(os.path.join(reel_dir, "reel.json"), encoding="utf8"))
    pp = spec.get("passport") or {}
    brand = reel_rules.load_json(reel_rules.BRAND_PATH, {})
    checklist = reel_rules.load_json(reel_rules.CHECKLIST_PATH, {"items": []})
    log = reel_rules.load_json(os.path.join(reel_rules.ROOT_DIR, "docs", "reels_log.json"), [])
    rel = os.path.relpath(reel_dir, reel_rules.ROOT_DIR)
    version = next((r.get("version") for r in log if os.path.normpath(r.get("reel", "")) == os.path.normpath(rel)), None)
    beats = spec.get("beats", [])
    txt = [reel_rules.clean(b["text"]) for b in beats]
    cov = cover(reel_dir, (pp.get("cover") or {}).get("text", ""), os.path.join(reel_dir, "cover.jpg"))
    link = utm_link(brand, reel_dir, version)
    L = [f"# Публикация: {spec.get('title', rel)}", "",
         "Собрано `scripts/reel_publish.py` из паспорта рилса, `docs/reels_brand.json` и чек-листа знаний. Публикует владелец.", "",
         "## Обложка", f"`cover.jpg` — первый рисунок и «{(pp.get('cover') or {}).get('text', '')}». Текст стоит внутри центра "
         "1080×1440: так его видно в сетке профиля. Проверка вслепую (07 §8 п.11): показать скриншот «Интересного» с обложкой "
         "трём людям — на что нажали бы первым?" + ("" if cov else " **Обложку не собрать: нет reel.mp4.**"), "",
         "## Подпись", pp.get("caption", "**нет подписи в паспорте**"), "",
         "## Ссылка с UTM (в шапку профиля или в подпись, если можно)", f"`{link}`", "",
         *([f"## Кодовое слово «{pp['keyword']['word']}» (09 §4)",
            f"Человек пишет «{pp['keyword']['word']}» в комментарии — автоответ в личку: {pp['keyword'].get('delivers', '')}. "
            "Ссылка выше — внутри этого сообщения, а не в шапке. Без включённого автоответа рилс с кодовым словом не "
            "публиковать (люди напишут и не получат обещанного — хуже, чем «ссылка в шапке»). Тексты сообщений — "
            "`docs/reels_funnel_texts.md`.", ""] if pp.get("keyword") else []),
         "Сравнивать рилсы по переходам и пересылкам на 1 000 просмотров, по удержанию 3 с и досмотру — не по просмотрам "
         "(07 §8 п.7). Цифры через 24 ч и 7 дней — в `docs/reels_log.json`, поле `after_publish`.", "",
         "## Закреплённый комментарий", pp.get("pinned_comment") or brand.get("pinned_comment_default", ""), "",
         "## Пробные Reels: варианты хука (07 §8 п.3)",
         "Каждый вариант — другая первая фраза; меняются ≥ 2 из 4 элементов первых 3–7 с (первая фраза, первый кадр, подпись; "
         "звук у нас не меняется). Не больше 4–5 пробных в день, один и тот же ролик повторно не заливать. Победитель — по "
         "удержанию 3 с, пересылкам и переходам; собрать вариант: "
         "`python scripts/reel_variant.py " + rel + " --variant N` (N — номер ниже; "
         "текст и первый кадр берутся из паспорта) или `--hook \"…\"`.", ""]
    L += [f"{i + 1}. {v['text']} (первый кадр {v['first']})" if isinstance(v, dict) and v.get("first")
          else f"{i + 1}. {v.get('text', '') if isinstance(v, dict) else v}"
          for i, v in enumerate(pp.get("hook_variants", []))] + [""]
    if pp.get("alt_final"):
        L += ["## Второй финал (07 §8 п.10)", pp["alt_final"], ""]
    if (pp.get("standard") or 0) >= reel_rules.MATRIX_STANDARD:
        cv = reel_rules.matrix_coverage(spec)
        L += ["## Матрица применения (docs/reels_knowledge/apply_matrix.jsonl)",
              f"Приёмов «каждый рилс»: во фразах {cv['beat']}, вне ролика {cv['where']}, кандидатом хука {cv['candidate']}, "
              f"отказ с причиной {cv['skip']}, без решения {cv['none']}. Решения — `passport.matrix` в reel.json.", ""]
    L += ["## Знания базы в этом рилсе", "| знание | где | фраза |", "|---|---|---|"]
    kn = pp.get("knowledge") or {}
    for it in checklist.get("items", []):
        if it["kind"] != "beat":
            continue
        v = kn.get(it["id"])
        if isinstance(v, dict) and "skip" in v:
            L.append(f"| {it['title']} | не к месту | {v['skip']} |")
            continue
        bs = list(dict.fromkeys(reel_rules._beats_of(v)))
        L.append(f"| {it['title']} | {', '.join(map(str, bs)) or '—'} | {' / '.join('«' + txt[b] + '»' for b in bs if b < len(txt))} |")
    L += ["", "Пункты, которые проверяет код (стоп-слова, стыдящие повеления, ярлыки ≤ 2, обложка, подпись, хэштеги, варианты "
          "хука, петля, длина), — в `scripts/reel_rules.py`; рилс с нарушением не рендерится.", "",
          "## Профиль канала (07 §8 п.23) — проверить один раз", f"- Имя: {brand.get('profile', {}).get('name_field', '')}",
          f"- Био: {brand.get('profile', {}).get('bio', '')}",
          f"- Хайлайты: {', '.join(brand.get('profile', {}).get('highlights', []))}",
          f"- Аватар: {brand.get('profile', {}).get('avatar', '')}", f"- Источник: {brand.get('profile', {}).get('source', '')}", ""]
    out = os.path.join(reel_dir, "publish.md")
    open(out, "w", encoding="utf8").write("\n".join(L))
    return out


if __name__ == "__main__":
    print(publish(sys.argv[1]))
