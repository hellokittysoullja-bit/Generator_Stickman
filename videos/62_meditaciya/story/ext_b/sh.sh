#!/bin/bash
# usage: sh.sh sid t1,t2,.. out.jpg — кадры на эти моменты в один лист
cd "$(dirname "$0")"; B=/tmp/claude-0/-home-user/7605bd81-268a-5536-b1b7-f9696ca784cb/scratchpad/a62b; rm -rf $B/sheets/$1; python3 make.py $1 --sheet $2 >/dev/null && python3 - "$1" "$3" "$B" <<'PY'
import sys,glob
from PIL import Image
fs=sorted(glob.glob(f'{sys.argv[3]}/sheets/{sys.argv[1]}/*.png'))
ims=[Image.open(f).resize((405,720)) for f in fs]
W=Image.new('RGB',(405*len(ims),720))
for i,im in enumerate(ims): W.paste(im,(405*i,0))
W.save(sys.argv[2])
PY
