#!/usr/bin/env python3
"""Стыки ручного монтажа длинного ролика (edit.json) — форма переходов и подсказки до сборки (владелец 15.11).

  python scripts/long_montage.py videos/NN

transition_checks(video_dir) — ошибки формы поля "transition" плана (только там, где оно задано: без поля — ничего).
hints(video_dir) — СОВЕТЫ, сборку не останавливают (правило владельца 15.11: новое — только с его согласия). По окнам
edit.json на готовом холсте (canvas.prepare — та же бумага, что у сборки) на каждом стыке считается:
  * перепад средней яркости экрана (LUMA_JUMP): «чёрный кот крупно → белая бумага» — переход света или другое окно;
  * уход центра внимания (центр масс чернил по ширине, ATTENTION_SHIFT, тот же расчёт, что у montage_qc): глаз
    прыгает через кадр — окно ближе к прошлому центру или переход move/through, который ведёт глаз;
  * смена направления камеры внутри одной картинки: план с "to" шире "win" (отъезд) среди наездов — одно направление
    на группу планов одной мысли (MONTAGE_SPEC §1.3), смена — со сменой мысли (тогда в why);
  * переходы в видеохуке: есть, но не на каждом стыке;
  * картинка не на кремовой бумаге (canvas.prepare не нашёл бумагу по краю) без "dark_why" у кадра — одна бумага на
    ролик, тёмная сцена только осознанно.
Сцены на бумаге (stage) — своя картинка, их экран здесь не считается."""
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

LUMA_JUMP = 85.0          # перепад средней яркости экрана (0..255) на стыке, выше — совет; L03: медиана 21, худший 146;
                          # при 60 советов было 59 (свет на каждом третьем стыке — шаблон), при 85 — худшие
ATTENTION_SHIFT = 0.25    # = montage_qc THRESHOLDS["cut_attention_shift"]
HOOK_TRANS_SHARE_MAX = 0.5
MOTION_KINDS = ("move", "through")
GENERIC_RE = re.compile(r"\W*(переход|склейка|смена плана|эффект)\W*", re.I)


def _edit(video_dir):
    ep = os.path.join(video_dir, "edit.json")
    return (json.load(open(ep, encoding="utf-8")).get("frames") or {}) if os.path.exists(ep) else {}


def transition_checks(video_dir):
    """Ошибки формы переходов: вид, why по смыслу, звук по правилам звука (движение — со своим звуком, свет — без
    звук — как у простой склейки), не на первом плане ролика."""
    import long_transitions as lt
    err = []
    for n, v in _edit(video_dir).items():
        for k, p in enumerate(v.get("shots") or [], 1):
            tr = p.get("transition")
            if not tr:
                continue
            where = f"TRANSITION: фраза {n}, план {k}"
            try:
                lt.spec(p)
            except ValueError as e:
                err.append(f"{where}: {e}")
                continue
            why = (tr.get("why") or "").strip()
            if len(why.split()) < 3 or GENERIC_RE.fullmatch(why):
                err.append(f"{where}: why «{why}» — зачем этот переход по смыслу (что продолжается через склейку)")
            if n == "1" and k == 1:
                err.append(f"{where}: у первого плана ролика нет прошлого кадра — переходу не с чего начаться")
            if tr["kind"] in MOTION_KINDS and not p.get("sound"):
                err.append(f"{where}: переход «{tr['kind']}» — движение, ему нужен свой \"sound\" у плана")
            if tr["kind"] in MOTION_KINDS and (p.get("whip") or p.get("tear")):
                err.append(f"{where}: переход «{tr['kind']}» вместе с whip/tear — один переход на стык")
    return err


def _screens(video_dir):
    """{фраза: (холст, сдвиг)} для картинок с ручным монтажом."""
    from PIL import Image

    import assemble_frames as af
    import canvas
    rep = af.load_report(video_dir)
    out = {}
    for n in _edit(video_dir):
        i = int(n) - 1
        src, _ = af.frame_source(video_dir, i, rep.get(i) or {})
        if os.path.exists(src):
            cv, off, on_paper = canvas.prepare(Image.open(src))
            out[n] = (cv, off, on_paper)
    return out


def view_stats(cv, off, w):
    """(средняя яркость, центр внимания по ширине или None) экрана окна w=[cx, cy, ширина] (px рисунка)."""
    import camera
    SH, SW = cv.shape[:2]
    x0, y0, x1, y1 = camera.window(w[0] + off[0], w[1] + off[1], w[2], SW, SH)
    crop = cv[int(y0):int(y1), int(x0):int(x1)].astype(np.float32).mean(2)
    if crop.size == 0:
        return None, None
    crop = crop[::2, ::2]
    paper = float(np.percentile(crop, 90))
    ink = crop < paper - 40
    cx = float(np.nonzero(ink)[1].mean()/crop.shape[1]) if ink.sum() > 50 else None
    return float(crop.mean()), cx


def _end_win(p):
    if p.get("to"):
        return p["to"]
    w = p["win"]
    return [w[0], w[1], w[2]/1.04]                  # long_edit.PUSH: без "to" — медленный наезд 4 %


def hints(video_dir, screens=None):
    """Советы по стыкам ручного монтажа (список строк). Сборку не останавливают."""
    ed = _edit(video_dir)
    if not ed:
        return []
    screens = _screens(video_dir) if screens is None else screens
    out = []
    order = sorted(ed, key=int)
    prev = None                                      # (фраза, план, экран-статистика конца)
    for n in order:
        shots = ed[n].get("shots") or []
        sc = screens.get(n)
        signs = []
        if sc is not None and len(sc) > 2 and not sc[2] and not ed[n].get("dark_why"):
            out.append(f"PAPER: фраза {n} — картинка не на кремовой бумаге (тёмная или залитая сцена, чаще всего рисунок "
                       f"из библиотеки рилсов): весь ролик — одна бумага; исключение — осознанно, \"dark_why\" у кадра "
                       f"edit.json (ночь в истории), иначе другая картинка")
        for k, p in enumerate(shots, 1):
            if p.get("stage") or not p.get("win") or sc is None:
                prev = None
                continue
            lum_a, cx_a = view_stats(sc[0], sc[1], p["win"])
            if prev is not None and lum_a is not None:
                pn, pk, lum_p, cx_p = prev
                led = bool(p.get("transition") or p.get("whip") or p.get("tear"))
                where = f"фраза {n}, план {k} (после фразы {pn}, план {pk})"
                if abs(lum_a - lum_p) > LUMA_JUMP and not led:
                    out.append(f"LUMA: {where}: яркость экрана {lum_p:.0f} → {lum_a:.0f} — жёсткий рез глаз режет; "
                               f"\"transition\": {{\"kind\": \"light\"}} или окно с бумагой")
                if cx_p is not None and cx_a is not None and abs(cx_a - cx_p) > ATTENTION_SHIFT and not led:
                    out.append(f"ATTENTION: {where}: центр внимания {cx_p:.2f} → {cx_a:.2f} ширины — глаз прыгает; "
                               f"окно ближе к прошлому центру или переход move/through, который ведёт глаз")
            if p.get("to"):
                signs.append((k, 1 if p["to"][2] < p["win"][2] else -1, p))
            else:
                signs.append((k, 1, p))
            le, ce = view_stats(sc[0], sc[1], _end_win(p))
            prev = (n, k, le, ce)
        flips = [(a, b) for a, b in zip(signs, signs[1:]) if a[1] != b[1]]
        for a, b in flips:
            out.append(f"DIRECTION: фраза {n}, план {b[0]}: камера {'наезжает' if b[1] > 0 else 'отъезжает'} после "
                       f"{'наезда' if a[1] > 0 else 'отъезда'} плана {a[0]} той же картинки — одно направление на мысль "
                       f"(MONTAGE_SPEC §1.3); отъезд — \"to\" шире \"win\" только со сменой мысли")
    out += hook_transitions(video_dir, ed)
    return out


def hook_transitions(video_dir, ed=None):
    """В видеохуке переходы есть (стыки ведут глаз), но не на каждом стыке (иначе это шаблон «эффектов»)."""
    ed = _edit(video_dir) if ed is None else ed
    sb = os.path.join(video_dir, "storyboard.json")
    if not ed or not os.path.exists(sb):
        return []
    import script_parser
    blocks = script_parser.parse_blocks(os.path.join(video_dir, "script.txt"))
    hook = {str(i + 1) for i, b in enumerate(blocks) if b.get("section") == "HOOK"}
    plans = [p for n, v in ed.items() if n in hook for p in (v.get("shots") or [])]
    cuts = max(0, len(plans) - 1)
    led = sum(1 for p in plans if p.get("transition") or p.get("whip") or p.get("tear"))
    if not cuts:
        return []
    if led == 0:
        return [f"HOOK-TRANSITIONS: в видеохуке {cuts} стыков и ни одного перехода (хлёст, рваная бумага, move, through, "
                f"light) — хотя бы на поворотах мысли"]
    if led/cuts > HOOK_TRANS_SHARE_MAX:
        return [f"HOOK-TRANSITIONS: переходов {led} на {cuts} стыков — больше половины: это шаблон, а не смысл"]
    return []


def main():
    vd = os.path.abspath(sys.argv[1])
    err = transition_checks(vd)
    for e in err:
        print("✗", e)
    hs = hints(vd)
    for h in hs:
        print("·", h)
    print(f"Переходы: {'ошибок нет' if not err else f'{len(err)} ошибок'}; советов по стыкам: {len(hs)}")
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
