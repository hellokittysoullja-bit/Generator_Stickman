"""Правила рилса — кодом, а не памятью агента (22.10, по вопросу владельца: «новый агент с нуля не должен сделать хуже»).

Каждое правило проверено на рилсе эп.02 и названо по своему источнику (подробно — docs/REELS_PLAYBOOK.md).
`reel.py` зовёт `check` перед рендером и не рендерит рилс с ошибкой (`--force` — только осознанно, с причиной).

    python scripts/reel_rules.py videos/NN/reel     # проверить reel.json без рендера
"""
import json
import math
import os
import re

MAX_SHOT_SEC = 3.0         # план не дольше 3 с (разбор роликов о Reels: смена картинки каждые 2–3 с)
FIRST_CUT_SEC = 2.0        # первая склейка в первые 2 с — «решают первые 1–2 секунды» (владелец 22.10)
HOOK_MAX_CHARS = 30        # первая фраза читается за ~1.3–1.8 с при 17 знаках в секунду
RISER_START_MAX = 0.05     # riser звучит с нулевой секунды (владелец 22.10), а не после хука
RISER_PEAK_ON_CUT = 0.10   # пик riser — на склейке (Clumzzy: riser — ожидание перед раскрытием)
MIN_PICTURE_H = 1360       # владелец 22.10: «столько воздуха в рилсах не оставляют» — при 1100 низ был пуст
MAX_FROZEN_SHARE = 0.05    # доля почти неподвижных кадров готового файла (reel_metrics.py), v9 — 0.025
READ_CPS, READ_PAD = 17.0, 0.3   # дочитать группу: знаки / 17 + 0.3 с (StudioBinder 17 зн/с; разбор 189 роликов 23.10)
ACCENT_KINDS = ("punch", "shake", "spot", "circle")   # акцент — только на ключевом слове, не на предлоге
CLITICS = {"в", "во", "на", "с", "со", "к", "ко", "по", "о", "об", "от", "до", "из", "у", "за", "для", "при", "без",
           "и", "а", "но", "не", "ни", "же", "ли", "бы", "что", "как", "это", "то", "он", "она", "ты", "я", "мы"}


# Против шаблона (владелец 23.10: «чтобы агент не делал шаблонно»): у каждого рилса паспорт — тип хука, схема,
# приёмы; журнал прошлых рилсов — docs/reels_log.json. Типы хуков — из базы знаний (01_hook_script_retention.md).
STEP_MIN, STEP_SHIFT = 1.4, 0.33   # правило 30° (Бордуэлл): соседние окна одного рисунка — ×1.4 или сдвиг на треть окна
MIN_SHOT_SEC = 0.7         # план короче 0.7 с не читается (плейбук; v12 минимум 0.706)
MAX_SRC_CHANGES_30S = 10   # смен рисунка за любые 30 с (Lang 1999: перегрузка содержания), v12 — 9
CAP_HOLD_PAD = 0.6         # субтитр стоит не дольше чтения + 0.6 с (Szarkowska 2018, Stern 2024), v12 — максимум +0.47
CTA_BEFORE_END = 5.0       # призыв начинается не позже чем за 5 с до конца (финал — зона ухода: Dashlet, NSDI 2023)
LATE_ZONE, LATE_SHOT_SEC = 0.8, 2.0   # гипотеза: в последних 20 % планы ≤ 2 с (предупреждение, не запрет)
ONE_MOTION_SEC = 0.2       # гипотеза: старты движений (наезд, хлёст, пометка, жест куклы) не ближе 0.2 с
PUNCH_MIN_GAP = 3.0        # гипотеза: наезды ближе 3 с обесценивают друг друга (Дмитрык: лишние крупные ослабляют следующие)
LONG_WORD_SYLLABLES = 4    # в первых трёх фразах слова не длиннее 4 слогов (тест незнакомца; предупреждение)
# Безопасные зоны экрана 1080×1920 (Meta/Restream): верх 14 % — шапка Reels, низ 400 px — подпись и кнопки, бока 70 px,
# правая колонка кнопок x > 930 ниже 45 % высоты. Рукописные надписи и маркер — целиком внутри.
SAFE_TOP, SAFE_BOTTOM, SAFE_SIDE, SAFE_RIGHT_COL, RIGHT_COL_FROM = 269, 1520, 70, 930, 864
# Стоп-слова (план 04 п.1.3): преувеличение гасит любопытство, Instagram режет «сенсационный» контент о здоровье,
# медицинские обещания и ложный дефицит — бан рекомендаций и удар по доверию; шаблон «если ты X — у тебя СДВГ».
STOP_WORDS = (r"\bшок", r"врачи скрывают", r"\b100\s?%", r"гарантированн", r"\bбомб", r"\bвылеч", r"\bизлеч",
              r"навсегда", r"убить время", r"чуть не умер", r"только для ленивых", r"осталось \d+ мест", r"только сегодня",
              r"если ты .{1,40}[—–-] у тебя сдвг",
              # матрица 24.10 (B-группа): затёртые зачины и концовки, «вы» вместо одного «ты», продажа в лоб
              r"вы не поверите", r"^итак\b", r"\bвот и вс[её]\b", r"\bспасибо за просмотр", r"\bкупи(те)?\b",
              r"\b(вы|вас|вам|вами)\b")
HOOK_TYPES = ("диссонанс", "вопрос", "число", "POV", "середина истории", "что если", "термин", "ошибка/запрет",
              "желаемый результат", "сравнение", "секрет/закулисье", "абсурд", "прямое обращение к узнаванию")
MAX_DEVICE_OVERLAP = 0.5   # приёмы нового рилса совпадают с прошлым не больше чем наполовину


def check_passport(spec, log, reel_dir=""):
    """Паспорт рилса против журнала: тип хука и первые слова не как у предыдущего рилса, приёмы не те же."""
    err = []
    pp = spec.get("passport")
    if not pp:
        return ["нет паспорта рилса (passport: hook_type, structure, devices) — без него не проверить шаблонность"]
    goal = pp.get("goal") or {}
    if not (goal.get("question") and goal.get("emotion")):
        err.append('в паспорте нет цели: "goal": {"question": один вопрос зрителя, "emotion": целевая эмоция} (Kallaway)')
    if pp.get("hook_type") not in HOOK_TYPES:
        err.append(f"тип хука «{pp.get('hook_type')}» — не из списка {HOOK_TYPES}")
    if len(pp.get("devices", [])) < 5:
        err.append("в паспорте меньше 5 приёмов — опишите, чем этот рилс держит")
    parent = os.path.normpath(pp.get("variant_of", "")) if pp.get("variant_of") else None   # вариант для пробных Reels
    prev = [r for r in log if os.path.normpath(r.get("reel", "")) not in (os.path.normpath(reel_dir), parent)]
    if prev:
        last = prev[-1]
        if pp.get("hook_type") == last.get("hook_type"):
            err.append(f"тип хука «{pp['hook_type']}» как у прошлого рилса ({last['reel']}): смените тип хука")
        first = " ".join(clean(spec["beats"][0]["text"]).split()[:2]).lower()
        if any(first == r.get("first_words", "").lower() for r in prev):
            err.append(f"рилс начинается теми же словами «{first}», что прошлый: хук станет узнаваемым шаблоном")
        a, b = set(pp.get("devices", [])), set(last.get("devices", []))
        if a and len(a & b) / len(a) > MAX_DEVICE_OVERLAP:
            err.append(f"приёмы совпадают с прошлым рилсом на {len(a & b) / len(a):.0%} (> {MAX_DEVICE_OVERLAP:.0%}): "
                       f"общие — {sorted(a & b)}")
    return err


# Волна 9 (23.10, docs/reels_knowledge/09_hooks_funnels_audience.md §3, §6, §10, §21–§22): паспорт хука — для рилсов
# "passport.standard" >= 9; прежние рилсы (эталон v15 и раньше) судятся своими правилами.
HOOK_STANDARD = 9
HOOK_CANDIDATES_MIN = 20     # §3.7: 20–30 кандидатов по разным формулам → оценка → три пробных Reels
LEVERS = range(1, 17)        # 16 глубинных рычагов §10
HOOK_FOCUS_MAX = 3           # §3.1: ≤ 3 фокусные точки первого кадра
AUDIENCE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "reels_knowledge")
# §21.16–17: один призыв в конце — в теле рилса до cta_beat призывных слов нет; кодовое слово заменяет «шапку профиля» (§4)
CTA_WORDS = (r"\bнапиши", r"\bподпиш", r"\bссылк", r"\bшапк", r"\bперейди", r"\bпереходи", r"\bжми\b", r"\bсохрани")


def _norm(t):
    return re.sub(r"[^\w]+", " ", str(t).lower().replace("ё", "е")).strip()


_corpus = {}


def audience_corpus():
    """Все дословные комментарии зрителей, собранные волной 9 (карты raw9/audience и разделы §8–§9 документа 09)."""
    if "t" not in _corpus:
        parts = []
        for root, _, files in os.walk(os.path.join(AUDIENCE_DIR, "raw9", "audience")):
            parts += [open(os.path.join(root, f), encoding="utf8").read() for f in sorted(files) if f.endswith(".md")]
        for name in ("09_hooks_funnels_audience.md", "10_insider_map.md"):   # 10 — карта «только для своих»
            doc = os.path.join(AUDIENCE_DIR, name)
            if os.path.exists(doc):
                parts.append(open(doc, encoding="utf8").read())
        _corpus["t"] = "\n".join(parts)
        _corpus["n"] = _norm(_corpus["t"])
    return _corpus


def variant_text(v):
    return v.get("text", "") if isinstance(v, dict) else v


def check_hook(spec, log=(), reel_dir=""):
    """Паспорт хука волны 9: для кого, боль, цитата аудитории (сверяется с её комментариями), снятие вины или
    переворот убеждения, обещание и выплата, первый кадр — событие без ответа, рычаг §10, 20+ кандидатов, варианты
    с другим первым кадром, один призыв, кодовое слово вместо «шапки профиля»."""
    pp = spec.get("passport") or {}
    if (pp.get("standard") or 0) < HOOK_STANDARD:
        return []
    beats = spec.get("beats", [])
    hk = pp.get("hook")
    if not isinstance(hk, dict):
        return ['стандарт 9: нет "passport.hook" — who, pain, audience_quote, blame_off/belief, payoff, first_frame, lever, '
                'candidates (09 §6, §22)']
    err = []
    for f in ("who", "pain"):
        if len(str(hk.get(f, "")).strip()) < 5:
            err.append(f"паспорт хука: «{f}» пусто — для кого рилс и какая боль названа (09 §3.3)")
    if not (str(hk.get("blame_off", "")).strip() or str(hk.get("belief", "")).strip()):
        err.append("паспорт хука: нет ни blame_off (снятие вины), ни belief (переворачиваемое убеждение) — разрыв хука (09 §1.7)")
    q = hk.get("audience_quote") or {}
    if not (q.get("text") and q.get("video") and isinstance(q.get("likes"), int)):
        err.append('паспорт хука: audience_quote — {"text": дословно, "likes": N, "video": id} из комментариев (09 §3.2)')
    else:
        c = audience_corpus()
        if _norm(q["text"]) not in c["n"]:
            err.append(f"цитата аудитории «{q['text'][:50]}» не найдена в комментариях волны 9 (raw9/audience, 09 §8–§9): "
                       "хук берётся из их слов, не из головы")
        elif q["video"] not in c["t"]:
            err.append(f"id ролика цитаты «{q['video']}» не найден в картах аудитории")
    lv = hk.get("lever")
    levers = lv if isinstance(lv, list) else [lv]
    if not levers or any(x not in LEVERS for x in levers):
        err.append(f"паспорт хука: lever {lv!r} — номер рычага 1–16 из 09 §10 (первый — главный)")
    else:
        prev = [r for r in log if r.get("lever") is not None
                and os.path.normpath(r.get("reel", "")) != os.path.normpath(reel_dir)
                and os.path.normpath(r.get("reel", "")) != os.path.normpath(pp.get("variant_of", "") or "-")]
        if prev and prev[-1]["lever"] == levers[0]:
            err.append(f"главный рычаг {levers[0]} — как у прошлого рилса ({prev[-1]['reel']}): смените рычаг (09 §22)")
    pay = hk.get("payoff") or {}
    n = len(beats)
    if not (pay.get("promise") and isinstance(pay.get("tease"), int) and isinstance(pay.get("pay"), int)):
        err.append('паспорт хука: payoff — {"promise": что обещано, "tease": фраза 0–1, "pay": фраза выплаты} (09 §1.8, §21.3)')
    else:
        if not 0 <= pay["tease"] <= 1:
            err.append(f"обещание развязки (фраза {pay['tease']}) — не в первых двух фразах: хук в три ступени (09 §21.3)")
        if not (0 <= pay["pay"] < n and pay["pay"] >= n * 0.6):
            err.append(f"выплата обещания (фраза {pay['pay']}) — не в последних 40 % рилса: хук не выплачен (09 §1.8)")
    ff = hk.get("first_frame") or {}
    if not (ff.get("event") and ff.get("object")):
        err.append('паспорт хука: first_frame — {"event": что происходит в кадре 0, "object": предмет боли, '
                   '"focus_points": ≤3} (09 §3.1)')
    elif not isinstance(ff.get("focus_points"), int) or ff["focus_points"] > HOOK_FOCUS_MAX:
        err.append(f"первый кадр: фокусных точек {ff.get('focus_points')!r} — нужно ≤ {HOOK_FOCUS_MAX} (09 §1.3)")
    first = (beats[0].get("shots") or [{}])[0] if beats else {}
    if first.get("kind") == "doll" or ff.get("shows_solution"):
        err.append("первый кадр показывает решение (кот рядом): ответ в кадре 0 — смотреть дальше незачем (09 §21.1)")
    cands = hk.get("candidates") or []
    texts = [_norm(variant_text(x)) for x in cands]
    if len(set(texts)) < HOOK_CANDIDATES_MIN:
        err.append(f"кандидатов хука {len(set(texts))} < {HOOK_CANDIDATES_MIN}: процедура 20–30 кандидатов по разным "
                   "формулам → оценка (09 §3.7)")
    elif beats and _norm(clean(beats[0]["text"])) not in texts:
        err.append("хук рилса не из списка кандидатов: выбор не прошёл оценку (09 §3.7)")
    hv = pp.get("hook_variants") or []
    if not pp.get("variant_of") and sum(1 for v in hv if isinstance(v, dict) and v.get("first")) < 2:
        err.append('пробные варианты хука: минимум два с другим первым кадром {"text", "first": "fN:cx,cy,h"} — '
                   "замену одного текста Instagram считает дублем (09 §1.11, §21.6)")
    cta = pp.get("cta_beat")
    if isinstance(cta, int):
        for i, b in enumerate(beats[:cta]):
            low = clean(b["text"]).lower()
            m = next((re.search(p, low) for p in CTA_WORDS if re.search(p, low)), None)
            if m:
                err.append(f"фраза {i}: призыв «{m.group(0)}» до фразы призыва {cta}: один призыв — в конце (09 §21.16–17)")
    kw = pp.get("keyword")
    if kw is not None:
        word = str((kw or {}).get("word", "")).strip()
        if not (word and (kw or {}).get("delivers")):
            err.append('кодовое слово: {"word": …, "delivers": что придёт в личку} — слово прямо называет выдачу (09 §4)')
        elif isinstance(cta, int) and 0 <= cta < n and word.lower() not in clean(beats[cta]["text"]).lower():
            err.append(f"кодового слова «{word}» нет в фразе призыва {cta}")
        if any(re.search(r"\bшапк", clean(b["text"]).lower()) for b in beats):
            err.append("кодовое слово и «шапка профиля» сразу: два пути — человек выбирает не выбирать (09 §21.16)")
        for name in ("caption", "pinned_comment"):
            if re.search(r"\bшапк", str(pp.get(name, "")).lower()):
                err.append(f"{name}: «шапка профиля» при кодовом слове — один путь к сайту, через слово (09 §4)")
            if word and name == "caption" and word.lower() not in str(pp.get(name, "")).lower():
                err.append(f"в подписи нет кодового слова «{word}»: кто не досмотрел до призыва, найдёт его там (09 §4)")
    return err


# Матрица применения (24.10, владелец: «обязан применять всё до единого»): каждый приём документа волны 9 — запись в
# docs/reels_knowledge/apply_matrix.jsonl; scope "reel" решается в каждом рилсе стандарта ≥ 10 — номером фразы, местом
# вне ролика (подпись, закреп, обложка, личка, бот) или отказом с причиной; одинаковая отговорка — не больше трёх раз.
MATRIX_PATH = os.path.join(AUDIENCE_DIR, "apply_matrix.jsonl")
MATRIX_STANDARD = 10
HOOK_LAYERS = ("verbal", "text", "visual", "audio", "caption")   # пять слоёв хука (правило владельца 24.10)
HOOK_C3 = ("context", "clarity", "curiosity")                       # 3C: «это про меня», «понятно о чём», «что дальше?»
HOOK_LAYERS_STANDARD = 12


def check_hook_layers(spec):
    """Хук — система из пяти слоёв, работающих одновременно (голос, текст на экране, кадр, звук, первая строка подписи),
    и проходит 3C: контекст («это про меня»), ясность («понятно, о чём»), любопытство («что дальше?»). Правило владельца
    24.10 (CLAUDE.md, рилсы п.0). Каждый слой и каждое C описаны в паспорте; что можно проверить по reel.json — проверено."""
    pp = spec.get("passport") or {}
    if (pp.get("standard") or 0) < HOOK_LAYERS_STANDARD:
        return []
    hk = pp.get("hook") or {}
    lay, c3, err = hk.get("layers") or {}, hk.get("c3") or {}, []
    for k in HOOK_LAYERS:
        if len(str(lay.get(k, "")).strip()) < 5:
            err.append(f"хук: слой «{k}» не описан в passport.hook.layers — хук это пять слоёв сразу: verbal (первая фраза), "
                       "text (текст на экране), visual (действие/предмет/эмоция в кадре 0), audio (голос, пауза, резкий звук), "
                       "caption (первая строка подписи продолжает интригу)")
    for k in HOOK_C3:
        if len(str(c3.get(k, "")).strip()) < 5:
            err.append(f"хук: 3C «{k}» не описан в passport.hook.c3 — context «это про меня», clarity «понятно, о чём», "
                       "curiosity «дико интересно, что дальше»")
    beats = spec.get("beats") or []
    b0 = beats[0] if beats else {}
    if b0 and not (any(e.get("kind") == "sfx" for e in b0.get("fx", [])) or b0.get("gaps")):
        err.append("хук: нет аудиослоя — ни звука, ни паузы во фразе 0")
    if b0 and not b0.get("shots"):
        err.append("хук: нет визуального слоя — у фразы 0 нет кадра")
    cap, first = str(pp.get("caption", "")), str(lay.get("caption", "")).strip()
    if first and not _norm(cap).startswith(_norm(first)):
        err.append("хук: слой caption — не первая строка подписи: в ленте видно только начало подписи")
    return err


# Хук ворует внимание (владелец 25.10: «хук должен буквально воровать внимание: сильный визуал, вербал и невербал,
# движение или необычный ракурс, и при этом не один какой-то эффект»). Стандарт ≥ 13; новый рилс ниже 13 не рендерится.
HOOK_STEAL_STANDARD = 13
HOOK_STEAL = ("visual", "verbal", "nonverbal", "motion")
HOOK_STEAL_EFFECTS_MIN = 2   # визуальных эффектов в первой фразе одновременно: не один
HOOK_PUSH_MIN = 0.15         # наезд хука: окно меняется хотя бы на 15 % за фразу, иначе это дрейф, а не движение


def hook_effects(b0):
    """Визуальные эффекты первой фразы, которые видно по reel.json: вход хлёстом или наездом, сильный наезд камеры,
    тряска, удар, прожектор, круг, жест куклы."""
    out = set()
    for s in (b0.get("shots") or [])[:1]:
        if s.get("whip"): out.add("whip")
        if s.get("zoom_in"): out.add("zoom_in")
        f, t = s.get("from"), s.get("to")
        if f and t and f[2] and abs(t[2] - f[2]) / f[2] >= HOOK_PUSH_MIN: out.add("push")
        if s.get("kind") == "doll" and s.get("actions"): out.add("doll")
    for e in b0.get("fx") or []:
        if e.get("kind") in ("shake", "punch", "spot", "circle"): out.add(e["kind"])
    return out


def check_hook_steal(spec, log=(), reel_dir=""):
    """Хук ворует внимание сразу всем: визуал (что в кадре), вербал (что сказано), невербал (мимика, поза, тон голоса),
    движение или необычный ракурс; в первой фразе не меньше двух визуальных эффектов одновременно."""
    pp = spec.get("passport") or {}
    std = pp.get("standard") or 0
    beats = spec.get("beats") or []
    if std < HOOK_STEAL_STANDARD:
        first = " ".join(clean(beats[0]["text"]).split()[:2]).lower() if beats else ""
        old = any(os.path.normpath(r.get("reel", "")) == os.path.normpath(reel_dir or "")
                  and r.get("first_words", "").lower() == first for r in log)
        if reel_dir and not old:
            return [f"новый рилс со стандартом {std}: нужен \"standard\": {HOOK_STEAL_STANDARD} — хук ворует внимание "
                    "(passport.hook.steal и два эффекта в первой фразе, CLAUDE.md, рилсы п.0а)"]
        return []
    st, err = (pp.get("hook") or {}).get("steal") or {}, []
    for k in HOOK_STEAL:
        if len(str(st.get(k, "")).strip()) < 10:
            err.append(f"хук: «{k}» не описан в passport.hook.steal — хук ворует внимание: visual (что в кадре 0), verbal "
                       "(что сказано), nonverbal (мимика, поза, тон голоса), motion (движение или необычный ракурс)")
    effs = hook_effects(beats[0]) if beats else set()
    if len(effs) < HOOK_STEAL_EFFECTS_MIN:
        err.append(f"хук: визуальных эффектов в первой фразе {len(effs)} ({', '.join(sorted(effs)) or 'нет'}), нужно "
                   f"≥ {HOOK_STEAL_EFFECTS_MIN} одновременно: вход хлёстом или наездом, сильный наезд (≥ 15 %), тряска, "
                   "удар, прожектор, круг — не один эффект")
    return err


CTA_COMMENT_RE = r"\bнапиши\b.*\bкоммент"


def check_call_to_comment(spec):
    """Призыв есть всегда (владелец 24.10): фраза passport.cta_beat просит написать в комментариях о себе («Напиши в
    комментах, что у тебя вызывает ступор»). На любой комментарий — автоличка, дальше бот и сайт (20_funnel/02 §1.1)."""
    pp = spec.get("passport") or {}
    if (pp.get("standard") or 0) < HOOK_LAYERS_STANDARD:
        return []
    beats, k = spec.get("beats") or [], pp.get("cta_beat")
    if not isinstance(k, int) or not 0 <= k < len(beats):
        return ["призыва нет: passport.cta_beat — номер фразы «Напиши в комментах, …» (призыв обязателен в каждом рилсе)"]
    if not re.search(CTA_COMMENT_RE, clean(beats[k]["text"]).lower()):
        return [f"фраза призыва {k} не зовёт в комментарии: нужен вопрос о себе «Напиши в комментах, …» "
                "(на любой комментарий — автоличка → бот/сайт)"]
    return []


def check_brand_and_face(spec, brand=None):
    """Имя и тёплая эмоция не теряются при переписывании (владелец 24.10: в v5 пропали рукописное «Напарник» и весёлое
    лицо куклы — без решения, просто не перенесены). Имя бренда — в тексте или рукописной надписью; если в рилсе есть
    кукла, хотя бы на одном её плане — лицо с эмоцией (`face`), а не только наклон и взгляд."""
    pp = spec.get("passport") or {}
    if (pp.get("standard") or 0) < HOOK_LAYERS_STANDARD:
        return []
    if brand is None:
        brand = json.load(open(BRAND_PATH, encoding="utf8")).get("brand") if os.path.exists(BRAND_PATH) else None
    beats, errs = spec.get("beats") or [], []
    said = [clean(b["text"]) for b in beats] + [f.get("text", "") for b in beats for f in b.get("fx", [])
                                                 if f.get("kind") in ("write", "mark")]
    if brand and not any(brand.lower()[:-1] in x.lower() for x in said):
        errs.append(f"имени «{brand}» нет ни в тексте, ни рукописной надписью: зритель не узнает, кто это")
    dolls = [s for b in beats for s in b.get("shots", []) if s.get("kind") == "doll"]
    if dolls and not any(a.get("do") == "face" for s in dolls for a in s.get("actions", [])):
        errs.append("кукла без эмоции: ни на одном её плане нет лица (`face`, например happy со звёздочками)")
    return errs


HAND_READ_MIN = 0.5     # дописанное слово стоит целиком хотя бы полсекунды до склейки, иначе его не прочесть


def check_written_read(events, shots, read_min=HAND_READ_MIN):
    """Рукописное слово не срезается склейкой (v11: «бесплатно» начинало писаться за 0,3 с до склейки и пропадало
    недописанным). Надпись держится, пока идут планы того же рода, поэтому видна до конца этой серии планов."""
    errs = []
    for e in events:
        if e.get("kind") not in ("write", "mark"):
            continue
        i = max((k for k, x in enumerate(shots) if x["t0"] <= e["t"] + 1e-6), default=0)
        kind, j = shots[i].get("kind", "crop"), i
        while j + 1 < len(shots) and shots[j + 1].get("kind", "crop") == kind:
            j += 1
        shown = min(shots[j]["t1"], e["t"] + e.get("dur", 0.6) + e.get("hold", 9e9)) - (e["t"] + e.get("dur", 0.6))
        if shown < read_min:
            errs.append(f"рукописное «{e.get('text')}» на {e['t']:.2f} с стоит дописанным {max(shown, 0):.2f} с "
                        f"< {read_min} до склейки {shots[j]['t1']:.2f} с: начать раньше (на само слово) или сдвинуть склейку")
    return errs


MATRIX_WHERE = ("caption", "pinned", "cover", "hook_variants", "dm", "bot", "site", "channel", "comments", "series")
SKIP_REPEAT_MAX = 3


def load_matrix(path=MATRIX_PATH):
    if not os.path.exists(path):
        return []
    return [json.loads(x) for x in open(path, encoding="utf8") if x.strip()]


def check_matrix(spec, matrix=None):
    """Каждый приём матрицы с областью «reel» — решён в passport.matrix этого рилса (стандарт ≥ 10)."""
    pp = spec.get("passport") or {}
    if (pp.get("standard") or 0) < MATRIX_STANDARD:
        return []
    matrix = load_matrix() if matrix is None else matrix
    dec = pp.get("matrix") or {}
    n = len(spec.get("beats", [])); ncand = len((pp.get("hook") or {}).get("candidates") or [])
    err, reasons = [], {}
    for it in matrix:
        if it.get("scope") != "reel":
            continue
        v, where = dec.get(it["id"]), f"приём {it['id']} «{it['title']}»"
        if v is None:
            err.append(f"{where}: нет решения в passport.matrix — {it.get('ask') or 'где применён?'}"); continue
        if isinstance(v, dict) and "skip" in v:
            r = str(v["skip"]).strip()
            if len(r) < SKIP_MIN_CHARS:
                err.append(f"{where}: отказ без причины")
            reasons.setdefault(r.lower(), []).append(it["id"]); continue
        if isinstance(v, dict) and "candidate" in v:
            if not (isinstance(v["candidate"], int) and 0 <= v["candidate"] < ncand):
                err.append(f"{where}: кандидат хука {v['candidate']!r} — не номер в passport.hook.candidates (0…{ncand - 1})")
            continue
        if isinstance(v, dict) and "where" in v:
            if v["where"] not in MATRIX_WHERE or len(str(v.get("how", "")).strip()) < SKIP_MIN_CHARS:
                err.append(f"{where}: вне ролика — {{\"where\": одно из {MATRIX_WHERE}, \"how\": что именно сделано}}")
            continue
        bs = _beats_of(v)
        if not bs or any(not 0 <= b < n for b in bs):
            err.append(f"{where}: {v!r} — не номер фразы 0…{n - 1}, не кандидат хука, не место и не отказ")
    for r, ids in reasons.items():
        if len(ids) > SKIP_REPEAT_MAX:
            err.append(f"одна и та же отговорка «{r[:60]}» у {len(ids)} приёмов ({', '.join(ids[:6])}…): причина — своя "
                       f"у каждого, не больше {SKIP_REPEAT_MAX} раз")
    return err


def matrix_coverage(spec, matrix=None):
    """Сколько приёмов «reel» применено во фразах, вне ролика, кандидатом хука и сколько отказов — для отчёта."""
    matrix = load_matrix() if matrix is None else matrix
    dec = (spec.get("passport") or {}).get("matrix") or {}
    out = {"beat": 0, "where": 0, "candidate": 0, "skip": 0, "none": 0}
    for it in matrix:
        if it.get("scope") != "reel":
            continue
        v = dec.get(it["id"])
        k = ("none" if v is None else "skip" if isinstance(v, dict) and "skip" in v else
             "candidate" if isinstance(v, dict) and "candidate" in v else "where" if isinstance(v, dict) and "where" in v
             else "beat")
        out[k] += 1
    return out


# Человеческий текст (24.10, владелец: «никакой нейросетевой фигни: длинные тире в каждом предложении, сильная
# парцелляция»). Правила и источники — docs/reels_knowledge/14_human_text.md: жёсткие запреты humanizer-ru (MIT,
# ilyautov), Wikipedia «Signs of AI writing», 26 карточек живой речи raw13. Ошибка, а не предупреждение: стандарт ≥ 11.
HUMAN_STANDARD = 11
PARCEL_WORDS = 2          # «предложение» из 1–2 слов с точкой — осколок («Неделю. Одна строчка.»)
PARCEL_MAX = 2            # осколков на весь текст рилса — не больше двух и никогда два подряд
NEG_PAIR_MAX = 1          # «Не X. А Y» / «Не X. Не Y» — один раз (12 §5: только против подозрения зрителя о себе)
ANAPHORA_RUN = 3          # три предложения подряд с одного слова — машинная тройка
DASH_RE = re.compile(r"(?<!\d)\s*[—–]\s*(?!\d)|\s-\s")   # тире вне диапазона «3–5» и дефис с пробелами
AI_PHRASES = (r"не просто\b[^.?!]{0,50},\s*а\b", r"\bне только\b[^.?!]*\bно и\b", r"\bстоит отметить",
              r"\bважно (понимать|помнить|отметить|знать)", r"\bданн(ый|ая|ое|ые|ого|ой|ую)\b", r"\bявляется\b",
              r"\bтаким образом\b", r"\bподводя итог", r"\bпогрузимся", r"\bдавай(те)? разбер[её]мся",
              r"раскрыть (свой )?потенциал", r"на новый уровень", r"\bв современном мире", r"\bв мире, где",
              r"\bиграет (важную|ключевую) роль", r"\bключ к\b", r"\bмагия\b", r"\bпутешестви",
              r"\bсамое интересное\b", r"\bи вот (главное|секрет)\b", r"\b(секрет|суть|правда|фишка) (прост[аы]?|в том)\s*:",
              r"\b(главное|секрет|суть|ответ)\s*:", r"\bты имеешь право\b", r"\bв рамках\b", r"\bв целях\b")
SELF_ANSWER_RE = re.compile(r"\?\s*(Потому что|Ответ|Всё просто|Просто потому|Дело в том)", re.I)


def _sentences(text):
    """Предложения текста по . ! ? …; кавычки и разметка рилса сняты."""
    t = clean(text).replace("«", "").replace("»", "").replace('"', "")
    return [x.strip() for x in re.split(r"(?<=[.!?…])\s+", t) if x.strip()]


def _words(s):
    return re.findall(r"[\w-]+", s)


def human_issues(texts):
    """Признаки машинного текста в списке строк (фразы рилса подряд). Список (где, что) — пусто, если текст живой."""
    out, sents = [], []
    for i, t in enumerate(texts):
        tc = clean(t)
        if DASH_RE.search(tc):
            out.append((i, f"тире в «{tc[:50]}»: перестроить фразу, запятая или двоеточие (14 §1.1)"))
        low = tc.lower()
        for rx in AI_PHRASES:
            m = re.search(rx, low)
            if m:
                out.append((i, f"«{m.group(0)}» — оборот нейросети (14 §1.3), сказать прямо"))
        if SELF_ANSWER_RE.search(tc):
            out.append((i, f"«{tc[:50]}»: вопрос и сам себе ответ «Зачем? Потому что» (14 §1.4)"))
        sents += [(i, s) for s in _sentences(t)]
    short = [k for k, (_, s) in enumerate(sents) if len(_words(s)) <= PARCEL_WORDS and not s.endswith("?")]
    for a, b in zip(short, short[1:]):
        if b == a + 1:
            out.append((sents[b][0], f"«{sents[a][1]} {sents[b][1]}» — два осколка подряд: рваная парцелляция (14 §1.2), "
                                    "склеить в одну фразу через «и», «поэтому», запятую"))
    if len(short) > PARCEL_MAX:
        out.append((sents[short[PARCEL_MAX]][0], f"осколков из 1–{PARCEL_WORDS} слов с точкой {len(short)} > {PARCEL_MAX}: "
                    f"{', '.join('«' + sents[k][1] + '»' for k in short)} (14 §1.2)"))
    neg = 0
    for (_, s1), (i2, s2) in zip(sents, sents[1:]):
        if re.match(r"(не|это не)\b", s1, re.I) and re.match(r"(а|не|это)\b", s2, re.I):
            neg += 1
            if neg > NEG_PAIR_MAX:
                out.append((i2, f"«{s1} {s2}» — ещё одно «Не X. А Y» (уже {neg} раз, можно {NEG_PAIR_MAX}): сказать Y прямо (14 §1.3)"))
    run = 1
    for k in range(1, len(sents)):
        w0, w1 = (_words(sents[k - 1][1]) or [""])[0].lower(), (_words(sents[k][1]) or [""])[0].lower()
        run = run + 1 if w0 and w0 == w1 else 1
        if run == ANAPHORA_RUN:
            out.append((sents[k][0], f"три предложения подряд с «{w1}»: машинная тройка (14 §1.5)"))
    return out


def reel_texts(spec):
    """Всё, что читает зритель: фразы рилса подряд, затем подпись, закреп, обложка, варианты хука."""
    beats = [b.get("text", "") for b in spec.get("beats", [])]
    pp = spec.get("passport") or {}
    extra = []
    for k in ("cover", "caption", "pinned_comment", "hook_variants"):
        v = pp.get(k)
        for x in (v if isinstance(v, list) else [v]):
            if isinstance(x, dict):
                x = x.get("text") or x.get("hook") or ""
            if isinstance(x, str) and x.strip():
                extra.append((k, x))
    return beats, extra


def check_human(spec):
    """Текст рилса — человеческой речью (стандарт ≥ 11): ни тире, ни рваной парцелляции, ни оборотов нейросети."""
    if ((spec.get("passport") or {}).get("standard") or 0) < HUMAN_STANDARD:
        return []
    beats, extra = reel_texts(spec)
    err = [f"фраза {i}: {m}" for i, m in human_issues(beats)]
    for k, x in extra:
        err += [f"{k}: {m}" for _, m in human_issues([x]) if "осколк" not in m]   # подпись и обложка — не речь кота
    return err


# Полное использование стратегии (24.10, владелец: «чтобы ты не мог не использовать все, чтобы не мог что-то
# пропустить»; CLAUDE.md, рилсы, п.11). Список берётся из самих документов при каждой проверке — правка документа
# сразу становится требованием: 40 связок 12 §6, 9 шагов формулы 12 §5, 16 рычагов 09 §10, страхи 09 §8.2,
# убеждения 09 §8.3, желания 09 §9.1. Каждый пункт решён в passport.coverage: номер фразы, место вокруг рилса или отказ.
COVERAGE_STANDARD = 11
STRATEGY_PATH = os.path.join(AUDIENCE_DIR, "12_strategy.md")
AUDIENCE_DOC = os.path.join(AUDIENCE_DIR, "09_hooks_funnels_audience.md")
COVERAGE_GROUPS = {"L": "связка 12 §6", "S": "шаг формулы 12 §5", "R": "рычаг 09 §10", "F": "страх 09 §8.2",
                   "B": "убеждение 09 §8.3", "D": "желание 09 §9.1"}
COVERAGE_NO_SKIP = ("S",)          # скелет рилса не пропускается
COVERAGE_NEED_HOW = ("F", "B", "D")  # страх → чем снят, убеждение → как развёрнуто, желание → как дано завуалированно
COVERAGE_LINKS_IN_REEL = (4, 10)   # связок §6 во фразах: 12 §6 — «в одном рилсе 4–6» главных, две-три могут делить одну
                                   # фразу (честный предел + «плохо, НО хорошо»); владелец 24.10 (вечер): «не надо городить
                                   # всё подряд, самое эффективное» — v7/v8 с 33 связками вышли на 73 с воды
TEXT_MAX_HARD = 600                 # потолок даже со словом владельца (~45 с)
TEXT_MAX_CHARS = 520               # текст рилса на ~40 с: при 14–15 знаках в секунду плюс паузы (владелец: «40 секунд и всё»)


def _section(text, start, stop):
    a = text.find(start)
    if a < 0:
        return ""
    b = text.find(stop, a + len(start))
    return text[a:b if b > 0 else None]


def strategy_items(strategy=STRATEGY_PATH, audience=AUDIENCE_DOC):
    """{id: название} всех пунктов стратегии и аудитории, вынутых из документов."""
    st = open(strategy, encoding="utf8").read() if os.path.exists(strategy) else ""
    au = open(audience, encoding="utf8").read() if os.path.exists(audience) else ""
    out = {}
    for m in re.finditer(r"^(\d+)\. \*\*(.+?)\*\*", _section(st, "\n## 6.", "\n## 7."), re.M):
        out[f"L{m.group(1)}"] = m.group(2).strip(" .")
    for k, m in enumerate(re.finditer(r"^\|[^|\n]+\|\s*\*\*(.+?)\*\*", _section(st, "\n## 5.", "\n## 6."), re.M), 1):
        out[f"S{k}"] = m.group(1)
    for m in re.finditer(r"^### (\d+)\. (.+)$", _section(au, "\n## 10.", "\n## 11."), re.M):
        out[f"R{m.group(1)}"] = m.group(2)
    for g, rx in (("F", r"^#### С(\d+)\. (.+)$"), ("B", r"^#### У(\d+)\. (.+)$")):
        for m in re.finditer(rx, au, re.M):
            out[f"{g}{m.group(1)}"] = m.group(2)
    for m in re.finditer(r"^#### (\d+)\. (.+)$", _section(au, "\n### 9.1.", "\n### 9.2."), re.M):
        out[f"D{m.group(1)}"] = m.group(2)
    return out


def check_coverage(spec, log=(), reel_dir="", items=None):
    """Каждый пункт стратегии решён в passport.coverage (ничего не забыто), но во фразах — только 4–8 сильнейших связок
    и текст на ~40 с (ничего лишнего); новый рилс — не ниже стандарта 11."""
    pp = spec.get("passport") or {}
    std = pp.get("standard") or 0
    if std < COVERAGE_STANDARD:
        first = " ".join(clean(spec["beats"][0]["text"]).split()[:2]).lower() if spec.get("beats") else ""
        old = any(os.path.normpath(r.get("reel", "")) == os.path.normpath(reel_dir or "")
                  and r.get("first_words", "").lower() == first for r in log)
        if reel_dir and not old:
            return [f"новый рилс со стандартом {std}: нужен \"standard\": {COVERAGE_STANDARD} — человеческий текст (14) и "
                    "решение по каждому пункту стратегии в passport.coverage (CLAUDE.md, рилсы, п.11–12)"]
        return []
    items = strategy_items() if items is None else items
    cov = pp.get("coverage") or {}
    n = len(spec.get("beats", []))
    err, reasons = [], {}
    for iid, title in items.items():
        g = iid[0]
        v, where = cov.get(iid), f"{COVERAGE_GROUPS[g]} {iid} «{title[:60]}»"
        if v is None:
            err.append(f"{where}: нет решения в passport.coverage (номер фразы, {{\"where\", \"how\"}} или {{\"skip\"}})")
            continue
        if isinstance(v, dict) and "skip" in v:
            r = str(v["skip"]).strip()
            if g in COVERAGE_NO_SKIP:
                err.append(f"{where}: шаг формулы не пропускается — он есть в каждом рилсе")
            elif len(r) < SKIP_MIN_CHARS:
                err.append(f"{where}: отказ без причины")
            reasons.setdefault(r.lower(), []).append(iid)
            continue
        how = str(v.get("how", "")).strip() if isinstance(v, dict) else ""
        if isinstance(v, dict) and "where" in v:
            if v["where"] not in MATRIX_WHERE or len(how) < SKIP_MIN_CHARS:
                err.append(f"{where}: вне ролика — {{\"where\": одно из {MATRIX_WHERE}, \"how\": что именно сделано}}")
            continue
        bs = _beats_of(v.get("beats") if isinstance(v, dict) else v)
        if not bs or any(not 0 <= b < n for b in bs):
            err.append(f"{where}: {v!r} — не номер фразы 0…{n - 1}, не место и не отказ")
        elif g in COVERAGE_NEED_HOW and len(how) < SKIP_MIN_CHARS:
            err.append(f"{where}: {{\"beats\": [...], \"how\": ...}} — чем снят страх, как развёрнуто убеждение, как дано желание")
    in_reel = [i for i in items if i[0] == "L" and _beats_of(cov.get(i).get("beats") if isinstance(cov.get(i), dict)
                                                           else cov.get(i))]
    lo, hi = COVERAGE_LINKS_IN_REEL
    if items and any(i[0] == "L" for i in items) and not lo <= len(in_reel) <= hi:
        err.append(f"связок во фразах {len(in_reel)}: нужно {lo}–{hi} самых сильных (12 §6), остальные — вокруг рилса или отказ")
    chars = sum(len(clean(b.get("text", ""))) for b in spec.get("beats", []))
    tm = pp.get("text_max") or {}                      # владелец разрешил длиннее (24.10: «43 секунды не страшно»)
    limit = min(int(tm.get("chars", TEXT_MAX_CHARS)), TEXT_MAX_HARD) if len(str(tm.get("owner", ""))) >= 10 else TEXT_MAX_CHARS
    if chars > limit:
        err.append(f"текст рилса {chars} знаков > {limit} (~40 с): вода, сократить до самого сильного"
                   + ("" if limit > TEXT_MAX_CHARS else " (длиннее — только словом владельца: passport.text_max {chars, owner})"))
    for r, ids in reasons.items():
        if len(ids) > SKIP_REPEAT_MAX:
            err.append(f"одна отговорка «{r[:60]}» у {len(ids)} пунктов ({', '.join(ids[:6])}…): причина — своя у каждого")
    return err


# Инвентарь всей базы (24.10, владелец: «я обязан все эти расшифровки применять… чтобы каждый рилс без этого не
# делался»). docs/reels_knowledge/inventory_matrix.jsonl собирает scripts/inventory_matrix.py из 20_funnel/01_inventory.md
# (3 205 приёмов из 400+ расшифровок и документов). Каждый пункт scope "reel" решён в passport.inventory рилса
# стандарта ≥ 12: номер фразы, {"where", "how"} вне ролика, {"by_code": что делает код}, {"same_as": номер уже решённого
# пункта матрицы или инвентаря} или {"skip": своя причина}. Новый рилс ниже стандарта 12 не рендерится.
INVENTORY_PATH = os.path.join(AUDIENCE_DIR, "inventory_matrix.jsonl")
INVENTORY_STANDARD = 12
BY_CODE_RE = re.compile(r"reel(_rules|_geom|_publish|_draft)?\.py|reel_rules\.|reel\.|reel_geom\.|library\.json|"
                        r"reel_metrics|check_\w+", re.I)


def load_inventory(path=INVENTORY_PATH):
    if not os.path.exists(path):
        return []
    return [json.loads(x) for x in open(path, encoding="utf8") if x.strip()]


def check_inventory(spec, log=(), reel_dir="", inventory=None, matrix=None):
    """Каждый приём инвентаря с областью «reel» решён в passport.inventory (стандарт ≥ 12); новый рилс — не ниже 12."""
    pp = spec.get("passport") or {}
    std = pp.get("standard") or 0
    if std < INVENTORY_STANDARD:
        first = " ".join(clean(spec["beats"][0]["text"]).split()[:2]).lower() if spec.get("beats") else ""
        old = any(os.path.normpath(r.get("reel", "")) == os.path.normpath(reel_dir or "")
                  and r.get("first_words", "").lower() == first for r in log)
        if reel_dir and not old:
            return [f"новый рилс со стандартом {std}: нужен \"standard\": {INVENTORY_STANDARD} — решение по каждому приёму "
                    "инвентаря всей базы в passport.inventory (CLAUDE.md, рилсы, п.16)"]
        return []
    inventory = load_inventory() if inventory is None else inventory
    matrix_ids = {m["id"] for m in (load_matrix() if matrix is None else matrix)}
    inv_ids = {i["id"] for i in inventory}
    dec = pp.get("inventory") or {}
    n = len(spec.get("beats", []))
    err, reasons = [], {}
    for it in inventory:
        if it.get("scope") != "reel":
            continue
        v, where = dec.get(it["id"]), f"инвентарь {it['id']} (строка {it['line']}) «{it['title'][:70]}»"
        if v is None:
            err.append(f"{where}: нет решения в passport.inventory"); continue
        if isinstance(v, dict) and "skip" in v:
            r = str(v["skip"]).strip()
            if len(r) < SKIP_MIN_CHARS:
                err.append(f"{where}: отказ без причины")
            reasons.setdefault(r.lower(), []).append(it["id"]); continue
        if isinstance(v, dict) and "by_code" in v:
            if not BY_CODE_RE.search(str(v["by_code"])):
                err.append(f"{where}: by_code должен называть, какой код это делает (reel.py, reel_rules.check_…)")
            continue
        if isinstance(v, dict) and "same_as" in v:
            if v["same_as"] not in matrix_ids | inv_ids:
                err.append(f"{where}: same_as {v['same_as']!r} — не номер матрицы и не номер инвентаря")
            elif v["same_as"] in inv_ids and not isinstance(dec.get(v["same_as"]), (int, list)) \
                    and "beats" not in (dec.get(v["same_as"]) or {}):
                pass                                    # ссылка на решённый не фразой пункт допустима
            continue
        if isinstance(v, dict) and "where" in v:
            if v["where"] not in MATRIX_WHERE or len(str(v.get("how", "")).strip()) < SKIP_MIN_CHARS:
                err.append(f"{where}: вне ролика — {{\"where\": одно из {MATRIX_WHERE}, \"how\": что именно сделано}}")
            continue
        bs = _beats_of(v.get("beats") if isinstance(v, dict) else v)
        if not bs or any(not 0 <= b < n for b in bs):
            err.append(f"{where}: {v!r} — не номер фразы 0…{n - 1}, не место, не код, не ссылка и не отказ")
        else:
            e = _inventory_proof(v, bs, spec.get("beats", []))
            if e: err.append(f"{where}: {e}")
    for r, ids in reasons.items():
        if len(ids) > SKIP_REPEAT_MAX:
            err.append(f"одна отговорка «{r[:60]}» у {len(ids)} пунктов инвентаря ({', '.join(ids[:5])}…): причина — своя")
    return err


def clean(text):
    return re.sub(r"\s+", " ", text.replace("*", "").replace("|", "")).strip()


def check_spec(spec, sfx_names):
    """Правила самого reel.json: звуки владельца, хук, раскладка, петля. Список ошибок (пустой — годно)."""
    err = []
    beats = spec.get("beats", [])
    if len(beats) < 2:
        return ["меньше двух фраз — хук и раскрытие не из чего собрать"]
    if "music" in spec or any(e.get("name") == "music" for b in beats for e in b.get("fx", [])):
        err.append("музыка: в рилсах её нет (решение владельца 22.10)")
    for i, b in enumerate(beats):
        for e in b.get("fx", []):
            if e.get("kind") == "sfx" and e.get("name") not in sfx_names:
                err.append(f"фраза {i}: звук «{e.get('name')}» — не из звуков владельца {sorted(sfx_names)}")
        for s in b.get("shots", []):
            if s.get("sound") and s["sound"] not in sfx_names:
                err.append(f"фраза {i}: звук плана «{s['sound']}» — не из звуков владельца")
    hook = clean(beats[0]["text"])
    if len(hook) > HOOK_MAX_CHARS:
        err.append(f"хук «{hook}» — {len(hook)} знаков, нужно ≤ {HOOK_MAX_CHARS}: первая фраза бьёт в лоб, коротко")
    riser = [e for e in beats[0].get("fx", []) if e.get("kind") == "sfx" and e.get("name") == "riser"]
    if not riser:
        err.append("в первой фразе нет riser: он звучит с нулевой секунды в каждом рилсе (владелец 22.10)")
    else:
        e = riser[0]
        start = spec.get("lead_in", 0.0) + e.get("dt", 0.0) if e.get("at", 0) == 0 and not e.get("after") else None
        if e.get("align") != "start" or start is None or start > RISER_START_MAX:
            err.append('riser должен начинаться с 0 с: {"at": 0, "align": "start", "dt": -lead_in}')
    if beats[1].get("after_sfx") != "riser":
        err.append('вторая фраза должна вставать на пик riser: "after_sfx": "riser"')
    if spec.get("picture_h", 1380) < MIN_PICTURE_H:
        err.append(f"picture_h {spec.get('picture_h')} < {MIN_PICTURE_H}: низ экрана будет пустой бумагой")
    for i, b in enumerate(beats):                     # эп.02 v11: наезд стоял на «при», а не на «СДВГ» (замер 23.10)
        words = [w for w in clean(b["text"]).split() if w not in ("—", "–", "-")]
        for e in b.get("fx", []):
            k = e.get("at", 0)
            if e.get("kind") in ACCENT_KINDS and k < len(words):
                w = re.sub(r"[^\w-]", "", words[k].lower())
                if w in CLITICS:
                    err.append(f"фраза {i}: {e['kind']} на служебном слове «{words[k]}» — акцент ставится на ключевое")
        marked = [w.startswith("*") or w.startswith("«*") or "*" in w for w in b["text"].replace("|", "").split()
                  if w not in ("—", "–", "-")]
        for e in b.get("fx", []):
            k = e.get("at", 0)
            if e.get("kind") in ACCENT_KINDS and k < len(words) and k < len(marked) and not marked[k]:
                if (k > 0 and marked[k - 1]) or (k + 1 < len(marked) and marked[k + 1]):
                    err.append(f"фраза {i}: {e['kind']} на «{words[k]}», а ключевое (*) — соседнее слово: сдвиг на одно")
        low = clean(b["text"]).lower()
        for pat in STOP_WORDS:
            if re.search(pat, low):
                err.append(f"фраза {i}: стоп-слово «{re.search(pat, low).group(0)}» — сенсация, медицинское обещание или "
                           "ложный дефицит: режет охват и доверие")
    whips = [s["whip"][0] for b in beats for s in b.get("shots", []) if s.get("whip") and not s.get("whip_back")]
    if whips and min(whips) < 0 < max(whips):
        err.append("хлёсты «вперёд по сюжету» в разные стороны: одна сторона на ролик (правило 180°), "
                   "обратный — с \"whip_back\": true")
    first = next((s for s in beats[0]["shots"] if "src" in s), None)
    last = next((s for s in reversed(beats[-1]["shots"]) if "src" in s), None)   # последний кадр ролика, не первый план фразы
    if first and last and first["src"] != last["src"]:
        err.append(f"петля: финал на {last['src']}, а начало на {first['src']} — конец = начало")
    return err


def check_timeline(shots, events, sfx_peaks, caps=None, total=None):
    """Правила по рассчитанному таймингу: длина планов, первая склейка, пик riser на склейке; с субтитрами (caps —
    [{t0, t1, text}]) ещё: хук дочитывается до первой склейки, группа субтитров не идёт через склейку, последняя
    группа успевает прочитаться."""
    err = []
    cuts = [s["t0"] for s in shots[1:]]
    if caps:
        need = len(caps[0]["text"]) / READ_CPS + READ_PAD
        if cuts and need > cuts[0] + 0.02:
            err.append(f"хук «{caps[0]['text']}» читается {need:.2f} с, а склейка на {cuts[0]:.2f} с: короче хук")
        for c in caps:
            for k in cuts:
                if c["t0"] + 0.05 < k < c["t1"] - 0.05:
                    err.append(f"субтитр «{c['text']}» ({c['t0']:.2f}–{c['t1']:.2f} с) идёт через склейку {k:.2f} с:"
                               " план на начало группы или «|» перед словом склейки")
        if total is not None:
            last = caps[-1]; need = len(last["text"]) / READ_CPS + READ_PAD
            if total - last["t0"] < need - 0.02:
                err.append(f"последний субтитр «{last['text']}» стоит {total - last['t0']:.2f} с, нужно {need:.2f}: больше tail")
        for c in caps[1:]:
            need = len(c["text"]) / READ_CPS + READ_PAD
            if c["t1"] - c["t0"] > need + CAP_HOLD_PAD + 0.02 and not c.get("gap"):
                err.append(f"субтитр «{c['text']}» стоит {c['t1'] - c['t0']:.2f} с при чтении {need:.2f}: "
                           "дольше чтения + 0.6 с глаз уходит с рисунка — следующая группа раньше")
    changes = [b["t0"] for a, b in zip(shots, shots[1:]) if (b.get("src") or b.get("kind")) != (a.get("src") or a.get("kind"))]
    for c0 in [0.0] + changes:
        n = sum(c0 <= c < c0 + 30.0 for c in changes)
        if n > MAX_SRC_CHANGES_30S:
            err.append(f"{n} смен рисунка за 30 с с {c0:.1f} с > {MAX_SRC_CHANGES_30S}: перегрузка, держите рисунок дольше"); break
    for a, b in zip(shots, shots[1:]):                # правило 30°: соседние окна одного рисунка — на ступень
        if a.get("src") and a.get("src") == b.get("src") and "from" in a and "from" in b and not b.get("jump"):
            pa, pb = a.get("to", a["from"]), b["from"]
            ratio = pb[2] / pa[2]; shift = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
            if 1 / STEP_MIN < ratio < STEP_MIN and shift < STEP_SHIFT * max(pa[2], pb[2]):
                err.append(f"склейка {b['t0']:.2f} с: окна одного рисунка {a['src']} почти одинаковы (×{ratio:.2f}, сдвиг "
                           f"{shift:.0f}) — скачок; крупнее/мельче хотя бы в {STEP_MIN} раза или \"jump\": true")
    for s in shots[:-1]:
        if s["t1"] - s["t0"] < MIN_SHOT_SEC - 0.02:
            err.append(f"план {s['t0']:.2f}–{s['t1']:.2f} с — {s['t1'] - s['t0']:.2f} с < {MIN_SHOT_SEC}: не успеть прочитать")
    for s in shots:
        d = s["t1"] - s["t0"]
        if d > MAX_SHOT_SEC + 0.02:
            err.append(f"план {s['t0']:.2f}–{s['t1']:.2f} с идёт {d:.2f} с > {MAX_SHOT_SEC}: разрежьте его вторым планом")
    if len(shots) > 1 and shots[1]["t0"] > FIRST_CUT_SEC:
        err.append(f"первая склейка на {shots[1]['t0']:.2f} с > {FIRST_CUT_SEC}: хук без смены картинки")
    for e in events:
        if e.get("kind") == "sfx" and e.get("name") == "riser":
            peak = e["t"] + (sfx_peaks["riser"] if e.get("align") == "start" else 0.0)
            gap = min(abs(peak - s["t0"]) for s in shots[1:]) if len(shots) > 1 else 9.0
            if gap > RISER_PEAK_ON_CUT:
                err.append(f"пик riser на {peak:.2f} с не на склейке (ближайшая в {gap:.2f} с)")
    return err


SOUND_MAX = {"swoosh_deep": 3, "oof": 2, "riser": 2,   # «появление важного» и «провал» обесцениваются повтором
             "shock": 1, "level_up": 2, "fast_glitch": 3, "typing": 2}   # звуки владельца 24.10 (library.json: avoid)
SOUND_REPEAT_SEC = 4.0     # один и тот же звук не ближе 4 с (кроме swoosh на хлёсте и тихих свистов наезда)
SOUND_DENSE_WIN, SOUND_DENSE_MAX = 0.5, 2   # не больше двух звуков в 0.5 с (Мёрч, «2,5 слоя»): предупреждение


def check_sounds(plan):
    """Звуки по reel.sound_plan: лимиты повторов (library.json, поле avoid) и одинаковые звуки подряд."""
    err = []
    for name, mx in SOUND_MAX.items():
        n = sum(p["name"] == name for p in plan)
        if n > mx:
            err.append(f"звук «{name}» {n} раз > {mx}: повтор обесценивает смысл звука (library.json, avoid)")
    loud = [p for p in plan if not p.get("soft")]
    by = {}
    for p in loud:
        by.setdefault(p["name"], []).append(p)
    for name, ps in by.items():
        ps = sorted(ps, key=lambda p: p["peak"])
        for a, b in zip(ps, ps[1:]):
            if b["peak"] - a["peak"] < SOUND_REPEAT_SEC and not (name == "swoosh" and (a.get("whip") or b.get("whip"))):
                err.append(f"«{name}» на {a['peak']:.2f} и {b['peak']:.2f} с — ближе {SOUND_REPEAT_SEC} с: повтор слышен")
    return err


def check_cut_sounds(plan, shots, near=0.35):
    """Каждая склейка слышна (владелец 24.10: «не должно быть тишины, на новой картинке свуш»): у каждой смены плана
    есть пик звука ближе near секунд — смысловой или переходный."""
    peaks = [p["peak"] for p in plan]
    return [f"склейка {s['t0']:.2f} с без звука: переход проваливается (свист, короткий свист или смысловой звук)"
            for s in shots[1:] if not any(abs(s["t0"] - q) <= near for q in peaks)]


def sound_warnings(plan):
    pk = sorted(p["peak"] for p in plan)
    for i, t in enumerate(pk):
        n = sum(t <= q < t + SOUND_DENSE_WIN for q in pk[i:])
        if n > SOUND_DENSE_MAX:
            return [f"{n} звука за {SOUND_DENSE_WIN} с с {t:.2f} с — звук спорит с текстом, разведите"]
    return []


# Знания базы, которые обязан применить каждый рилс (владелец 23.10: «не вижу, чтобы во всех новых рилсах автоматически
# использовались все эти знания»): docs/reels_knowledge/apply_checklist.json. Как сделать пункт — решает рилс; рендер не
# начнётся, пока у каждого пункта в passport.knowledge нет номера фразы или отказа с причиной.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKLIST_PATH = os.path.join(ROOT_DIR, "docs", "reels_knowledge", "apply_checklist.json")
BRAND_PATH = os.path.join(ROOT_DIR, "docs", "reels_brand.json")
SKIP_MIN_CHARS = 15
SHAME_WORDS = (r"\bсоберись", r"\bперестань", r"возьми себя в руки", r"\bхватит ныть", r"\bлентя[йи]",
               r"вот почему ты вс[её] срываешь")
# Волна 8 (23.10, docs/reels_knowledge/08_deep_persuasion_funnel.md): давление включает реактивность (мета-анализы
# 2025–2026, r ≈ .20) — призыв без «обязательно», «срочно», «успей», «должен»; закреп «напиши 1 / 2» — дословно пример
# приманки вовлечения из правил Instagram 2024; смысловые петли не реже раза в 12 с (Kallaway 20–30 с — мнение, берём строже
# с запасом); у рилса-серии — название и номер серии (персонаж-сериал: System1/IPA, Duolingo).
CONTROL_WORDS = (r"\bобязательно\b", r"\bсрочно\b", r"\bуспей", r"\bнемедленно\b", r"\bты должн", r"\bвы должн",
                 r"\bнужно перейти", r"\bпереходи прямо", r"\bне упусти")
# Приманки удержания и вовлечения (09 §19: «досмотри до конца», «поставь лайк» — минус к лайкам и доверию; Instagram режет
# «просьбы о реакции») — во фразах, подписи и закрепе.
ENGAGEMENT_BAIT = (r"досмотри", r"до конца ролика", r"\bставь лайк", r"\bпоставь лайк", r"\bлайкни", r"\bподписывайся",
                   r"\bжми сердечко")
BAIT_PATTERNS = (r"напиши\s*[«\"']?\d", r"пиши\s*[«\"']?\d", r"\b1\b[^.]{0,40}\b2\b.{0,20}(напиши|пиши|ставь)",
                 r"(напиши|пиши|ставь)[^.]{0,30}\b1\b[^.]{0,40}\b2\b", r"ставь\s*[+❤🔥]")
LOOP_GAP_MAX = 12.5        # с: между смысловыми петлями (passport.knowledge.meaning_loops) и от начала до первой
COVER_MAX_WORDS, COVER_MAX_CHARS = 4, 24
CAPTION_HEAD = 125         # Instagram показывает ~125 знаков подписи до «ещё»: ключевая фраза ниши — в них
LENGTH_WORK_SEC = 40.0     # рабочая вилка 20–40 с (07 §8 п.35, мнение) — предупреждение


def load_json(p, default):
    import json
    return json.load(open(p, encoding="utf8")) if os.path.exists(p) else default


def brand_beat(spec, brand):
    name = (brand or {}).get("brand", "")
    return next((i for i, b in enumerate(spec.get("beats", [])) if name and name.lower() in clean(b["text"]).lower()), None)


def _norm_q(t):
    return re.sub(r"\s+", " ", re.sub(r"[«»\"'.,:;!?…]", "", clean(t))).strip().lower()


def _inventory_proof(v, bs, beats):
    """Решение «во фразе» доказывается (рилс эп.01 v5: 955 голых номеров фраз без единой правки сценария — владелец
    назвал это бумагой): "quote" — слова, которые стоят в этой фразе дословно, или "evidence" — событие кадра или звука
    этой фразы: "fx:<вид или звук>" (fx:strike — зачёркивание), "shot:<рисунок или вид плана>", "gaps"."""
    if not isinstance(v, dict) or not (v.get("quote") or v.get("evidence")):
        return (f"{v!r} — голый номер фразы: нужно {{\"beats\": [N], \"quote\": слова этой фразы}} или "
                "\"evidence\": \"fx:…\" / \"shot:…\" / \"gaps\" — чем именно фраза делает приём")
    if v.get("quote"):
        q = _norm_q(v["quote"])
        if len(q) < 2 or not any(q in _norm_q(beats[b]["text"]) for b in bs):
            return f"цитата «{v['quote']}» не стоит дословно во фразе {bs}"
        return ""
    kind, _, name = str(v["evidence"]).partition(":")
    for b in bs:
        bb = beats[b]
        if kind == "gaps" and bb.get("gaps"):
            return ""
        if kind == "fx" and any(name in (e.get("kind"), e.get("name")) or (name == "strike" and "strike_at" in e)
                                for e in bb.get("fx", [])):
            return ""
        if kind == "shot" and any(name in (s.get("src"), s.get("kind"), s.get("sound")) for s in bb.get("shots", [])):
            return ""
    return f"доказательства «{v['evidence']}» нет во фразе {bs}"


def _beats_of(v):
    if isinstance(v, bool):
        return []
    if isinstance(v, int):
        return [v]
    if isinstance(v, list):
        return [x for x in v if isinstance(x, int) and not isinstance(x, bool)]
    if isinstance(v, dict):
        return [x for k, x in v.items() if k != "skip" and isinstance(x, int) and not isinstance(x, bool)]
    return []


def check_knowledge(spec, checklist=None, brand=None):
    """Каждый пункт чек-листа знаний закрыт в паспорте фразой или отказом с причиной; пункты kind=code — проверка кодом."""
    checklist = checklist if checklist is not None else load_json(CHECKLIST_PATH, {"items": []})
    brand = brand if brand is not None else load_json(BRAND_PATH, {})
    pp = spec.get("passport") or {}; kn = pp.get("knowledge") or {}
    beats = spec.get("beats", []); n = len(beats); cta = pp.get("cta_beat"); br = brand_beat(spec, brand)
    err = []
    for it in checklist.get("items", []):
        if it["kind"] != "beat":
            continue
        v = kn.get(it["id"])
        where = f"знание «{it['id']}» ({it['title']}; {it['source']})"
        if v is None or v == "TODO":
            err.append(f"{where}: в passport.knowledge нет ни номера фразы, ни отказа с причиной"); continue
        if isinstance(v, dict) and "skip" in v:
            if len(str(v["skip"]).strip()) < SKIP_MIN_CHARS:
                err.append(f"{where}: отказ без причины — напишите, почему здесь не к месту")
            continue
        bs = _beats_of(v)
        if not bs or any(not 0 <= b < n for b in bs):
            err.append(f"{where}: {v!r} — не номер фразы 0…{n - 1}"); continue
        for f in it.get("fields", []):
            if not isinstance(v, dict) or f not in v:
                err.append(f"{where}: нужны поля {it['fields']}")
        rule = it.get("check", "")
        lo, hi = min(bs), max(bs)
        bad = ((rule == "beat == 0" and lo != 0) or
               (rule == "beat < cta" and cta is not None and lo >= cta) or
               (rule == "beat <= cta" and cta is not None and lo > cta) or
               (rule == "beat >= cta" and cta is not None and hi < cta) or
               (rule == "beat < brand" and br is not None and lo >= br) or
               (rule.startswith("authority") and isinstance(v, dict) and "loss" in v and "authority" in v
                and not 1 <= v["authority"] - v["loss"] <= 2))
        if bad:
            err.append(f"{where}: фраза {v!r} нарушает «{rule}» (призыв — {cta}, продукт — {br})")
    low = " ".join(clean(b["text"]).lower() for b in beats)
    for pat in CONTROL_WORDS:
        m = re.search(pat, low)
        if m:
            err.append(f"давящее слово «{m.group(0)}» — включает реактивность: зритель делает наоборот (08 §1, мета-анализы "
                       "реактивности); призыв — как выбор («захочешь — …»)")
    pin = pp.get("pinned_comment") or brand.get("pinned_comment_default") or ""
    for pat in BAIT_PATTERNS:
        if re.search(pat, pin.lower()):
            err.append(f"закреплённый комментарий «{pin[:60]}…» — приманка вовлечения («напиши цифру»): пример из правил "
                       "Instagram о снижении показов (08 §2); нужен открытый вопрос о зрителе")
            break
    texts = [("фраза", clean(b["text"]).lower()) for b in beats] + [("подпись", str(pp.get("caption", "")).lower()),
                                                                   ("закреп", str(pp.get("pinned_comment", "")).lower())]
    for where, x in texts:
        m = next((re.search(q, x) for q in ENGAGEMENT_BAIT if re.search(q, x)), None)
        if m:
            err.append(f"{where}: «{m.group(0)}» — приманка удержания/реакции: портит доверие, Instagram режет охват (09 §19)")
    ser = pp.get("series")
    if ser is not None and not (isinstance(ser, dict) and ser.get("name") and ser.get("episode")):
        err.append('серия рилса: "series": {"name": …, "episode": N} — название и номер (08 §2, персонаж-сериал)')
    for pat in SHAME_WORDS:
        m = re.search(pat, low)
        if m:
            err.append(f"стыдящее повеление «{m.group(0)}» — зритель с СДВГ слышит упрёк (07 §8 п.33, правила Meta)")
    labels = pp.get("labels")
    if labels is None:
        err.append('в паспорте нет "labels" — терминов-ярлыков рилса (не больше двух, 07 §8 п.18)')
    elif len(labels) > 2:
        err.append(f"ярлыков {len(labels)} > 2: третий термин «нарочно усложняет» (07 §8 п.18)")
    cover = (pp.get("cover") or {}).get("text", "")
    if not cover:
        err.append('в паспорте нет "cover": {"text": …} — обложка = первый рисунок + ясный текст (07 §8 п.11)')
    elif len(cover.split()) > COVER_MAX_WORDS or len(cover) > COVER_MAX_CHARS:
        err.append(f"текст обложки «{cover}» длиннее {COVER_MAX_WORDS} слов / {COVER_MAX_CHARS} знаков: в сетке не читается")
    cap = pp.get("caption", "")
    if not cap:
        err.append('в паспорте нет "caption" — подписи с ключевой фразой ниши и 3–5 хэштегами (07 §8 п.24)')
    else:
        tags = re.findall(r"#\w+", cap)
        if not any(k.lower() in cap[:CAPTION_HEAD].lower() for k in brand.get("niche_keywords", [])):
            err.append(f"в первых {CAPTION_HEAD} знаках подписи нет ключевой фразы ниши {brand.get('niche_keywords')}")
        if not 3 <= len(tags) <= brand.get("max_hashtags", 5):
            err.append(f"хэштегов {len(tags)}: нужно 3–{brand.get('max_hashtags', 5)}")
    if not (pp.get("pinned_comment") or brand.get("pinned_comment_default")):
        err.append("нет закреплённого комментария (passport.pinned_comment или brand.pinned_comment_default)")
    hv = pp.get("hook_variants") or []
    hook = clean(beats[0]["text"]) if beats else ""
    if not 3 <= len(hv) <= 5:
        err.append(f"вариантов хука {len(hv)}: нужно 3–5 для пробных Reels (07 §8 п.3)")
    lib = load_json(os.path.join(ROOT_DIR, "assets", "sfx", "reels", "library.json"), {})
    peak = (lib.get("riser") or {}).get("peak_sec", 1.65)
    hv = [variant_text(v) for v in hv]
    for v in hv:                                    # вариант дочитывается до пика riser — до первой склейки (тот же расчёт,
        need = len(clean(v)) / READ_CPS + READ_PAD  # что check_timeline для хука); длиннее — склейка уедет за 2 с
        if len(clean(v)) > HOOK_MAX_CHARS or need > peak + 0.02:
            mx = int((peak - READ_PAD) * READ_CPS)
            err.append(f"вариант хука «{v}» читается {need:.2f} с > пика riser {peak} с: короче (≤ {mx} знаков)")
    if len({clean(v).lower() for v in hv} | {hook.lower()}) != len(hv) + 1:
        err.append("варианты хука повторяют друг друга или сам хук")
    return err


def knowledge_timing(spec, beat_t0, total):
    """Ре-хук стоит на 35–60 % ролика; смысловые петли (meaning_loops) — не реже раза в LOOP_GAP_MAX с от начала до
    призыва (по рассчитанному времени фраз)."""
    kn = (spec.get("passport") or {}).get("knowledge") or {}
    err = []
    bs = _beats_of(kn.get("re_hook"))
    if bs and bs[0] < len(beat_t0):
        share = beat_t0[bs[0]] / total
        if not 0.35 <= share <= 0.60:
            err.append(f"ре-хук (фраза {bs[0]}) на {share:.0%} ролика — нужно 35–60 % (01: Kallaway, heyDominik)")
    loops = sorted(set(b for b in _beats_of(kn.get("meaning_loops")) if b < len(beat_t0)))
    if loops:
        cta = (spec.get("passport") or {}).get("cta_beat")
        end = beat_t0[cta] if cta is not None and cta < len(beat_t0) else total
        ts = [0.0] + [beat_t0[b] for b in loops] + [end]
        for a, b in zip(ts, ts[1:]):
            if b - a > LOOP_GAP_MAX + 0.02:
                err.append(f"смысловых петель нет {b - a:.1f} с ({a:.1f}–{b:.1f} с) > {LOOP_GAP_MAX}: новый вопрос, поворот "
                           "или обещание — чаще (08 §3)")
    return err


def check_overlays(boxes, picture_h=None):
    """Рукописные надписи и маркер (boxes — [(фраза, текст, x0, y0, x1, y1)] по туши, в пикселях экрана 1080×1920)
    целиком в безопасной зоне: не под шапкой Reels, не под подписью, не у края и не под колонкой кнопок; и не в полосе
    субтитров ниже картинки (эп.01 v4: «Прости, долго» ушло под субтитры — y задан под 1100 и пересчитался в 1405)."""
    err = []
    for i, txt, x0, y0, x1, y1 in boxes:
        where = []
        if picture_h and y1 > picture_h: where.append(f"низ {y1:.0f} > {picture_h} — в полосе субтитров (y в reel.json — под 1100)")
        if y0 < SAFE_TOP: where.append(f"верх {y0:.0f} < {SAFE_TOP} (шапка Reels)")
        if y1 > SAFE_BOTTOM: where.append(f"низ {y1:.0f} > {SAFE_BOTTOM} (подпись и кнопки)")
        if x0 < SAFE_SIDE or x1 > 1080 - SAFE_SIDE: where.append(f"x {x0:.0f}–{x1:.0f} у края экрана")
        if y1 > RIGHT_COL_FROM and x1 > SAFE_RIGHT_COL: where.append(f"правый край {x1:.0f} под колонкой кнопок")
        if where:
            err.append(f"фраза {i}: надпись «{txt}» — " + "; ".join(where))
    return err


def check_cta(spec, beat_t0, total):
    """Призыв (passport.cta_beat) начинается не позже чем за 5 с до конца: позже — до него не досматривают."""
    k = (spec.get("passport") or {}).get("cta_beat")
    if k is None or k >= len(beat_t0):
        return ['в паспорте нет "cta_beat" — номера фразы призыва: без него не проверить, что призыв успевают увидеть']
    if beat_t0[k] > total - CTA_BEFORE_END + 0.02:
        return [f"призыв (фраза {k}) начинается на {beat_t0[k]:.1f} с, за {total - beat_t0[k]:.1f} с до конца < {CTA_BEFORE_END}"]
    return []


def syllables(w):
    return len(re.findall(r"[аеёиоуыэюяaeiouy]", w.lower()))


HAND_WORDS_MAX, HAND_WIN = 3, 7.0   # рукописных слов не больше 3 за 7 с (п.1.15), два текста не в одни 0.5 с
ARCS, CHARGES = ("t", "r"), ("+", "-", "−")


def check_writing(events, shots):
    """Рукописный текст до первой склейки — ошибка: хук работает одной картинкой и одним субтитром (п.1.15)."""
    cut = shots[1]["t0"] if len(shots) > 1 else 9e9
    return [f"рукописное «{e['text']}» на {e['t']:.2f} с — до первой склейки {cut:.2f} с: в хуке один текст — субтитр"
            for e in events if e.get("kind") in ("write", "mark") and e["t"] < cut - 0.01]


def warnings(spec, shots, total, events=()):
    """Гипотезы без доказанного порога — печатаются, рендер не останавливают."""
    out = []
    hand = sorted((e["t"], e["text"]) for e in events if e.get("kind") in ("write", "mark"))
    for i, (t, _) in enumerate(hand):
        n = sum(len(clean(x).split()) for tt, x in hand[i:] if tt < t + HAND_WIN)
        if n > HAND_WORDS_MAX:
            out.append(f"рукописных слов {n} за {HAND_WIN:.0f} с с {t:.2f} с > {HAND_WORDS_MAX}: читать некогда (п.1.15)"); break
    for (t1, x1), (t2, x2) in zip(hand, hand[1:]):
        if t2 - t1 < 0.5:
            out.append(f"«{x1}» и «{x2}» начаты через {t2 - t1:.2f} с: два текста сразу (п.1.15)")
    beats = spec.get("beats", [])
    arcs = [b.get("arc") for b in beats]; ch = [b.get("charge") for b in beats]
    if any(arcs):                                       # кривая «напряжение — разрядка» (п.1.23), если размечена
        for i, (a, b) in enumerate(zip(arcs, arcs[1:])):
            if a == b == "r":
                out.append(f"фразы {i} и {i + 1} — две разрядки подряд: напряжение падает (п.1.23)")
        run = 1
        for i in range(1, len(ch)):
            run = run + 1 if ch[i] and ch[i] == ch[i - 1] else 1
            if run > 2:
                out.append(f"фразы {i - 2}–{i} — три подряд со знаком «{ch[i]}»: качели ценности замерли (п.1.23)")
        if ch and ch[-1] not in ("+", None):
            out.append("рилс кончается на «−»: конец на «+» (п.1.23)")
    starts = [(e["t"], e["kind"]) for e in events if e.get("kind") in ("punch", "write", "mark", "circle", "arrow")]
    starts += [(s["t0"], "вход наездом" if s.get("zoom_in") else "хлёст") for s in shots[1:] if s.get("zoom_in") or s.get("whip")]
    starts += [(s["t0"] + a["t"], "жест куклы") for s in shots if s.get("kind") == "doll"
               for a in s.get("actions", []) if a.get("do") in ("tilt", "look", "pose", "paw")]
    starts.sort()
    for (t1, k1), (t2, k2) in zip(starts, starts[1:]):    # Mital, Smith, Henderson: держит одно движущееся
        if t2 - t1 < ONE_MOTION_SEC:
            out.append(f"{k1} {t1:.2f} и {k2} {t2:.2f} с — два движения сразу: разведите на {ONE_MOTION_SEC} с")
    if total > LENGTH_WORK_SEC:
        out.append(f"рилс {total:.1f} с > {LENGTH_WORK_SEC:.0f}: каждую фразу сверх вилки проверить сжатием (07 §8 п.35)")
    pt = sorted(e["t"] for e in events if e.get("kind") == "punch")
    for a, b in zip(pt, pt[1:]):
        if b - a < PUNCH_MIN_GAP:
            out.append(f"наезды на {a:.2f} и {b:.2f} с — ближе {PUNCH_MIN_GAP} с: второй слабее, оставьте сильнейший")
    for s in shots:
        if s["t0"] >= LATE_ZONE * total and s["t1"] - s["t0"] > LATE_SHOT_SEC + 0.02:
            out.append(f"финал: план {s['t0']:.2f}–{s['t1']:.2f} с длиннее {LATE_SHOT_SEC} с — в последних 20 % уходят чаще")
    lens = [len(clean(b["text"])) for b in beats]          # ритм: три фразы одной длины подряд — метроном (матрица B)
    for i in range(len(lens) - 2):
        if max(lens[i:i + 3]) - min(lens[i:i + 3]) <= 2:
            out.append(f"фразы {i}–{i + 2} одной длины ({lens[i]}–{max(lens[i:i + 3])} знаков): ритм ровный, короткую — рядом с длинной")
            break
    for i, b in enumerate(spec.get("beats", [])[:3]):
        for w in clean(b["text"]).split():
            if syllables(w) > LONG_WORD_SYLLABLES:
                out.append(f"фраза {i}: «{w}» — {syllables(w)} слогов в начале ролика: проще слово (тест незнакомца)")
    return out


if __name__ == "__main__":
    import json
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import reel
    spec = json.load(open(os.path.join(sys.argv[1], "reel.json"), encoding="utf8"))
    log_p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "reels_log.json")
    log = json.load(open(log_p, encoding="utf8")) if os.path.exists(log_p) else []
    errs = (check_spec(spec, set(reel.SFX)) + check_passport(spec, log, os.path.relpath(sys.argv[1])) + check_knowledge(spec)
            + check_hook(spec, log, os.path.relpath(sys.argv[1])) + check_hook_layers(spec) + check_call_to_comment(spec)
            + check_brand_and_face(spec) + check_hook_steal(spec, log, os.path.relpath(sys.argv[1]))
            + check_matrix(spec)
            + check_coverage(spec, log, os.path.relpath(sys.argv[1])) + check_human(spec)
            + check_inventory(spec, log, os.path.relpath(sys.argv[1])))
    print("\n".join("✗ " + e for e in errs) or "✓ reel.json по правилам (тайминг проверит reel.py при рендере)")
    sys.exit(1 if errs else 0)
