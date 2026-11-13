#!/bin/bash
# python3/node: слои героев плана → клип ../clips/<id>.mp4 → лист кадров; кадры слоёв удаляются (диск).
# ./run.sh s01 [s04 s14]
set -e
cd "$(dirname "$0")"
export NAPARNIK_PYLIB313=${NAPARNIK_PYLIB313:-/tmp/claude-0/-home-user/7605bd81-268a-5536-b1b7-f9696ca784cb/scratchpad/blender/pylib313}
export NODE_PATH=${NODE_PATH:-$(npm root -g)}
(cd chars_src && python3 heroes28e.py)
for id in "$@"; do
  python3 chars_src/make_cfg.py $id
  (cd chars_src && node render25.js ${NP:-3} $id)
  du -sh chars/$id
  python3 assemble.py clip --id $id --jobs ${NJ:-3}
  python3 assemble.py sheet --id $id --n 6
  if [ -z "$KEEP" ]; then rm -rf chars/$id/L_*; fi
done
