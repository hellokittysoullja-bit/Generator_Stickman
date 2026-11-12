"""Сцена «Дима, 01:47»: Blender 4.2 без интерфейса.

    bl -b --factory-startup -P scene.py -- still [--pct 50] [--engine EEVEE|WORKBENCH] [--nochars]
    bl -b --factory-startup -P scene.py -- anim  [--frames 1-90]

Фон — 3D (room.py, EEVEE + Freestyle-линия), герои — Grease Pencil (chars.py рисует контуры в пикселях
кадра, здесь они ложатся на плоскость перед диваном, точно в свои пиксели).
"""
import math
import os
import sys
import time

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
PYLIB = os.environ.get('NAPARNIK_PYLIB')
if PYLIB:
    sys.path.insert(0, PYLIB)

import room  # noqa: E402

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['still']
MODE = argv[0]


def opt(name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


PCT = int(opt('--pct', '100'))
ENGINE = opt('--engine', 'EEVEE')
OUT = opt('--out', HERE)
FPS = 30
NFRAMES = 90

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)

sc = bpy.context.scene
cam = room.camera()

# пиксели, где chars.py рисует экран телефона и огонёк (свет в 3D ставится туда же)
import chars  # noqa: E402

info = room.build(screen_px=chars.SCREEN_PX, flame_px=chars.FLAME_PX)

# ---------------------------------------------------------------- рендер

r = sc.render
r.resolution_percentage = PCT
r.fps = FPS
sc.view_settings.view_transform = 'Standard'
sc.view_settings.look = 'None'
sc.view_settings.exposure = 0.0
if ENGINE == 'WORKBENCH':
    r.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'FLAT'
    sc.display.shading.color_type = 'MATERIAL'
else:
    r.engine = 'BLENDER_EEVEE_NEXT'
    ee = sc.eevee
    ee.taa_render_samples = int(opt('--samples', '24'))
    ee.use_shadows = True
    ee.shadow_ray_count = 1
    ee.shadow_step_count = 6
    ee.use_raytracing = False
    ee.use_gtao = True
    ee.gtao_distance = 0.4

# Freestyle: тонкая тёмная линия у 3D-предметов (силуэт, грани, складки), как у фонов образцов
if '--nofs' not in argv:
    r.use_freestyle = True
    r.line_thickness_mode = 'ABSOLUTE'
    r.line_thickness = 1.0
    vl = sc.view_layers[0]
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    fs.crease_angle = math.radians(140)
    ls = fs.linesets[0] if fs.linesets else fs.linesets.new('lines')
    ls.select_by_visibility = True
    ls.select_by_edge_types = True
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = True
    ls.select_by_collection = True
    ls.collection = info['outside']
    ls.collection_negation = 'EXCLUSIVE'
    lst = ls.linestyle
    lst.color = (0.02, 0.018, 0.04)
    lst.alpha = 0.75
    lst.thickness = 2.2 * PCT / 100
    lst.chaining = 'PLAIN'
    # дрожь руки: толщина по шуму вдоль линии
    tm = lst.thickness_modifiers.new('noise', 'NOISE')
    tm.amplitude = 1.0 * PCT / 100
    tm.period = 30
    tm.blend = 'ADD'

# компоновка: свечение ярких мест (окна дома, луна, цифры, экран, огонёк)
sc.use_nodes = True
nt = sc.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
rl = nt.nodes.new('CompositorNodeRLayers')
gl = nt.nodes.new('CompositorNodeGlare')
gl.glare_type = 'FOG_GLOW'
gl.quality = 'HIGH'
gl.threshold = 0.9
gl.size = 8
gl.mix = -0.55
comp = nt.nodes.new('CompositorNodeComposite')
nt.links.new(rl.outputs['Image'], gl.inputs['Image'])
nt.links.new(gl.outputs['Image'], comp.inputs['Image'])
r.use_compositing = True

# ---------------------------------------------------------------- герои (Grease Pencil)

if '--nochars' not in argv:
    import gpdraw  # noqa: E402
    gpdraw.build(MODE, NFRAMES, info)

sc.frame_start = 1
sc.frame_end = NFRAMES

if MODE == 'still':
    sc.frame_set(int(opt('--frame', '1')))
    r.filepath = os.path.join(OUT, opt('--name', 'still.png'))
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print('RENDER_TIME %.1f s' % (time.time() - t), flush=True)
elif MODE == 'anim':
    a, b = (opt('--frames', '1-%d' % NFRAMES)).split('-')
    sc.frame_start, sc.frame_end = int(a), int(b)
    r.image_settings.file_format = 'PNG'
    r.filepath = os.path.join(OUT, 'frames', 'f_')
    t = time.time()
    bpy.ops.render.render(animation=True)
    print('RENDER_TIME %.1f s for %d frames' % (time.time() - t, sc.frame_end - sc.frame_start + 1), flush=True)
elif MODE == 'blend':
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'scene.blend'))
