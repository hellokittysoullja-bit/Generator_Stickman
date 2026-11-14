#!/bin/bash
# usage: sh.sh sid t1,t2,.. out.jpg
cd "$(dirname "$0")"; S=/tmp/claude-0/-home-user/7605bd81-268a-5536-b1b7-f9696ca784cb/scratchpad/a62c/sheets/$1; rm -rf $S; python3 make.py $1 --sheet $2 >/dev/null && python3 - "$S" "$3" <<'PY'
import sys,glob
from PIL import Image
fs=sorted(glob.glob(sys.argv[1]+'/*.png'))
ims=[Image.open(f).resize((405,720)) for f in fs]
W=Image.new('RGB',(405*len(ims),720))
for i,im in enumerate(ims): W.paste(im,(405*i,0))
W.save(sys.argv[2])
PY
