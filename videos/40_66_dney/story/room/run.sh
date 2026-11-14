#!/bin/bash
# python3/node: слои героев плана → клип ../clips/<id>.mp4 → лист кадров; кадры слоёв удаляются (диск).
# ./run.sh s02 [s03 ...]
set -e
cd "$(dirname "$0")"
export NODE_PATH=${NODE_PATH:-/opt/node-tools/node_modules}
export NP=${NP:-2} NJ=${NJ:-2}   # CPU делим с другими агентами: не больше 2 процессов
(cd chars_src && python3 heroes40e.py && python3 heroes40l.py)
for id in "$@"; do
  python3 chars_src/make_cfg.py $id
  (cd chars_src && node render25.js $NP $id)
  du -sh chars/$id
  python3 assemble.py clip --id $id --jobs $NJ
  python3 assemble.py sheet --id $id --n 6
  if [ -z "$KEEP" ]; then rm -rf chars/$id/L_*; fi
done
