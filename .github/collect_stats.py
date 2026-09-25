# Сводит ответ API о выпусках в stats.json: текущие счетчики и снимок на каждый день.
#
#   collect_stats.py <прошлый stats.json> <releases.json>  > stats.json
#
# История хранится по дням: последний снимок дня заменяет прежний того же дня, так что
# файл растет на одну строку в сутки, сколько бы раз ни запускался сбор.

import json, sys
from datetime import datetime, timezone

old = json.load(open(sys.argv[1]))
releases = json.load(open(sys.argv[2]))

rows = []
for r in releases:
    if r.get("draft"):
        continue
    dmg = sum(a["download_count"] for a in r.get("assets", []) if a["name"].endswith(".dmg"))
    rows.append({"tag": r["tag_name"], "published": r.get("published_at"), "downloads": dmg})
rows.sort(key=lambda x: x["published"] or "")

now = datetime.now(timezone.utc)
today = now.strftime("%Y-%m-%d")
total = sum(x["downloads"] for x in rows)

history = [h for h in old.get("history", []) if h.get("date") != today]
history.append({"date": today, "total": total, "by": {x["tag"]: x["downloads"] for x in rows}})
history.sort(key=lambda h: h["date"])

json.dump({"updated": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "total": total,
           "releases": rows, "history": history}, sys.stdout, ensure_ascii=False, indent=1)
