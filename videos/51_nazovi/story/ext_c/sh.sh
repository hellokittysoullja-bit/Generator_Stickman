#!/bin/bash
# sh.sh sNN t1,t2,... — лист кадров в /tmp/a51c/sNN.jpg
cd "$(dirname "$0")"
python3 make.py $1 --sheet $2 2>&1 | grep -v "^s[0-9]* sheet" | tail -5
rm -f /tmp/a51c/$1_*.png
python3 - "$1" "$2" <<'P'
import sys,subprocess
sid,ts=sys.argv[1],sys.argv[2].split(",")
fs=[f"/tmp/a51c/tmp/sheets/{sid}/{sid}_{float(t):.2f}.png" for t in ts]
subprocess.check_call(["python3","sheet.py",f"/tmp/a51c/{sid}.jpg"]+fs+["--w",sys.argv[3] if len(sys.argv)>3 else "330"])
P
