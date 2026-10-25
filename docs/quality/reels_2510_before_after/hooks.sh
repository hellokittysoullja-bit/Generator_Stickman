#!/bin/bash
# Хуки было → стало подряд, со звуком: первые 7 с каждого рилса, подпись сверху.
set -e
D=$(dirname "$0"); B=/tmp/claude-0/-home-user-Generator-Stickman/7605bd81-268a-5536-b1b7-f9696ca784cb/scratchpad/before
F="/home/user/Generator_Stickman/assets/fonts/reels/Onest[wght].ttf"
V=/home/user/Generator_Stickman/videos
L=""
for r in 03_lenivyi 04_noch 05_ustal; do
  for w in was now; do
    src=$B/$r/reel.mp4; lab="БЫЛО"; col=0xB02020
    if [ $w = now ]; then src=$V/$r/reel/reel.mp4; lab="СТАЛО"; col=0x1E7A32; fi
    ffmpeg -v error -y -t 7.6 -i $src -vf "scale=540:960,drawbox=x=0:y=0:w=540:h=64:color=white@0.85:t=fill,drawtext=fontfile='$F':text='$lab · ${r#*_}':fontcolor=$col:fontsize=40:x=16:y=12" \
      -c:v libx264 -crf 20 -preset veryfast -c:a aac -b:a 160k -ar 48000 -ac 2 $D/h_${r}_$w.mp4
    L="$L file 'h_${r}_$w.mp4'\n"
  done
done
printf "$L" > $D/hooks.txt
ffmpeg -v error -y -f concat -safe 0 -i $D/hooks.txt -c copy $D/hooks_compare.mp4
ls -la $D/hooks_compare.mp4
