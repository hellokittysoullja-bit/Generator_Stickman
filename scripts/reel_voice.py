#!/usr/bin/env python3
"""Голос рилса через Lumean: один заказ на весь текст, пословный тайминг, кэш по тексту и шаблону.

Выход — `<reel_dir>/voice/`: `voice.wav` (48 кГц, громкость −16 LUFS), `words.json` ([{word, start, end}] в естественном
времени дорожки, слово в слово как `reel.tokens`) и `meta.json` (текст, шаблон, заказ). Раскладку фраз по ролику (пик
riser, немые паузы, перебивка) делает `reel.py`: он режет эту дорожку по фразам и ставит куски на свои места, поэтому
правка монтажа не требует новой платной озвучки.

Шаблон голоса — `LUMEAN_REEL_TEMPLATE_ID` или `LUMEAN_TEMPLATE_ID` из `.env`; ключ — `LUMEAN_API_KEY`, только `.env`.

    python scripts/reel_voice.py videos/01_sdvg_pismo/reel [--force]
"""
import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import lumean_tts as L  # noqa: E402
import reel  # noqa: E402

TARGET_LUFS = -16.0


def load_env():
    p = os.path.join(ROOT, ".env")
    for line in open(p, encoding="utf8") if os.path.exists(p) else ():
        m = re.match(r"\s*([A-Z_]+)\s*=\s*(.*)\s*$", line)
        if m and m.group(2) and m.group(1) not in os.environ:
            os.environ[m.group(1)] = m.group(2)


def phrase_texts(beats):
    """Текст для голоса: без разметки (`*`, `|`), фраза — строка."""
    return [reel.clean(b["text"]).strip() for b in beats]


def word_times(text, words, rows):
    """Пословный тайминг по посимвольному выравниванию Lumean. Нормализация голоса может прочитать «3» как «три» —
    такие слова не совпадают посимвольно и получают время соседей (между концом предыдущего и началом следующего)."""
    spoken = "".join(c for c, _, _ in rows)
    sm = difflib.SequenceMatcher(None, text, spoken, autojunk=False)
    t2a = {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            t2a[a + k] = b + k
    out, pos = [], 0
    for w in words:
        token = reel.clean(w)
        i = text.find(token, pos); pos = i + len(token)
        idx = [t2a[j] for j in range(i, i + len(token)) if j in t2a and text[j].isalnum()]
        out.append(dict(word=token, start=rows[idx[0]][1], end=rows[idx[-1]][2]) if idx else dict(word=token, start=None, end=None))
    for k, w in enumerate(out):                       # слово без совпадения — между соседями
        if w["start"] is None:
            prev = next((x["end"] for x in reversed(out[:k]) if x["start"] is not None), 0.0)
            nxt = next((x["start"] for x in out[k + 1:] if x["start"] is not None), prev + 0.4)
            w["start"], w["end"] = prev + 0.02, max(prev + 0.05, nxt - 0.02)
    return out


def loudnorm_wav(src, dst):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", f"loudnorm=I={TARGET_LUFS}:TP=-1.5:LRA=11",
                    "-ar", str(reel.SR), "-ac", "2", dst], check=True)


def build(reel_dir, force=False):
    load_env()
    key = os.environ.get("LUMEAN_API_KEY")
    tpl = os.environ.get("LUMEAN_REEL_TEMPLATE_ID") or os.environ.get("LUMEAN_TEMPLATE_ID")
    if not key or not tpl:
        raise SystemExit("нужны LUMEAN_API_KEY и LUMEAN_REEL_TEMPLATE_ID (или LUMEAN_TEMPLATE_ID) в .env")
    spec = json.load(open(os.path.join(reel_dir, "reel.json"), encoding="utf8"))
    words, _spans = reel.tokens(spec["beats"])
    text = "\n".join(phrase_texts(spec["beats"]))
    sig = hashlib.sha1(f"{tpl}\n{text}".encode()).hexdigest()[:16]
    out = os.path.join(reel_dir, "voice"); os.makedirs(out, exist_ok=True)
    meta_p = os.path.join(out, "meta.json")
    if not force and os.path.exists(meta_p) and json.load(open(meta_p, encoding="utf8")).get("sig") == sig:
        print("голос уже озвучен для этого текста и шаблона:", out); return out
    with tempfile.TemporaryDirectory() as tmp:
        res = L.process_section(key, tpl, tmp, 0, "reel", text, os.path.basename(os.path.dirname(os.path.abspath(reel_dir))))
        if not res.get("audio_path"):
            raise SystemExit(f"озвучка не получена: {res.get('reason')}")
        if not res.get("alignment"):
            raise SystemExit("Lumean не дал посимвольного выравнивания — без него субтитры и склейки не привязать к голосу")
        loudnorm_wav(res["audio_path"], os.path.join(out, "voice.wav"))
        times = word_times(text, words, res["alignment"])
    json.dump(times, open(os.path.join(out, "words.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    json.dump(dict(sig=sig, template=tpl, order=res.get("order_id"), text=text), open(meta_p, "w", encoding="utf8"),
              ensure_ascii=False, indent=1)
    print(f"голос: {out}/voice.wav, слов {len(times)}, заказ {res.get('order_id')}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("reel_dir"); ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    build(a.reel_dir, a.force)
