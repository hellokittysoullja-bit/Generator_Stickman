"""Библиотека оригиналов: каждая картинка, которую сгенерировала модель (кадры эпизодов с забракованными вариантами,
рисунки рилсов, позы и лица куклы, эталоны героя), лежит в library/cat/originals/ байт в байт, как пришла из шлюза
или как была положена в репозиторий (25.10, слово владельца: «библиотека, которая всё пополняется: оригиналы всех
сгенерированных фото с котом, старых и новых, и всегда пополняется с новой генерацией»).

Пополнение само: llm_gateway.Gateway.image() зовёт capture() на каждую полученную картинку. Выключить — CAT_LIBRARY=0
(так делают тесты). Повтор той же картинки (тот же sha256) не дублируется: к записи добавляется новое место, где она
используется. В git копия того же файла места не занимает — одинаковое содержимое хранится одним объектом.

    python scripts/cat_library.py --scan      # собрать все оригиналы, уже лежащие в репозитории, и пересобрать галерею
    python scripts/cat_library.py --gallery   # только пересобрать README и превью
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.environ.get("CAT_LIBRARY_DIR") or os.path.join(ROOT, "library", "cat")
THUMB_W = 360

# Что в репозитории — оригинал генерации (а не производная: маски, листы, увеличенные src, обложки).
SCAN = [
    ("videos/*/frames/*.png", "кадр эпизода", "Gemini 3.1 Flash Image (кадры длинных роликов)"),
    ("videos/*/reel/gen/*.png", "рисунок рилса", "GPT-Image-2 medium (scripts/reel_draw.py)"),
    ("look/hero.png", "герой: эталон", "референс героя"),
    ("look/states/*.png", "герой: состояние", "эталон состояния героя"),
    ("look/style/*.png", "образец стиля", "образец стиля"),
    ("experiments/alive_cat/doll/assets/hero_*.png", "кукла: поза", "GPT-Image-2 (позы рига)"),
    ("experiments/alive_cat/doll/faces/*_src.png", "кукла: лицо", "исходник лица рига"),
    ("experiments/alive_cat/doll/beckon.png", "кукла: поза", "поза рига"),
    ("experiments/alive_cat/doll/point.png", "кукла: поза", "поза рига"),
    ("experiments/alive_cat/doll/assets/envelope.png", "предмет", "ассет пилота куклы"),
]
SKIP = re.compile(r"_mask\.png$")


def enabled():
    return os.environ.get("CAT_LIBRARY", "1") != "0"


def _paths():
    o = os.path.join(LIB, "originals"); t = os.path.join(LIB, "thumbs"); os.makedirs(o, exist_ok=True); os.makedirs(t, exist_ok=True)
    return o, t, os.path.join(LIB, "catalog.json")


def load():
    _, _, c = _paths()
    return json.load(open(c, encoding="utf8")) if os.path.exists(c) else []


def save(cat):
    _, _, c = _paths()
    cat.sort(key=lambda r: (r.get("date", ""), r["file"]))
    tmp = c + ".tmp"; json.dump(cat, open(tmp, "w", encoding="utf8"), ensure_ascii=False, indent=1); os.replace(tmp, c)


def _ext(data):
    return ".jpg" if data[:3] == b"\xff\xd8\xff" else ".webp" if data[8:12] == b"WEBP" else ".png"


def _slug(s):
    s = re.sub(r"[^0-9A-Za-z_-]+", "_", s).strip("_")
    return s[:48] or "image"


def _size(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return list(im.size)
    except Exception:
        return None


def _thumb(src, dst):
    from PIL import Image
    with Image.open(src) as im:
        im = im.convert("RGB"); im.thumbnail((THUMB_W, THUMB_W * 2)); im.save(dst, "JPEG", quality=84)


def add(data, name, kind, **meta):
    """Положить картинку (байты) в библиотеку. Возвращает запись каталога; та же картинка второй раз не копируется."""
    o, t, _ = _paths()
    if not data:
        raise ValueError(f"{name}: пустой файл")
    sha = hashlib.sha256(data).hexdigest()
    cat = load()
    rec = next((r for r in cat if r["sha256"] == sha), None)
    used = meta.pop("used_in", None)
    if rec is None:
        date = meta.pop("date", None) or datetime.date.today().isoformat()
        fn = f"{date}_{_slug(name)}_{sha[:8]}{_ext(data)}"
        p = os.path.join(o, fn)
        with open(p + ".tmp", "wb") as f:
            f.write(data)
        os.replace(p + ".tmp", p)
        _thumb(p, os.path.join(t, fn.rsplit(".", 1)[0] + ".jpg"))
        rec = dict(file=fn, sha256=sha, bytes=len(data), size=_size(p), date=date, kind=kind, used_in=[], **meta)
        cat.append(rec)
    else:
        for k, v in meta.items():
            if v and not rec.get(k): rec[k] = v
    if used and used not in rec["used_in"]:
        rec["used_in"].append(used)
    save(cat)
    return rec


def capture(images, model, prompt, size=None, quality=None, price=None):
    """Вызов из шлюза: каждая новая картинка генерации — в библиотеку. Ошибка библиотеки генерацию не ломает."""
    if not enabled():
        return
    who = " ".join(os.path.relpath(a, ROOT) if os.path.exists(a) else a for a in sys.argv[:3])
    for k, data in enumerate(images):
        try:
            add(data, f"gen_{_slug(model)}", "генерация", model=model, prompt=prompt, gen_size=size, quality=quality,
                price=price if k == 0 else 0, source=who)
        except Exception as e:                       # библиотека — не повод потерять оплаченную картинку
            print(f"  библиотека: не сохранено ({e})", file=sys.stderr)
    gallery()


def _git_date(path):
    out = subprocess.run(["git", "-C", ROOT, "log", "--diff-filter=A", "--format=%as", "--", path],
                         capture_output=True, text=True).stdout.split()
    return out[-1] if out else None


def _prompt_for(path):
    side = path[:-4] + ".json"
    if os.path.exists(side):
        try:
            j = json.load(open(side, encoding="utf8"))
            return j.get("prompt"), j.get("model"), j.get("price")
        except ValueError:
            pass
    m = re.match(r".*/videos/([^/]+)/frames/(\d+)\.png$", path)
    if m:
        rep = os.path.join(ROOT, "videos", m.group(1), "media_plan", "frames_report.json")
        if os.path.exists(rep):
            r = json.load(open(rep, encoding="utf8"))
            fr = next((f for f in r.get("frames", []) if f.get("index") == int(m.group(2)) - 1), None)
            if fr:
                return fr.get("prompt"), r.get("model"), None
    return None, None, None


def scan(extra=()):
    """Все оригиналы, уже лежащие в репозитории (и прежние версии из истории git), — в библиотеку."""
    import glob
    n0 = len(load())
    for pat, kind, origin in SCAN:
        for p in sorted(glob.glob(os.path.join(ROOT, pat))):
            if SKIP.search(p):
                continue
            rel = os.path.relpath(p, ROOT)
            prompt, model, price = _prompt_for(p)
            add(open(p, "rb").read(), rel.replace("/", "_").rsplit(".", 1)[0], kind, used_in=rel, origin=origin,
                prompt=prompt, model=model, price=price, date=_git_date(rel))
            for sha, date in _history(rel):           # прежние версии того же файла (перерисованные кадры)
                data = subprocess.run(["git", "-C", ROOT, "cat-file", "-p", sha], capture_output=True).stdout
                add(data, rel.replace("/", "_").rsplit(".", 1)[0] + "_old", kind, used_in=f"{rel} (прежняя версия)",
                    origin=origin, date=date)
    import fnmatch                                     # удалённые из репозитория оригиналы (снятые как брак) — из истории
    hist = subprocess.run(["git", "-C", ROOT, "log", "--all", "--format=", "--name-only", "--", "*.png", "*.jpg"],
                          capture_output=True, text=True).stdout.split()
    for rel in sorted(set(hist)):
        if os.path.exists(os.path.join(ROOT, rel)) or SKIP.search(rel):
            continue
        hit = next(((k, o) for pat, k, o in SCAN if fnmatch.fnmatch(rel, pat)), None)
        if not hit:
            continue
        for sha, date in _history(rel):
            data = subprocess.run(["git", "-C", ROOT, "cat-file", "-p", sha], capture_output=True).stdout
            if data:
                add(data, rel.replace("/", "_").rsplit(".", 1)[0], hit[0], used_in=f"{rel} (удалён из репозитория)",
                    origin=hit[1], date=date)
    for p, kind, origin in extra:
        if os.path.exists(p):
            add(open(p, "rb").read(), os.path.basename(p).rsplit(".", 1)[0], kind, used_in=p, origin=origin)
    gallery()
    return len(load()) - n0


def _history(rel):
    log = subprocess.run(["git", "-C", ROOT, "log", "--all", "--format=%H %as", "--", rel], capture_output=True, text=True).stdout
    seen, out = set(), []
    cur = subprocess.run(["git", "-C", ROOT, "rev-parse", "--verify", "-q", f"HEAD:{rel}"], capture_output=True,
                         text=True).stdout.strip()
    for line in log.splitlines():
        c, d = line.split()
        b = subprocess.run(["git", "-C", ROOT, "rev-parse", "--verify", "-q", f"{c}:{rel}"], capture_output=True,
                           text=True).stdout.strip()
        if b and b != cur and b not in seen:
            seen.add(b); out.append((b, d))
    return out


def gallery():
    """README.md библиотеки: превью по видам, ссылка на оригинал, где используется, промпт."""
    cat = load()
    groups = {}
    for r in cat:
        groups.setdefault(r["kind"], []).append(r)
    total = sum(r["bytes"] for r in cat)
    lines = ["# Библиотека оригиналов: кот и всё, что сгенерировано", "",
             f"Картинок: **{len(cat)}**, {total / 1e6:.0f} МБ. Оригиналы — `originals/` байт в байт, как пришли из модели "
             "(PNG без пересжатия); `thumbs/` — превью для этой страницы; `catalog.json` — промпт, модель, цена, где "
             "используется.", "",
             "Пополняется сама: каждая генерация через шлюз (`llm_gateway.Gateway.image`) кладёт картинку сюда, "
             "включая забракованные варианты. Собрать уже лежащее в репозитории: `python scripts/cat_library.py --scan`.", ""]
    for kind in sorted(groups):
        rs = sorted(groups[kind], key=lambda r: (r.get("date") or "", r["file"]))
        lines += [f"## {kind} ({len(rs)})", "", "| превью | оригинал | где | промпт |", "|---|---|---|---|"]
        for r in rs:
            th = "thumbs/" + r["file"].rsplit(".", 1)[0] + ".jpg"
            sz = "×".join(map(str, r["size"])) if r.get("size") else ""
            used = "<br>".join(f"`{u}`" for u in r.get("used_in", [])[:3]) or (r.get("source") or "")
            pr = (r.get("prompt") or "").replace("|", "/").replace("\n", " ")
            pr = (pr[:220] + "…") if len(pr) > 220 else pr
            lines.append(f"| ![]({th}) | [{r['file']}](originals/{r['file']})<br>{sz}, {r.get('date') or ''} | {used} | {pr} |")
        lines.append("")
    with open(os.path.join(LIB, "README.md"), "w", encoding="utf8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true"); ap.add_argument("--gallery", action="store_true")
    ap.add_argument("--extra", nargs="*", default=[], help="ещё файлы: путь — вне репозитория (эталоны сайта)")
    a = ap.parse_args()
    if a.scan:
        print("добавлено", scan([(p, "эталон сайта", "сайт «Напарник»") for p in a.extra]))
    if a.gallery or not a.scan:
        gallery()
    print(len(load()), "картинок в", os.path.relpath(LIB, ROOT))
