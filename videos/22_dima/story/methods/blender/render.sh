#!/bin/bash
# Сцена «Дима, 01:47» в Blender 4.2 без экрана: 3D-комната (EEVEE + Freestyle) + герои Grease Pencil.
#
#   BLENDER_DIR=/путь/к/blender-4.2.3-linux-x64 ./render.sh still   # still.png 1080x1920 (~160 с на 4 ядрах)
#   BLENDER_DIR=...                              ./render.sh anim    # anim.mp4 3 с, 30 к/с (~2 мин фон + ~5 с/кадр)
#
# Нужно: портативный Blender 4.2 LTS (download.blender.org); в режиме -b он открывает GPU-контекст через EGL,
# поэтому рядом лежат libEGL.so.1 + libEGL_mesa.so.0 из пакетов Ubuntu libegl1 и libegl-mesa0 (распакованы
# dpkg -x в $EGL_DIR, систему не трогают) — рисует программный llvmpipe из уже стоящего libgl1-mesa-dri;
# shapely для Python 3.11 Блендера — в $PYLIB (pip install --target).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SCR="${SCRATCH:-/tmp/claude-0/-home-user/7605bd81-268a-5536-b1b7-f9696ca784cb/scratchpad/blender}"
BLENDER_DIR="${BLENDER_DIR:-$SCR/blender-4.2.3-linux-x64}"
EGL_DIR="${EGL_DIR:-$SCR/egl}"
export NAPARNIK_PYLIB="${PYLIB:-$SCR/pylib}"
export LD_LIBRARY_PATH="$EGL_DIR/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"
export __EGL_VENDOR_LIBRARY_FILENAMES="$EGL_DIR/usr/share/glvnd/egl_vendor.d/50_mesa.json"
export EGL_PLATFORM=surfaceless
B="$BLENDER_DIR/blender -b --factory-startup -P $HERE/scene.py --"
WORK="${WORK:-$SCR/out}"
mkdir -p "$WORK/frames"

case "${1:-still}" in
  still)
    $B still --pct 100 --samples 32 --out "$HERE" --name still.png ;;
  anim)
    # комната рендерится один раз (линейный EXR), в каждом кадре — только слой героев поверх неё
    $B roombg --nochars --pct 100 --samples 32 --out "$WORK"
    rm -f "$WORK"/frames/f_*.jpg
    $B anim --frames 1-90 --pct 100 --samples 8 --bg "$WORK/room_bg.exr" --out "$WORK"
    ffmpeg -y -loglevel error -framerate 30 -i "$WORK/frames/f_%04d.jpg" -c:v libx264 -pix_fmt yuv420p \
      -crf 18 -preset slow -movflags +faststart "$HERE/anim.mp4"
    rm -f "$WORK"/frames/f_*.jpg ;;
esac
