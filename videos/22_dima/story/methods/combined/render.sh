#!/bin/bash
# «Дима, 01:47» — совмещённый способ: комната Blender (проходы света, один раз) + слои героев SVG, сборка numpy.
#
#   ./render.sh passes   # проходы комнаты: 3 слоя глубины × (base, screen, flame) + линии Freestyle, ~1 раз на сцену
#   ./render.sh check    # контроль: полный рендер комнаты на t=1.3 против суммы проходов
#   ./render.sh anim     # anim.mp4 (кадры собираются в памяти и сразу идут в ffmpeg, на диск не пишутся)
#   ./render.sh still    # still.png, t = 1.3 с
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SCR="${SCRATCH:-/tmp/claude-0/-home-user/7605bd81-268a-5536-b1b7-f9696ca784cb/scratchpad/blender}"
BLENDER_DIR="${BLENDER_DIR:-$SCR/blender-4.2.3-linux-x64}"
EGL_DIR="${EGL_DIR:-$SCR/egl}"
PASSES="${PASSES:-$SCR/passes}"
export NAPARNIK_PYLIB313="${PYLIB313:-$SCR/pylib313}"     # OpenEXR (+ shapely) для системного Python
export LD_LIBRARY_PATH="$EGL_DIR/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"
export __EGL_VENDOR_LIBRARY_FILENAMES="$EGL_DIR/usr/share/glvnd/egl_vendor.d/50_mesa.json"
export EGL_PLATFORM=surfaceless
B="$BLENDER_DIR/blender -b --factory-startup -P $HERE/passes.py --"

case "${1:-anim}" in
  passes) $B passes --out "$PASSES" --over 1.5 --samples 40 --layout "$HERE/chars/layout.json" ;;
  check)  $B full --out "$PASSES" --over 1.5 --samples 40 --layout "$HERE/chars/layout.json" --t 1.3
          python3 "$HERE/assemble.py" check --passes "$PASSES" --full "$PASSES/full.exr" --t 1.3 --diff "$PASSES/check_diff.png" ;;
  anim)   python3 "$HERE/assemble.py" anim --passes "$PASSES" --chars "$HERE/chars" --frames 90 --crf 16 --out "$HERE/anim.mp4" ;;
  still)  python3 "$HERE/assemble.py" still --passes "$PASSES" --chars "$HERE/chars" --t 1.3 --out "$HERE/still.png" ;;
esac
