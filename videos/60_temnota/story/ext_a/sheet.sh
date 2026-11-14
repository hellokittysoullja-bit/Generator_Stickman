#!/bin/sh
# ./sheet.sh s01 0.0,0.5,1.0  → лист кадров /tmp/claude-0/a60/<id>_sheet.jpg
rm -rf /tmp/a60a/sheets/$1
python3 "$(dirname "$0")/make.py" $1 --sheet $2 >/dev/null && ffmpeg -y -loglevel error -pattern_type glob -i "/tmp/a60a/sheets/$1/$1_*.png" -vf scale=360:-1,tile=3x2 -update 1 /tmp/claude-0/a60/$1_sheet.jpg
