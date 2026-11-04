#!/usr/bin/env python3
"""Обязательная структура длинного ролика YouTube (владелец 27.10: «без которой вообще невозможно сделать ролик»).

  python scripts/long_rules.py videos/NN_тема            — проверка до плана кадров, картинок и озвучки
  python scripts/long_rules.py videos/NN_тема --final    — то же + проверки готового ролика (F1–F4)
  python scripts/long_rules.py videos/NN_тема --template — заготовка long_passport.json со всеми полями

Правила — docs/long_knowledge/checklist.json (каждое из роликов, прочитанных целиком, конспект 01_notes.md).
kind=code проверяется здесь по script.txt и long_passport.json; kind=decide требует в паспорте items[id]
{"how": ...} или {"skip": ...}. make_video.py зовёт check() до первого платного шага и не идёт дальше при ошибке.
Код 0 — чисто, 1 — есть дыры."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from reel_rules import human_issues  # noqa: E402  (тот же «человеческий текст», что у рилсов)

CHECKLIST = os.path.join(ROOT, "docs", "long_knowledge", "checklist.json")
PASSPORT = "long_passport.json"
LONG_WORDS = 300            # сценарий длиннее — это длинный ролик, структура обязательна (эп.01/02 — пробы по 30 слов)
TITLE_MAX = 55              # Aprilynne Alter: дальше YouTube режет название троеточием
URGENCY = ("срочно", "успей", "последний шанс", "только сегодня", "пока не поздно", "осталось мало")
WARMUP = ("привет", "здравствуй", "добро пожаловать", "сегодня мы", "сегодня я", "в этом видео", "в этом ролике",
          "на нашем канале", "на моём канале", "на моем канале", "мой канал", "наш канал")
GOODBYE = ("спасибо за просмотр", "подписывайтесь", "подпишись", "ставьте лайк", "поставь лайк", "до встречи",
           "до новых встреч", "всем пока")
YOU = re.compile(r"\b(ты|тебя|тебе|тобой|твой|твоя|твоё|твое|твои|твоих|твоим|твою|твоей|твоего|твоему)\b")
CLIMAX_WORDS = 10
SKELETON = (6, 10)
CUT_SHARE = 0.10            # Jon Dorman: «если не вырезал 10 %, ты не старался»
EMOTIONS_MIN = 3


def checklist(path=CHECKLIST):
    return json.load(open(path, encoding="utf-8"))["items"]


def norm(s):
    s = (s or "").lower().replace("ё", "е")
    s = re.sub(r"\[[^\]]*\]", " ", s)
    s = re.sub(r"[^\w\s]", " ", s)
    return " ".join(s.split())


def sections(script_text):
    """[(ИМЯ, текст для голоса)] секций HOOK / BLOCK* / FINAL и title из METADATA."""
    parts = re.split(r"===\s*(.*?)\s*===", script_text)
    out, title = [], ""
    for i in range(1, len(parts), 2):
        name, body = parts[i].strip().upper(), parts[i + 1] if i + 1 < len(parts) else ""
        if name.startswith("METADATA"):
            m = re.search(r"^\s*TITLE\s*:\s*(.+)$", body, re.M)
            title = m.group(1).strip() if m else ""
        elif name.startswith(("HOOK", "BLOCK", "FINAL")):
            out.append((name, re.sub(r"\[[^\]]*\]", " ", body).strip()))
    return title, out


def sentences(text):
    return [x.strip() for x in re.split(r"(?<=[.!?…])\s+", text) if x.strip()]


def words(text):
    return re.findall(r"[а-яёa-z0-9]+", text.lower())


def is_long(video_dir):
    """Структура обязательна для длинного ролика: есть паспорт или сценарий длиннее LONG_WORDS слов."""
    if os.path.exists(os.path.join(video_dir, PASSPORT)):
        return True
    p = os.path.join(video_dir, "script.txt")
    if not os.path.exists(p):
        return False
    _, secs = sections(open(p, encoding="utf-8").read())
    return sum(len(words(t)) for _, t in secs) >= LONG_WORDS


def template(items=None):
    items = items or checklist()
    return {
        "standard": 1,
        "questions": ["", "", "", "", ""],
        "promise": ["", "", ""],
        "climax": "",
        "skeleton": ["", "", "", "", "", ""],
        "hook_candidates": [""] * 10,
        "hook_voiced": ["", ""],
        "points": [{"block": "BLOCK 1", "rehook": "", "unpack": "story", "unpack_quote": "", "payoff_quote": "",
                    "emotion": ""}],
        "end_hook": "",
        "facts": {},
        "revision": {"words_before": 0, "words_after": 0},
        "approved": {"title": False, "hook": False, "script": False},
        "items": {it["id"]: {"how": ""} for it in items if it["kind"] == "decide"},
        "final_checks": {"viewer_watch": [], "distraction_test": "", "phone_audio": "", "outsider": ""},
    }


def _filled(x):
    return isinstance(x, str) and x.strip() != ""


def check(video_dir, final=False, items=None):
    """Список дыр (пусто — структура соблюдена). Каждая строка начинается с id правила."""
    items = items or checklist()
    err = []
    sp = os.path.join(video_dir, "script.txt")
    pp = os.path.join(video_dir, PASSPORT)
    if not os.path.exists(sp):
        return [f"нет {sp}"]
    if not os.path.exists(pp):
        return [f"нет {pp}: заготовка — python scripts/long_rules.py {video_dir} --template "
                "(правила — docs/long_knowledge/checklist.json)"]
    title, secs = sections(open(sp, encoding="utf-8").read())
    try:
        p = json.load(open(pp, encoding="utf-8"))
    except ValueError as e:
        return [f"{pp} не читается как JSON: {e}"]
    hook = " ".join(t for n, t in secs if n.startswith("HOOK"))
    blocks = [(n, t) for n, t in secs if n.startswith("BLOCK")]
    final_txt = " ".join(t for n, t in secs if n.startswith("FINAL"))
    spoken = " ".join(t for _, t in secs)

    # T1 название
    if not title:
        err.append("T1: нет названия — === METADATA === и строка TITLE: …")
    else:
        if len(title) > TITLE_MAX:
            err.append(f"T1: название {len(title)} знаков > {TITLE_MAX} — YouTube обрежет конец («{title}»)")
        if any(u in title.lower() for u in URGENCY):
            err.append(f"T1: «срочность» в названии — у нас запрет давления («{title}»)")
    # Q1 вопросы и обещание
    qs = [q for q in p.get("questions") or [] if _filled(q)]
    if len(qs) < 5:
        err.append(f"Q1: выписано вопросов зрителя {len(qs)} < 5 (все вопросы, которые рождает название)")
    promise = [x for x in p.get("promise") or [] if _filled(x)]
    if len(promise) != 3:
        err.append(f"H3: обещаний {len(promise)}, нужно ровно три конкретные вещи (passport.promise)")
    for x in promise:
        if norm(x) not in norm(hook):
            err.append(f"H3: обещание «{x}» не стоит в HOOK дословно")
    # Q2, Q4 кульминация и скелет
    cl = p.get("climax") or ""
    if not _filled(cl):
        err.append("Q2: нет одной кульминации (passport.climax)")
    elif len(words(cl)) > CLIMAX_WORDS:
        err.append(f"Q2: кульминация {len(words(cl))} слов > {CLIMAX_WORDS} — сжать в одну короткую фразу")
    sk = [x for x in p.get("skeleton") or [] if _filled(x)]
    if not SKELETON[0] <= len(sk) <= SKELETON[1]:
        err.append(f"Q4: скелет {len(sk)} продвижений, нужно {SKELETON[0]}–{SKELETON[1]}")
    # H1, H2 первая фраза и разговор
    first = (sentences(hook) or [""])[0]
    low = norm(hook)[:200]
    for w in WARMUP:
        if norm(w) in low:
            err.append(f"H1: разгон в начале («{w}») — тема и ставка в первой фразе, без «о канале»")
            break
    if not first:
        err.append("H1: нет секции HOOK")
    if "?" not in hook or not YOU.search(hook.lower()):
        err.append("H2: в хуке нет вопроса зрителю на «ты» — ролик должен стать разговором")
    # H4 варианты вступления
    if len([x for x in p.get("hook_candidates") or [] if _filled(x)]) < 10:
        err.append("H4: вариантов вступления меньше 10 (hook_candidates)")
    if len([x for x in p.get("hook_voiced") or [] if _filled(x)]) < 2:
        err.append("H4: озвучено и прослушано меньше двух вариантов вступления (hook_voiced)")
    # P1–P5 пункты
    if len(blocks) < 3:
        err.append(f"P1: пунктов (=== BLOCK …) {len(blocks)} < 3")
    pts = p.get("points") or []
    by_block = {norm(x.get("block")): x for x in pts}
    emos = set()
    for n, t in blocks:
        pt = by_block.get(norm(n)) or by_block.get(norm(n.split(":")[0]))
        if not pt:
            err.append(f"P2: у «{n}» нет записи в passport.points (rehook, unpack, unpack_quote, payoff_quote, emotion)")
            continue
        head = norm(" ".join(sentences(t)[:2]))
        if not _filled(pt.get("rehook")) or norm(pt["rehook"]) not in head:
            err.append(f"P2: «{n}» не начинается своим хуком (rehook дословно в первых двух предложениях)")
        un, pay, body = norm(pt.get("unpack_quote")), norm(pt.get("payoff_quote")), norm(t)
        if pt.get("unpack") not in ("story", "metaphor"):
            err.append(f"P3: «{n}»: unpack — story или metaphor")
        if not un or un not in body:
            err.append(f"P3: «{n}»: история или метафора (unpack_quote) не найдена в тексте блока")
        elif not pay or pay not in body:
            err.append(f"P3: «{n}»: вывод (payoff_quote) не найден в тексте блока")
        elif body.index(un) > body.index(pay):
            err.append(f"P3: «{n}»: вывод звучит раньше истории — ответ выплачен сразу, кривая уйдёт ступенькой")
        if "?" not in t:
            err.append(f"P4: в «{n}» нет вопроса зрителю")
        if _filled(pt.get("emotion")):
            emos.add(norm(pt["emotion"]))
    if blocks and len(emos) < EMOTIONS_MIN:
        err.append(f"P5: эмоций по пунктам {len(emos)} < {EMOTIONS_MIN} — волна, а не ровная линия")
    # E1 конец
    eh = p.get("end_hook") or ""
    if not final_txt:
        err.append("E1: нет секции FINAL")
    elif not _filled(eh) or norm(eh) not in norm(final_txt):
        err.append("E1: конец-хук (end_hook) не стоит в FINAL дословно")
    for g in GOODBYE:
        if norm(g) in norm(final_txt):
            err.append(f"E1: «{g}» в конце — конец должен вести дальше, а не прощаться")
    # R1 правка
    rv = p.get("revision") or {}
    before, after = rv.get("words_before") or 0, rv.get("words_after") or 0
    now = len(words(spoken))
    if not before or not after:
        err.append("R1: нет замера правки (revision.words_before / words_after)")
    else:
        if after > before * (1 - CUT_SHARE):
            err.append(f"R1: правка вырезала {100 * (1 - after / before):.0f} % < {100 * CUT_SHARE:.0f} %")
        if abs(now - after) > max(10, 0.03 * after):
            err.append(f"R1: words_after {after}, а в тексте сейчас {now} слов — замер не от этого текста")
    # R3 цифры
    facts = {str(k) for k in (p.get("facts") or {})}
    for num in sorted(set(re.findall(r"\d+(?:[.,]\d+)?", spoken))):
        if num not in facts:
            err.append(f"R3: у цифры «{num}» нет источника в passport.facts")
    # R4 человеческий текст
    for i, m in human_issues([t for _, t in secs]):
        err.append(f"R4: {secs[i][0]}: {m}")
    # A1 одобрение
    ap = p.get("approved") or {}
    for k in ("title", "hook", "script"):
        if ap.get(k) is not True:
            err.append(f"A1: владелец не одобрил {k} — до плана кадров, картинок и озвучки нельзя")
    # decide-пункты
    got = p.get("items") or {}
    for it in items:
        if it["kind"] != "decide":
            continue
        d = got.get(it["id"])
        if not isinstance(d, dict) or not (_filled(d.get("how")) or _filled(d.get("skip"))):
            err.append(f"{it['id']}: нет решения — {it['rule']}")
    # хук и надписи — как у нынешних рилсов, с раскадровки
    err += hook_build(video_dir)
    # F1–F4 проверки готового ролика
    if final:
        fc = p.get("final_checks") or {}
        if not [x for x in fc.get("viewer_watch") or [] if _filled(x)]:
            err.append("F1: нет пометок просмотра целиком как зритель (final_checks.viewer_watch)")
        for k, rid, what in (("distraction_test", "F2", "теста на отвлечение"),
                             ("phone_audio", "F3", "проверки звука с телефона без наушников"),
                             ("outsider", "F4", "показа вступления человеку не из ниши")):
            if not _filled(fc.get(k)):
                err.append(f"{rid}: нет {what} (final_checks.{k})")
    return err


# ── Хук длинного ролика — как у нынешних рилсов (владелец 04.11: «проверь, динамичный ли хук как в рилсах нынешних и
# имеются ли все sfx… субтитры не надо, но не забывай про все надписи поясняющие»). Действует с раскадровки
# (storyboard.json) для всех длинных роликов, кроме двух уже собранных (LEGACY): у L01/L02 влёт без удара и 5 звуков за
# первые 10 с — ниже эталона рилс 17. Пороги — те же, что у рилсов (reel_rules, правила 28–29), без своих чисел.
LEGACY = {"L01_potom", "L02_otvlechenie"}
EST_WPS = 2.4               # темп L02 до озвучки (слов в секунду); после озвучки — время слов из alignment
LABEL_EVERY_SEC = 30        # поясняющая надпись (жирный текст fx.json, мысль key или акцент accent) не реже раза в 30 с
LABEL_GAP_MAX = 45          # и без дыры больше 45 с между надписями
HOOK_CAM_RE = re.compile(r"hook_cam\(\s*t\s*,\s*hit\s*=")


def _phrase_times(video_dir, blocks):
    """Начало и длина каждой фразы: по alignment, если ролик озвучен, иначе оценка по словам (EST_WPS) и паузам."""
    try:
        from speech_timing import SpeechTiming
        on = SpeechTiming(video_dir).onsets(blocks)
    except Exception:
        on = None
    est, acc = [], 0.0
    for b in blocks:
        est.append(acc)
        acc += max(1, b["words"]) / EST_WPS + b.get("pause_after", 0.0)
    starts = [0.0] + list(on[1:]) if on else est
    ends = starts[1:] + [acc if not on else starts[-1] + max(1, blocks[-1]["words"]) / EST_WPS]
    return starts, ends


def hook_build(video_dir):
    """Дыры хука и надписей по раскадровке, сцене и звукам (пусто — как у нынешних рилсов). Без storyboard.json — []."""
    sb_path = os.path.join(video_dir, "storyboard.json")
    if os.path.basename(os.path.normpath(video_dir)) in LEGACY or not os.path.exists(sb_path):
        return []
    import script_parser
    from reel_rules import SOUND_DENSITY_MIN, SOUND_GAP_MAX, SOUND_KINDS_MIN
    err = []
    sb = json.load(open(sb_path, encoding="utf-8"))
    frames = dict(sb.get("frames") or [])
    blocks = script_parser.parse_blocks(os.path.join(video_dir, "script.txt"))
    hook_n = sum(1 for b in blocks if b.get("section") == "HOOK")
    starts, ends = _phrase_times(video_dir, blocks)
    hook_end = ends[hook_n - 1] if hook_n else 0.0
    # 1. сцена движения на первой фразе, влёт с ударом (правила 28–29)
    a = (frames.get("1") or {}).get("anim")
    path = os.path.join(video_dir, "anim", f"{a}.py") if a else None
    if not a:
        err.append("HOOK-MOTION: у первой фразы нет сцены движения (storyboard frames[1].anim) — хук стоит, как "
                   "фото; нужен рисунок, который двигается с кадра 0 (скилл reel-anim, HyperFrames)")
    elif not os.path.exists(path):
        err.append(f"HOOK-MOTION: сцены anim/{a}.py ещё нет — хук без движения не собирается")
    elif not HOOK_CAM_RE.search(open(path, encoding="utf-8").read()):
        err.append(f"HOOK-MOTION: anim/{a}.py — камера не anim.hook_cam(t, hit=…): влёт без удара на ударном слоге "
                   "слабее эталона рилс 17 (правило 29)")
    # 2. звуки хука — плотность рилса (≥ 5 на 10 с, ≥ 5 разных, тишина ≤ 3,5 с)
    sp = os.path.join(video_dir, "sfx.json")
    ev = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else []
    peaks, kinds = [], set()
    for e in ev:
        i = int(e.get("phrase", 0)) - 1
        if not 0 <= i < hook_n:
            continue
        t = starts[i] + e.get("at", 0.0)
        if "word" in e:                      # до озвучки слово — по его месту во фразе
            ws = words(script_parser.strip_pipeline_only_tags(blocks[i]["text"]))
            stem = norm(e["word"])
            k = next((j for j, w in enumerate(ws) if norm(w).startswith(stem)), None)
            if k is None:
                err.append(f"HOOK-SFX: «{e.get('name')}»: слова «{e['word']}» нет во фразе {i + 1}")
                continue
            t = starts[i] + (ends[i] - starts[i]) * k / max(1, len(ws)) + e.get("offset", 0.0)
        peaks.append(t); kinds.add(e.get("name"))
    if hook_end:
        dens = len(peaks) / hook_end * 10
        if dens < SOUND_DENSITY_MIN:
            err.append(f"HOOK-SFX: в хуке ({hook_end:.0f} с) звуков {len(peaks)} — {dens:.1f} на 10 с < "
                       f"{SOUND_DENSITY_MIN} (эталон рилс 17 — 5,7): свист на каждой склейке, удар на событии рисунка, "
                       "звук на смысловом слове")
        if len(kinds) < SOUND_KINDS_MIN:
            err.append(f"HOOK-SFX: разных звуков в хуке {len(kinds)} < {SOUND_KINDS_MIN}")
        pts = [0.0] + sorted(peaks) + [hook_end]
        gap, at = max((b - a_, a_) for a_, b in zip(pts, pts[1:]))
        if gap > SOUND_GAP_MAX:
            err.append(f"HOOK-SFX: тишина без звуков {gap:.1f} с с {at:.1f} с > {SOUND_GAP_MAX} с")
    # 3. поясняющие надписи по всему ролику (субтитров нет, текст на экране — надписи)
    fp = os.path.join(video_dir, "fx.json")
    fx = (json.load(open(fp, encoding="utf-8")).get("phrases") or {}) if os.path.exists(fp) else {}
    lab = sorted({int(k) for k, v in frames.items() if str(k).isdigit() and (v.get("key") or v.get("accent"))}
                 | {int(k) for k, v in fx.items() if v.get("bold")})
    total = ends[-1] if ends else 0.0
    need = int(total // LABEL_EVERY_SEC)
    if len(lab) < need:
        err.append(f"LABELS: поясняющих надписей {len(lab)} на {total / 60:.1f} мин < {need} (одна на "
                   f"{LABEL_EVERY_SEC} с): жирный текст fx.json на цифрах и обещаниях, мысль key или акцент accent")
    pts = [0.0] + [starts[i - 1] for i in lab if 0 < i <= len(starts)] + [total]
    gap, at = max((b - a_, a_) for a_, b in zip(pts, pts[1:]))
    if gap > LABEL_GAP_MAX:
        err.append(f"LABELS: {gap:.0f} с без единой надписи с {at / 60:.1f} мин > {LABEL_GAP_MAX} с")
    return err


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("video_dir")
    ap.add_argument("--final", action="store_true", help="плюс проверки готового ролика F1–F4")
    ap.add_argument("--template", action="store_true", help="записать заготовку long_passport.json")
    a = ap.parse_args()
    vd = os.path.abspath(a.video_dir)
    if a.template:
        p = os.path.join(vd, PASSPORT)
        if os.path.exists(p):
            sys.exit(f"{p} уже есть — не перезаписываю")
        json.dump(template(), open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"Заготовка: {p}")
        return
    err = check(vd, final=a.final)
    for e in err:
        print("✗", e)
    print(f"Структура длинного ролика: {'соблюдена' if not err else f'{len(err)} дыр'}")
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
