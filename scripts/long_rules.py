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
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from reel_rules import human_issues  # noqa: E402  (тот же «человеческий текст», что у рилсов)
from long_sfx import MOTION_SNAP_SEC, MOTION_SOUNDS  # noqa: E402  (свист — звук движения: правило и сборка одни)

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
# Надписи — не по таймеру, а по смыслу, всегда (владелец 04.11: «их должно быть больше… не в какое-то количество
# времени, а просто когда нужно, всегда»). Фраза, где звучит число, имя или название, приём, «Напарник» или
# кульминация, несёт надпись: жирный текст fx.json или карандаш (key / accent раскадровки). Не нужна — fx.json
# phrases[N].nolabel = {"why": …} словами.
LABEL_NUM_RE = re.compile(
    r"\b(\d+|два|две|двух|двум|три|тр[её]х|четыре|четыр[её]х|пять|пяти|шесть|шести|семь|семи|восемь|восьми|восемью|"
    r"девять|девяти|десять|десяти|десят(ая|ой|ую|ый|ом)|одиннадцат\w*|двенадцат\w*|пятнадцат\w*|двадцат\w*|"
    r"тридцат\w*|сорок\w*|пятьдесят|пятидесяти|шестьдесят|семьдесят|семидесяти|восемьдесят|девяносто|сто|ста|"
    r"сотн\w*|тысяч\w*|половин\w*|треть|трети|четверть|четверти|двухминутн\w*)\b")
LABEL_TERM_RE = re.compile(r"\b(при[её]м\w*|напарник\w*)\b")
LONG_SFX_PER_10S = 3.0      # звуков в длинном ролике — не меньше 3 в каждом куске 10 с (владелец 04.11, вечер: «было 4,
LONG_SFX_WINDOW = 10.0      # теперь 3… как будто слишком много звуков… плавающие 3–4, по смыслу, не хардкод шаблон»)
LONG_SFX_MEAN_MAX = 4.0     # и в среднем после хука не больше 4 на 10 с: кусок с важным событием может нести 5–6,
                            # тогда соседние тише; хук — по правилам рилса (там звуков больше, правило 29)
LONG_SFX_GAP_MAX = 6.0      # после хука тишина без звуков не длиннее 6 с (L03 до правки: 4,6 звука на 10 с)
MANUAL_MONTAGE_SEC = 180    # первые 3 минуты — монтаж руками, без автоматики (владелец 04.11: «ручной у тебя будет на
                            # 3 минуты… собственноручно, по смыслу, без шаблонности и автоматики»); хук 40–60 с — как рилс
MANUAL_MAX_SHOT = 3.5       # план ручных минут после хука — не дольше нормы ролика (shots.MAX_VIEW_SEC)
VIDEO_HOOK_MIN_SEC = 40     # «видеохук» — весь HOOK, но не короче 40 с (владелец 04.11: «первые 40–60 секунд… как рилс»)
PICTURE_EVERY_SEC = 7.0     # новая картинка в видеохуке не реже раза в 7 с (рилс 17: 6 рисунков на 35 с)
VIDEO_HOOK_MEAN_SHOT = 2.2  # средний план видеохука (рилс 17 — 1,67 с; L02 в хуке — автоматика до 3,5 с)
HOOK_CAM_RE = re.compile(r"hook_cam\(\s*t\s*,\s*hit\s*=")


_WORD_TIMES = {}            # video_dir -> время слов фраз из alignment (после озвучки), для _word_t


def _phrase_times(video_dir, blocks):
    """Начало и длина каждой фразы: по alignment, если ролик озвучен, иначе оценка по словам (EST_WPS) и паузам."""
    try:
        from speech_timing import SpeechTiming
        st = SpeechTiming(video_dir)
        on = st.onsets(blocks)
        _WORD_TIMES[os.path.abspath(video_dir)] = st.word_times if on else None
    except Exception:
        on = None
    est, acc = [], 0.0
    for b in blocks:
        est.append(acc)
        acc += max(1, b["words"]) / EST_WPS + b.get("pause_after", 0.0)
    starts = [0.0] + list(on[1:]) if on else est
    ends = starts[1:] + [acc if not on else starts[-1] + max(1, blocks[-1]["words"]) / EST_WPS]
    return starts, ends


def _word_t(blocks, starts, ends, idx, at, wt=None):
    """Время момента в клипе картинки (фразы idx, с 0: своя и поглощённые absorb): секунды от начала клипа или слово
    (["слово", k] — k-е вхождение, как в long_edit.word_time) — до озвучки по месту слова во фразе. Нет слова — None."""
    import script_parser
    if isinstance(at, (int, float)):
        return starts[idx[0]] + float(at)
    stem, k = (at, 1) if isinstance(at, str) else (at[0], int(at[1]))
    if wt:                                   # ролик озвучен — настоящее время слова
        for i in idx:
            for w in (wt[i] if i < len(wt) else []):
                if norm(w["word"]).startswith(norm(stem)):
                    k -= 1
                    if not k:
                        return w["start"]
        return None
    for i in idx:
        ws = words(script_parser.strip_pipeline_only_tags(blocks[i]["text"]))
        for j, w in enumerate(ws):
            if norm(w).startswith(norm(stem)):
                k -= 1
                if not k:
                    return starts[i] + (ends[i] - starts[i]) * j / max(1, len(ws))
    return None


def _video_hook_montage(video_dir, blocks, frames, starts, ends, hook_n, fx_path):
    """Видеохук длинного ролика спроектирован как рилс (владелец 04.11: «не просто слайд-шоу»). Зона — весь HOOK, но не
    короче VIDEO_HOOK_MIN_SEC. Пороги — рилсовые (reel_rules): план MIN_SHOT_SEC–MAX_SHOT_SEC, первая склейка ≤
    FIRST_CUT_SEC, акцентов ≥ ACCENT_PER_10S на 10 с и ≥ ACCENT_KINDS_MIN видов."""
    from reel_rules import ACCENT_KINDS_MIN, ACCENT_PER_10S, FIRST_CUT_SEC, MAX_SHOT_SEC, MIN_SHOT_SEC
    err = []
    zone = max(ends[hook_n - 1] if hook_n else 0.0, VIDEO_HOOK_MIN_SEC)
    zn = [i for i in range(len(blocks)) if starts[i] < zone - 0.5]          # фразы видеохука (с 0)
    pic = [i for i in zn if {"new", "lib", "same", "plan", "anim"} & set(frames.get(str(i + 1)) or {})]   # своя картинка
    if not pic or pic[0] != 0:
        err.append("VIDEO-HOOK: у первой фразы нет своей картинки в раскадровке")
        return err
    need = int(zone // PICTURE_EVERY_SEC)
    if len(pic) < need:
        err.append(f"VIDEO-HOOK: картинок в видеохуке ({zone:.0f} с) {len(pic)} < {need} — новая картинка не реже раза в "
                   f"{PICTURE_EVERY_SEC:.0f} с, как в рилсе (рилс 17: 6 на 35 с)")
    ep = os.path.join(video_dir, "edit.json")
    edit = (json.load(open(ep, encoding="utf-8")).get("frames") or {}) if os.path.exists(ep) else {}
    cuts, acc, missing = [], [], False
    for n, i in enumerate(pic):
        nxt = pic[n + 1] if n + 1 < len(pic) else zn[-1] + 1
        sh = (edit.get(str(i + 1)) or {}).get("shots") or []
        if not sh:
            err.append(f"VIDEO-HOOK: картинка фразы {i + 1} без ручного монтажа (edit.json) — в видеохуке нет "
                       "автоматической раскладки, каждый план со смыслом и why, как в рилсе")
            missing = True
            continue
        for k, p in enumerate(sh):
            if not (p.get("why") or "").strip():
                err.append(f"VIDEO-HOOK: фраза {i + 1}, план {k + 1}: нет why — монтаж со смыслом, а не ради склейки")
            t = starts[i] if k == 0 else _word_t(blocks, starts, ends, list(range(i, nxt)), p.get("at", 0.0),
                                                    _WORD_TIMES.get(os.path.abspath(video_dir)))
            if t is None:
                err.append(f"VIDEO-HOOK: фраза {i + 1}, план {k + 1}: слова «{p.get('at')}» нет во фразе")
                continue
            cuts.append(t)
            cuts += _stage_beats(p, blocks, starts, ends, list(range(i, nxt)), video_dir)
            if p.get("stage"):
                acc.append(("stage", t))
            for kind in ("punch", "shake", "spot", "whip", "parallax"):
                if p.get(kind):
                    acc.append((kind, t))
    if (frames.get("1") or {}).get("anim"):
        acc.append(("anim", 0.0))
    for i in zn:
        v = frames.get(str(i + 1)) or {}
        for kind in ("key", "accent"):
            if v.get(kind):
                acc.append((kind, starts[i]))
    fx = (json.load(open(fx_path, encoding="utf-8")).get("phrases") or {}) if os.path.exists(fx_path) else {}
    for i in zn:
        v = fx.get(str(i + 1)) or {}
        acc += [("bold", starts[i])] * len(v.get("bold") or [])
        acc += [("hand", starts[i])] * len(v.get("hand") or [])
        if v.get("narrator"):
            acc.append(("narrator", starts[i]))
    cuts = sorted(set(round(c, 2) for c in cuts))
    if not missing and cuts:
        if len(cuts) > 1 and cuts[1] > FIRST_CUT_SEC + 0.02:
            err.append(f"VIDEO-HOOK: первая склейка на {cuts[1]:.1f} с > {FIRST_CUT_SEC} — «решают первые 1–2 секунды»")
        cuts = [c for c in cuts if c < zone]                 # за краем видеохука — обычный монтаж ролика
        plans = [(a, b - a) for a, b in zip(cuts, cuts[1:] + [min(zone, ends[zn[-1]])]) if b > a]
        for a, d in plans:
            if d > MAX_SHOT_SEC + 0.05:
                err.append(f"VIDEO-HOOK: план с {a:.1f} с идёт {d:.1f} с > {MAX_SHOT_SEC} — разрежьте вторым планом")
            elif d < MIN_SHOT_SEC - 0.05:
                err.append(f"VIDEO-HOOK: план с {a:.1f} с идёт {d:.2f} с < {MIN_SHOT_SEC} — не читается")
        if plans:
            mean = sum(d for _, d in plans) / len(plans)
            if mean > VIDEO_HOOK_MEAN_SHOT:
                err.append(f"VIDEO-HOOK: средний план {mean:.1f} с > {VIDEO_HOOK_MEAN_SHOT} (рилс 17 — 1,67 с) — больше смен плана")
    rate = len(acc) / zone * 10
    if rate < ACCENT_PER_10S:
        err.append(f"VIDEO-HOOK: акцентов {len(acc)} за {zone:.0f} с — {rate:.1f} на 10 с < {ACCENT_PER_10S}: удар-наезд, "
                   "тряска, прожектор, хлёст, жирный текст, мысль карандашом, котик-ведущий — на смысловых словах")
    kinds = {k for k, _ in acc}
    if len(kinds) < ACCENT_KINDS_MIN:
        err.append(f"VIDEO-HOOK: видов акцентов {len(kinds)} ({', '.join(sorted(kinds)) or 'нет'}) < {ACCENT_KINDS_MIN}")
    return err


def label_needs(text, climax=""):
    """Почему фразе нужна надпись на экране (пусто — не нужна): число, имя или название, приём, «Напарник», кульминация."""
    low = text.lower()
    why = []
    if LABEL_NUM_RE.search(low):
        why.append("число")
    for sent in re.split(r"(?<=[.!?…])\s+", text):
        toks = [t.strip("«»\"'(),:;—–-.!?") for t in sent.split()][1:]
        if any(t and t[0].isupper() and t != "Я" and not t.lower().startswith("напарник") for t in toks):
            why.append("имя или название")
            break
    if LABEL_TERM_RE.search(low):
        why.append("приём или «Напарник»")
    if climax and climax in norm(text):
        why.append("кульминация")
    return ", ".join(why)


def _manual_minutes(video_dir, blocks, frames, starts, ends):
    """Каждая картинка, которая начинается в первые MANUAL_MONTAGE_SEC, смонтирована руками в edit.json (у плана why);
    планы не дольше MANUAL_MAX_SHOT (в хуке строже — _video_hook_montage)."""
    err = []
    ep = os.path.join(video_dir, "edit.json")
    edit = (json.load(open(ep, encoding="utf-8")).get("frames") or {}) if os.path.exists(ep) else {}
    pic = [i for i in range(len(blocks)) if {"new", "lib", "same", "plan", "anim"} & set(frames.get(str(i + 1)) or {})]
    for n, i in enumerate(pic):
        if starts[i] >= MANUAL_MONTAGE_SEC:
            break
        nxt = pic[n + 1] if n + 1 < len(pic) else len(blocks)
        f_end = starts[nxt] if nxt < len(blocks) else ends[-1]
        sh = (edit.get(str(i + 1)) or {}).get("shots") or []
        if not sh:
            err.append(f"MANUAL: картинка фразы {i + 1} ({int(starts[i] // 60)}:{int(starts[i] % 60):02d}) без ручного монтажа — "
                       f"первые {MANUAL_MONTAGE_SEC // 60} минуты монтируются руками (edit.json, why у каждого плана)")
            continue
        ts = []
        for k, p in enumerate(sh):
            if not (p.get("why") or "").strip():
                err.append(f"MANUAL: фраза {i + 1}, план {k + 1}: нет why")
            t = starts[i] if k == 0 else _word_t(blocks, starts, ends, list(range(i, nxt)), p.get("at", 0.0),
                                                    _WORD_TIMES.get(os.path.abspath(video_dir)))
            if t is None:
                err.append(f"MANUAL: фраза {i + 1}, план {k + 1}: слова «{p.get('at')}» нет в клипе картинки")
                continue
            ts.append(t)
            ts += _stage_beats(p, blocks, starts, ends, list(range(i, nxt)), video_dir)
        ts = sorted(ts) + [f_end]
        for a, b in zip(ts, ts[1:]):
            if b - a > MANUAL_MAX_SHOT + 0.3 and a < MANUAL_MONTAGE_SEC:
                err.append(f"MANUAL: план с {int(a // 60)}:{a % 60:04.1f} идёт {b - a:.1f} с > {MANUAL_MAX_SHOT} — вторым планом по смыслу")
    return err


def _stage_beats(p, blocks, starts, ends, idx, video_dir):
    """Моменты внутри сцены на бумаге (появление элемента, сдвиг карточки) — для темпа они как склейки: сцена с тремя
    событиями за 4 с не «план 4 с»."""
    sp = p.get("stage")
    if not sp:
        return []
    els = sp.get("items") or sp.get("cards") or []
    out = []
    for at in [e.get("at") for e in els] + [sp.get("focus_at")]:
        if at:
            t = _shot_t(video_dir, blocks, starts, ends, idx, at)     # тем же поиском слова, что у сборщика
            if t is not None:
                out.append(t)
    return out


TEXT_WHY_RE = re.compile(r"влета|на экран|появля|надпис|строк[аиуе]|подпис|пишется|дописан", re.I)
CUT_WHY_RE = re.compile(r"склейк|смена плана|новая картинка|переход на|влёт картинки", re.I)
GENERIC_WHY_RE = re.compile(r"\W*(общий|средний|крупный|ещё один|другой)?\s*(план|кадр)\W*|\W*смена плана\W*|\W*склейка\W*",
                            re.I)


def edit_sounds(video_dir, blocks, frames, starts, ends):
    """[(время, фраза, звук)] звуков склеек: план монтажа с "sound" — на начале своего плана (первый — на начале
    картинки), тем же поиском слова, что у сборщика."""
    ep = os.path.join(video_dir, "edit.json")
    if not os.path.exists(ep):
        return []
    import long_edit
    edit = json.load(open(ep, encoding="utf-8")).get("frames") or {}
    wt = _WORD_TIMES.get(os.path.abspath(video_dir))
    pic = [i for i in range(len(blocks)) if {"new", "lib", "same", "plan", "anim"} & set(frames.get(str(i + 1)) or {})]
    out = []
    for n, i in enumerate(pic):
        nxt = pic[n + 1] if n + 1 < len(pic) else len(blocks)
        ws = [dict(word=w["word"], start=w["start"] - starts[i]) for k in range(i, nxt) for w in wt[k]] if wt else None
        for k, p in enumerate((edit.get(str(i + 1)) or {}).get("shots") or []):
            sp = p.get("stage")
            if sp and ws is not None:                     # появления и сдвиги сцены на бумаге — на своих словах
                els = sp.get("items") or sp.get("cards") or []
                marks = [(e.get("at"), e.get("sound")) for e in els] + [(sp.get("focus_at"), sp.get("focus_sound"))]
                for at, snd in marks:
                    if at and snd:
                        try:
                            out.append((starts[i] + long_edit.word_time(at, ws), i, snd))
                        except ValueError:
                            pass
            if not p.get("sound"):
                continue
            if k == 0:
                t = starts[i]
            elif ws is not None:
                try:
                    t = starts[i] + long_edit.word_time(p.get("at", 0.0), ws)
                except ValueError:
                    continue
            else:
                t = _word_t(blocks, starts, ends, list(range(i, nxt)), p.get("at", 0.0))
            if t is not None:
                out.append((t, i, p["sound"]))
    return out


def motion_events(video_dir, blocks, frames, starts, ends):
    """Моменты движения на экране по ручному монтажу (edit.json): начало картинки, склейки планов, появления и сдвиги
    сцены на бумаге — тем же поиском слова, что у сборщика. Картинки без ручного монтажа — None (их склейки выбирает
    сборщик, до сборки их нет)."""
    ep = os.path.join(video_dir, "edit.json")
    edit = (json.load(open(ep, encoding="utf-8")).get("frames") or {}) if os.path.exists(ep) else {}
    pic = [i for i in range(len(blocks)) if {"new", "lib", "same", "plan", "anim"} & set(frames.get(str(i + 1)) or {})]
    out = []
    for n, i in enumerate(pic):
        nxt = pic[n + 1] if n + 1 < len(pic) else len(blocks)
        shots = (edit.get(str(i + 1)) or {}).get("shots")
        if not shots or (frames.get(str(i + 1)) or {}).get("anim"):   # сцена движения: рисунок движется сам, свист
            out.append((i, nxt, None))                                  # на её событии законен (рилсы так же)
            continue
        idx = list(range(i, nxt))
        ts = [starts[i]]
        for k, p in enumerate(shots):
            if k:
                t = _shot_t(video_dir, blocks, starts, ends, idx, p.get("at", 0.0))
                if t is not None:
                    ts.append(t)
            ts += _stage_beats(p, blocks, starts, ends, idx, video_dir)
        out.append((i, nxt, ts))
    return out


def _shot_t(video_dir, blocks, starts, ends, idx, at):
    """Время плана тем же поиском слова, что у сборщика (long_edit.word_time: сначала слово целиком, потом начало)."""
    wt = _WORD_TIMES.get(os.path.abspath(video_dir))
    if wt:
        import long_edit
        ws = [dict(word=w["word"], start=w["start"] - starts[idx[0]]) for k in idx for w in wt[k]]
        try:
            return starts[idx[0]] + long_edit.word_time(at, ws)
        except ValueError:
            return None
    return _word_t(blocks, starts, ends, idx, at)


def motion_sounds(video_dir, blocks, frames, starts, ends, motion):
    """Свист из sfx.json — только на движении (long_sfx.MOTION_SOUNDS): не дальше MOTION_SNAP_SEC от склейки или
    появления элемента сцены (сборщик ставит его ровно на их кадр). Свист в пустоту — ошибка: звук движения у события
    (план edit.json, элемент сцены, надпись fx.json "sound") или звук смысла на слове."""
    err = []
    spans = motion_events(video_dir, blocks, frames, starts, ends)
    for t, i, e in motion:
        span = next((s for s in spans if s[0] <= i < s[1]), None)
        if span is None or span[2] is None:
            continue
        d = min(abs(t - m) for m in span[2])
        if d > MOTION_SNAP_SEC + 1e-6:
            err.append(f"SFX: свист «{e['name']}» во фразе {i + 1} на «{e['word']}» ({e.get('why')}) — в {d:.2f} с от "
                       f"ближайшего движения на экране: звук движения ставится у самого события (план edit.json "
                       f"\"sound\", элемент сцены, надпись fx.json \"sound\") или меняется на звук смысла")
    return err


def text_sounds(video_dir, blocks, starts, ends):
    """[(время, фраза, звук)] звуков надписей fx.json ("sound" у bold/hand, у подписи — с приставкой «hand:»): на слове
    надписи, строка кота-ведущего —
    не раньше, чем он сел (long_fx.bold_after_narrator; точное время ставит сборщик по отрисовке)."""
    fp = os.path.join(video_dir, "fx.json")
    if not os.path.exists(fp):
        return []
    import long_fx
    ready = long_fx.ENTER_SEC + long_fx.GROW_SEC + long_fx.SETTLE_SEC + long_fx.BOLD_AFTER_NARRATOR
    out = []
    for n, v in (json.load(open(fp, encoding="utf-8")).get("phrases") or {}).items():
        i = int(n) - 1
        if not 0 <= i < len(blocks):
            continue
        for kind in ("bold", "hand"):
            for e in v.get(kind) or []:
                if not e.get("sound"):
                    continue
                t = _shot_t(video_dir, blocks, starts, ends, [i], e["word"]) if e.get("word") else None
                t = starts[i] + 0.3 if t is None else t
                if kind == "bold" and v.get("narrator"):
                    t = max(t, starts[i] + ready)
                out.append((t, i, ("hand:" if kind == "hand" else "") + e["sound"]))
    return out


def stage_checks(video_dir):
    """Сцены на бумаге (edit.json "stage", long_stage): вид items (1–3 вырезки) или cards (ровно две карточки), у
    вырезки — рамка box или многоугольник poly, исходник существует, подпись — до трёх слов."""
    ep = os.path.join(video_dir, "edit.json")
    if not os.path.exists(ep):
        return []
    import long_stage
    err = []
    for n, v in (json.load(open(ep, encoding="utf-8")).get("frames") or {}).items():
        for k, p in enumerate(v.get("shots") or [], 1):
            sp = p.get("stage")
            if not sp:
                continue
            where = f"STAGE: фраза {n}, план {k}"
            kind = sp.get("type")
            els = sp.get("items") if kind == "items" else sp.get("cards") if kind == "cards" else None
            if els is None:
                err.append(f"{where}: вид сцены «{kind}» — items (вырезки) или cards (две карточки)")
                continue
            if kind == "items" and not 1 <= len(els) <= 3:
                err.append(f"{where}: вырезок {len(els)} — от одной до трёх, иначе мелко и не читается")
            if kind == "cards" and len(els) != 2:
                err.append(f"{where}: карточек {len(els)} — ровно две (сравнение, одна уезжает, другая на весь экран)")
            for e in els:
                src = e.get("src") or ""
                if kind == "items" and not (e.get("box") or e.get("poly")):
                    err.append(f"{where}: у вырезки {src} нет рамки box или многоугольника poly")
                if src.startswith("lib:") and not os.path.exists(long_stage.resolve_src(src, video_dir)):
                    err.append(f"{where}: в библиотеке нет {src[4:]}")
                if len((e.get("label") or "").split()) > 3:
                    err.append(f"{where}: подпись «{e['label']}» длиннее трёх слов")
    return err


def generic_whys(video_dir):
    """Планы монтажа без смысла в why («общий план», «смена плана»): склейка ради ритма, а не по смыслу."""
    ep = os.path.join(video_dir, "edit.json")
    if not os.path.exists(ep):
        return []
    err = []
    for n, v in (json.load(open(ep, encoding="utf-8")).get("frames") or {}).items():
        for k, p in enumerate(v.get("shots") or [], 1):
            w = (p.get("why") or "").strip()
            if GENERIC_WHY_RE.fullmatch(w) or len(w.split()) < 2:
                err.append(f"EDIT-WHY: фраза {n}, план {k}: «{w}» — зачем план по смыслу (что зритель видит и на каком "
                           f"слове), а не «общий план»")
    return err


def _edit_order(video_dir, blocks, frames, starts):
    wt = _WORD_TIMES.get(os.path.abspath(video_dir))
    ep = os.path.join(video_dir, "edit.json")
    if not wt or not os.path.exists(ep):
        return []
    import long_edit
    edit = json.load(open(ep, encoding="utf-8")).get("frames") or {}
    pic = [i for i in range(len(blocks)) if {"new", "lib", "same", "plan", "anim"} & set(frames.get(str(i + 1)) or {})]
    err = []
    for n, i in enumerate(pic):
        nxt = pic[n + 1] if n + 1 < len(pic) else len(blocks)
        ws = [dict(word=w["word"], start=w["start"] - starts[i]) for k in range(i, nxt) for w in wt[k]]
        prev = 0.0
        for k, p in enumerate(((edit.get(str(i + 1)) or {}).get("shots") or [])[1:], 2):
            try:
                t = long_edit.word_time(p.get("at", 0.0), ws)
            except ValueError as e:
                err.append(f"EDIT-ORDER: фраза {i + 1}, план {k}: {e}")
                continue
            if t <= prev + 0.3:
                err.append(f"EDIT-ORDER: фраза {i + 1}, план {k} «{p.get('at')}» на {t:.2f} с не после прошлого ({prev:.2f} с): "
                           "слово звучит в клипе не раз — [\"слово\", номер вхождения]")
            prev = max(prev, t)
    return err


def hook_build(video_dir):
    """Дыры хука и надписей по раскадровке, сцене и звукам (пусто — как у нынешних рилсов). Без storyboard.json — []."""
    sb_path = os.path.join(video_dir, "storyboard.json")
    if os.path.basename(os.path.normpath(video_dir)) in LEGACY or not os.path.exists(sb_path):
        return []
    import script_parser
    from reel_rules import SOUND_GAP_MAX, SOUND_KINDS_MIN
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
    # 2. звуки — в каждом куске 10 с не меньше 3, после хука в среднем не больше 4 (владелец 04.11); в хуке ещё ≥ 5 разных и тишина ≤ 3,5 с
    sp = os.path.join(video_dir, "sfx.json")
    ev = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else []
    peaks, hook_kinds, motion = [], set(), []
    for e in ev:
        i = int(e.get("phrase", 0)) - 1
        if not 0 <= i < len(blocks):
            err.append(f"SFX: «{e.get('name')}»: фразы {e.get('phrase')} нет")
            continue
        if "word" not in e:                  # секунды от начала фразы промахиваются (L03: 3 свиста на 0,5–0,9 с мимо)
            err.append(f"SFX: «{e.get('name')}» во фразе {i + 1} без слова — звук на слово (word) или на склейку "
                       f"(edit.json, \"sound\" у плана): тогда он встаёт точно")
            continue
        if CUT_WHY_RE.search(e.get("why") or ""):
            err.append(f"SFX: «{e.get('name')}» во фразе {i + 1} — «{e.get('why')}»: звук склейки ставится у плана "
                       f"монтажа (edit.json \"sound\"), тогда его пик ровно на склейке, как в рилсах")
        elif TEXT_WHY_RE.search(e.get("why") or ""):
            err.append(f"SFX: «{e.get('name')}» во фразе {i + 1} — «{e.get('why')}»: звук надписи ставится у самой "
                       f"надписи (fx.json bold/hand \"sound\") — сборщик кладёт его на кадр, где она видна, после всех "
                       f"сдвигов (кот-ведущий, дописанная мысль)")
        t = _shot_t(video_dir, blocks, starts, ends, [i], e["word"])   # тем же поиском, что long_sfx.resolve:
        if t is None:                                                    # «кот» — это «кот,», а не «котик»
            err.append(f"SFX: «{e.get('name')}»: слова «{e['word']}» нет во фразе {i + 1}")
            continue
        peaks.append(t + e.get("offset", 0.0))
        if e.get("name") in MOTION_SOUNDS:
            motion.append((t + e.get("offset", 0.0), i, e))
        if i < hook_n:
            hook_kinds.add(e.get("name"))
    for t, i, name in edit_sounds(video_dir, blocks, frames, starts, ends):   # звуки склеек из монтажа
        peaks.append(t)
        if i < hook_n:
            hook_kinds.add(name)
    for t, i, name in text_sounds(video_dir, blocks, starts, ends):          # звуки надписей (fx.json "sound")
        if name.startswith("hand:"):
            name = name[5:]
            if name in MOTION_SOUNDS:     # подпись не влетает — её пишет карандаш со своим звуком
                err.append(f"SFX: свист «{name}» на рукописной подписи во фразе {i + 1}: подпись пишется карандашом "
                           f"(его звук уже есть), а не влетает — свист без движения; звук смысла — можно")
                continue
        peaks.append(t)
        if i < hook_n:
            hook_kinds.add(name)
    err += motion_sounds(video_dir, blocks, frames, starts, ends, motion)
    total = ends[-1] if ends else 0.0
    thin = []
    for a in range(0, int(math.ceil(total / LONG_SFX_WINDOW))):
        lo, hi = a * LONG_SFX_WINDOW, min(total, (a + 1) * LONG_SFX_WINDOW)
        need = LONG_SFX_PER_10S * (hi - lo) / LONG_SFX_WINDOW
        got = sum(lo <= p < hi for p in peaks)
        if hi - lo >= 3 and got < math.floor(need):
            thin.append(f"{int(lo // 60)}:{int(lo % 60):02d}–{int(hi // 60)}:{int(hi % 60):02d} ({got})")
    body = sorted(p for p in peaks if hook_end <= p < total)
    if total - hook_end >= LONG_SFX_WINDOW:
        mean = len(body)/(total - hook_end)*LONG_SFX_WINDOW
        if mean > LONG_SFX_MEAN_MAX + 1e-9:
            err.append(f"SFX: после хука в среднем {mean:.1f} звука на 10 с > {LONG_SFX_MEAN_MAX:.0f} — слишком часто "
                       f"(владелец 04.11): оставить удары на событиях, свисты на смене картинки, звуки на смысловых словах")
        pts = [hook_end] + body + [total]
        gap, at = max((b - a_, a_) for a_, b in zip(pts, pts[1:]))
        if gap > LONG_SFX_GAP_MAX:
            err.append(f"SFX: тишина без звуков {gap:.1f} с с {int(at // 60)}:{int(at % 60):02d} > {LONG_SFX_GAP_MAX:.0f} с")
    if thin:
        err.append(f"SFX: звуков меньше {LONG_SFX_PER_10S:.0f} на 10 с в {len(thin)} кусках из "
                   f"{int(math.ceil(total / LONG_SFX_WINDOW))}: {', '.join(thin[:8])}{' …' if len(thin) > 8 else ''} — "
                   "свист на смене картинки и плана, удар на событии рисунка, звук на смысловом слове (sfx.json, why)")
    if hook_end:
        if len(hook_kinds) < SOUND_KINDS_MIN:
            err.append(f"HOOK-SFX: разных звуков в хуке {len(hook_kinds)} < {SOUND_KINDS_MIN}")
        pts = [0.0] + sorted(p for p in peaks if p < hook_end) + [hook_end]
        gap, at = max((b - a_, a_) for a_, b in zip(pts, pts[1:]))
        if gap > SOUND_GAP_MAX:
            err.append(f"HOOK-SFX: тишина без звуков {gap:.1f} с с {at:.1f} с > {SOUND_GAP_MAX} с")
    # 3. видеохук смонтирован как рилс: ручной монтаж каждой картинки, планы 0,7–3 с, смены картинок, акценты
    err += _video_hook_montage(video_dir, blocks, frames, starts, ends, hook_n, fx_path=os.path.join(video_dir, "fx.json"))
    # 4. первые 3 минуты — ручной монтаж каждой картинки (после хука — планы не дольше нормы ролика)
    err += _manual_minutes(video_dir, blocks, frames, starts, ends)
    # 4а. планы ручного монтажа идут по порядку — тем же поиском слова, что у сборщика (long_edit.word_time): «я»,
    # «рядом», «это» звучат в длинном клипе не раз, и план вставал на первое вхождение (сборка L03 упала 04.11)
    err += _edit_order(video_dir, blocks, frames, starts)
    err += generic_whys(video_dir)
    err += stage_checks(video_dir)
    # 5. надписи — только где добавляют то, чего нет ни в картинке, ни сразу на слух, и не чаще лимита (владелец 04.11,
    # вечер: «рисунков карандашом слишком много… даже там, где не надо»; L03: 65 надписей на 7 мин — раз в 6,5 с)
    fp = os.path.join(video_dir, "fx.json")
    fx = (json.load(open(fp, encoding="utf-8")).get("phrases") or {}) if os.path.exists(fp) else {}
    err += label_density(video_dir, blocks, frames, fx, starts, ends, hook_end)
    err += narrator_rhythm(fx, starts, ends)
    err += text_share(frames, fx)
    return err


HOOK_LABEL_EVERY = 5.0  # в видеохуке — не чаще одной надписи в 5 с (там ещё удары, хлёсты, прожектор)
LABEL_WINDOW, LABEL_MAX = 60.0, 3   # после хука — не больше 3 надписей на любую минуту (одна в ~20 с)


def label_times(video_dir, blocks, frames, fx, starts, ends):
    """[(время, вид, текст)] всех надписей ролика: жирные и рукописные fx.json (на своём слове), мысль и акцент
    карандашом раскадровки (на своей картинке, с начала фразы)."""
    wt = _WORD_TIMES.get(os.path.abspath(video_dir))
    out = []
    for n, v in fx.items():
        i = int(n) - 1
        if not 0 <= i < len(blocks):
            continue
        for kind in ("bold", "hand"):
            if kind == "bold" and v.get("narrator"):    # строка кота-ведущего — его часть, её частоту держит
                continue                                  # narrator_rhythm (раз в 1,5–3 мин)
            for e in v.get(kind) or []:
                t = _word_t(blocks, starts, ends, [i], e["word"], wt) if e.get("word") else None
                out.append((starts[i] if t is None else t, kind, e.get("text", "")))
    for n, v in frames.items():
        i = int(n) - 1
        if 0 <= i < len(blocks) and {"new", "lib", "same", "plan", "anim"} & set(v):
            out += [(starts[i], k, v[k]) for k in ("key", "accent") if v.get(k)]
    return sorted(out)


def label_density(video_dir, blocks, frames, fx, starts, ends, hook_end):
    """Не больше одной надписи в HOOK_LABEL_EVERY с в видеохуке и LABEL_MAX на любые LABEL_WINDOW с после него.
    Надпись ставится там, где добавляет то, чего нет ни в картинке, ни сразу на слух: число, имя, название приёма,
    главный вывод. Повтор нарисованного («прыжок» у прыгающего кота, «скука» у скучающего) — не нужен."""
    err = []
    labels = label_times(video_dir, blocks, frames, fx, starts, ends)
    zone = max(hook_end, VIDEO_HOOK_MIN_SEC)
    hook = [x for x in labels if x[0] < zone]
    cap = int(zone // HOOK_LABEL_EVERY)
    if len(hook) > cap:
        err.append(f"LABELS: в видеохуке {len(hook)} надписей за {zone:.0f} с > {cap} (одна в {HOOK_LABEL_EVERY:.0f} с) — "
                   f"оставить те, что добавляют число, имя или суть, которых нет в картинке")
    body = [x for x in labels if x[0] >= zone]
    worst = None
    for k, (t0, _, _) in enumerate(body):
        inside = [x for x in body[k:] if x[0] < t0 + LABEL_WINDOW]
        if len(inside) > LABEL_MAX and (worst is None or len(inside) > len(worst[1])):
            worst = (t0, inside)
    if worst:
        t0, inside = worst
        err.append(f"LABELS: с {int(t0 // 60)}:{int(t0 % 60):02d} за минуту {len(inside)} надписей > {LABEL_MAX} "
                   f"({', '.join('«' + x[2] + '»' for x in inside)}) — надпись только там, где добавляет то, чего нет ни "
                   f"в картинке, ни на слух: число, имя, приём, главный вывод")
    return err


NARRATOR_NOT_BEFORE = 10.0                 # кот-ведущий (размытый фон) — не в первые 10 с ролика
NARRATOR_MIN_GAP, NARRATOR_MAX_GAP = 90.0, 180.0   # не чаще раза в 1,5 мин и не реже раза в 3 мин (владелец 04.11)


def narrator_rhythm(fx, starts, ends):
    """Кот-ведущий перед размытой сценой (fx.json narrator): не раньше 10-й секунды, между выходами не меньше 1,5 мин и
    не больше 3 мин (и от начала ролика до первого, и от последнего до конца). Где именно — по смыслу: прямое
    обращение к зрителю (why обязателен, long_fx.load)."""
    err = []
    total = ends[-1] if ends else 0.0
    ts = sorted(starts[int(n) - 1] for n, v in fx.items() if v.get("narrator") and 0 < int(n) <= len(starts))
    for n, v in fx.items():                      # кот говорит со зрителем, сцена размыта — карандашу там не место,
        if v.get("narrator") and not v.get("bold"):   # смысл несёт жирная строка (владелец 04.11)
            err.append(f"NARRATOR: фраза {n} — кот-ведущий без жирной строки (fx.json bold): при размытом фоне смысл "
                       f"всегда несёт жирный текст")
    early = [t for t in ts if t < NARRATOR_NOT_BEFORE]
    if early:
        err.append(f"NARRATOR: кот-ведущий на {early[0]:.1f} с — не в первые {NARRATOR_NOT_BEFORE:.0f} с ролика")
    def mmss(t):
        return f"{int(t // 60)}:{int(t % 60):02d}"
    for a, b in zip(ts, ts[1:]):
        if b - a < NARRATOR_MIN_GAP:
            err.append(f"NARRATOR: выходы на {mmss(a)} и {mmss(b)} — через {b - a:.0f} с, чаще раза в "
                       f"{NARRATOR_MIN_GAP / 60:.1f} мин")
    if total > NARRATOR_MAX_GAP:
        for a, b in zip([0.0] + ts, ts + [total]):
            if b - a > NARRATOR_MAX_GAP:
                err.append(f"NARRATOR: с {mmss(a)} до {mmss(b)} нет кота-ведущего {b - a:.0f} с — реже раза в "
                           f"{NARRATOR_MAX_GAP / 60:.0f} мин: поставить на прямое обращение к зрителю в этом куске")
    return err


HAND_SHARE_MIN = 0.60   # владелец 04.11: рукописного (подписи со стрелками, мысль, акцент) не меньше 60 %, жирного ≤ 40 %


def text_share(frames, fx):
    """Доля рукописного среди надписей ролика (владелец 04.11, по L03: «90 % занимает жирный шрифт, а я хочу, чтобы 60 %
    рисованный и только 40 % жирный… вдумчиво, не пихать»). Рукописное — fx.json hand (подпись со стрелкой к предмету),
    карандаш key и accent раскадровки; жирное — fx.json bold. Доля добирается не новыми подписями ради числа, а тем,
    что жирная строка остаётся только там, где сверху нужно пояснение (мысль героя, суть), остальное — рукой у предмета."""
    hand = sum(len((fx.get(n) or {}).get("hand") or []) for n in fx)
    hand += sum(bool(v.get(k)) for v in frames.values() for k in ("key", "accent")
                if {"new", "lib", "same", "plan", "anim"} & set(v))
    bold = sum(len((fx.get(n) or {}).get("bold") or []) for n in fx if not (fx.get(n) or {}).get("narrator"))
    if hand + bold and hand/(hand + bold) < HAND_SHARE_MIN - 1e-9:
        return [f"TEXT-SHARE: рукописных надписей {hand}, жирных {bold} — рукописного {hand/(hand + bold):.0%} < "
                f"{HAND_SHARE_MIN:.0%}: жирная строка — только поясняющая сверху, остальное — подпись рукой со стрелкой "
                f"к предмету (fx.json hand) или мысль карандашом; новых подписей ради доли не добавлять"]
    return []


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
