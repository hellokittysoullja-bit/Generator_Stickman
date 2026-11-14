#!/bin/bash
# usage: sh.sh sid t1,t2,.. out
cd "$(dirname "$0")"; rm -rf /tmp/a60c/sheets/$1; python3 make.py $1 --sheet $2 >/dev/null && python3 - "$1" "$3" <<'PY'
import sys,glob
from PIL import Image
fs=sorted(glob.glob(f'/tmp/a60c/sheets/{sys.argv[1]}/*.png'))
ims=[Image.open(f).resize((405,720)) for f in fs]
W=Image.new('RGB',(405*len(ims),720))
for i,im in enumerate(ims): W.paste(im,(405*i,0))
W.save(sys.argv[2])
PY
