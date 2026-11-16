#!/bin/bash
# Снимок незакоммиченной работы (код художников и клипы) в ветку wip/stories, не трогая main и рабочую папку.
# Нужен на случай лимита или падения сессии: git fetch origin wip/stories && git checkout origin/wip/stories -- <пути>
set -e
cd "$(dirname "$0")/.."
export GIT_INDEX_FILE=$(mktemp)
git read-tree HEAD
git add -A videos/7[5-9]_*/story videos/8[0-9]_*/story docs 2>/dev/null
git add -f videos/7[5-9]_*/story/clips/*.mp4 videos/8[0-9]_*/story/clips/*.mp4 2>/dev/null || true
tree=$(git write-tree)
parent=$(git rev-parse -q --verify origin/wip/stories || git rev-parse HEAD)
c=$(git commit-tree "$tree" -p "$parent" -m "WIP snapshot $(date -u +%FT%TZ): story reels 75-78 code and clips")
rm -f "$GIT_INDEX_FILE"
git push -q origin "$c:refs/heads/wip/stories" && echo "snapshot $c"
