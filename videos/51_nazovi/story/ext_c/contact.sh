#!/bin/bash
# contact.sh sNN N [w] — лист из N равномерных кадров готового клипа в /tmp/a51c/cNN.jpg
cd "$(dirname "$0")/.."
id=$1; n=$2; w=${3:-330}
rm -rf /tmp/a51c/ct_$id; mkdir -p /tmp/a51c/ct_$id
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 clips/$id.mp4)
fs=""
for i in $(seq 0 $((n-1))); do
 t=$(python3 -c "print(round($d*($i+0.5)/$n,3))")
 ffmpeg -loglevel error -y -ss $t -i clips/$id.mp4 -frames:v 1 /tmp/a51c/ct_$id/f$i.png
 fs="$fs /tmp/a51c/ct_$id/f$i.png"
done
python3 ext_c/sheet.py /tmp/a51c/c$id.jpg $fs --w $w
