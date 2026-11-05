#!/usr/bin/env python3
"""Разбор ниши YouTube: что залетает у длинных роликов (владелец 03.11 и 05.11: «что в моей нише будет вирусным»).

YouTube Data API v3 (ключ — `.env`, YOUTUBE_API_KEY; в вывод не попадает). По каждому запросу — ролики средней (4–20 мин)
и длинной (20+ мин) длины за последние DAYS дней, по просмотрам; потом карточки роликов и каналов. «Залёт» —
просмотры / подписчики канала: у канала на 2 тыс. ролик на 100 тыс. — тема, а не аудитория канала.
Квота: search.list — 100 единиц, videos/channels.list — 1 на 50 штук; QUERIES × 2 длины ≈ 7 000 из 10 000 в сутки.

    python scripts/niche_scan.py docs/long_knowledge/niche_scan_0511.json [--days 60]
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request

API = "https://www.googleapis.com/youtube/v3/"
QUERIES = [
    "сдвг", "сдвг у взрослых", "прокрастинация", "как перестать прокрастинировать", "лень", "как побороть лень",
    "нет сил ничего делать", "не могу начать делать", "дофамин", "дофаминовое голодание", "концентрация внимания",
    "как вернуть фокус", "клиповое мышление", "зависимость от телефона", "думскроллинг", "выгорание",
    "дисциплина", "сила воли", "привычки", "как всё успевать", "тайм менеджмент", "продуктивность",
    "мотивация", "перфекционизм", "откладываю на потом", "тревожность", "перегруз мозга", "усталость после работы",
    "как учиться", "память и мозг", "режим дня", "утро продуктивное", "одиночество и прокрастинация",
    "почему я ничего не делаю", "психология лени",
]


def key():
    for line in open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"), encoding="utf-8"):
        if line.startswith("YOUTUBE_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    sys.exit("нет YOUTUBE_API_KEY в .env")


def call(method, **p):
    p["key"] = KEY
    with urllib.request.urlopen(API + method + "?" + urllib.parse.urlencode(p), timeout=60) as r:
        return json.load(r)


def minutes(iso):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0.0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d*1440 + h*60 + mi + s/60


def main():
    global KEY
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--days", type=int, default=60)
    a = ap.parse_args()
    KEY = key()
    after = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=a.days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    found = {}
    for q in QUERIES:
        for dur in ("medium", "long"):
            try:
                r = call("search", part="id", q=q, type="video", videoDuration=dur, order="viewCount", maxResults=50,
                         publishedAfter=after, relevanceLanguage="ru", regionCode="RU")
            except Exception as e:                       # квота кончилась — сохраняем то, что есть
                print(f"стоп на «{q}» ({dur}): {e}", file=sys.stderr)
                break
            for it in r.get("items", []):
                found.setdefault(it["id"]["videoId"], set()).add(q)
        else:
            continue
        break
    ids = list(found)
    vids, chans = {}, {}
    for i in range(0, len(ids), 50):
        for v in call("videos", part="snippet,statistics,contentDetails", id=",".join(ids[i:i+50])).get("items", []):
            vids[v["id"]] = v
    cids = list({v["snippet"]["channelId"] for v in vids.values()})
    for i in range(0, len(cids), 50):
        for c in call("channels", part="statistics", id=",".join(cids[i:i+50])).get("items", []):
            chans[c["id"]] = int(c["statistics"].get("subscriberCount", 0) or 0)
    now = dt.datetime.now(dt.timezone.utc)
    rows = []
    for vid, v in vids.items():
        sn, st = v["snippet"], v.get("statistics", {})
        subs = chans.get(sn["channelId"], 0)
        views = int(st.get("viewCount", 0) or 0)
        days = (now - dt.datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00"))).days
        rows.append(dict(id=vid, title=sn["title"], ch=sn["channelTitle"], subs=subs, views=views, days=days,
                         min=round(minutes(v["contentDetails"].get("duration")), 1), ratio=views/max(subs, 1),
                         likes=int(st.get("likes", st.get("likeCount", 0)) or 0),
                         comments=int(st.get("commentCount", 0) or 0), q=sorted(found[vid]),
                         lang=sn.get("defaultAudioLanguage", "")))
    rows.sort(key=lambda r: -r["views"])
    json.dump(rows, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"роликов {len(rows)}, каналов {len(chans)}, запросов {len(QUERIES)}")


if __name__ == "__main__":
    main()
