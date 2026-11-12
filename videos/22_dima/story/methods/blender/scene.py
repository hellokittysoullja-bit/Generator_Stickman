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

# ---------------------------------------------------------------- герои (Grease Pencil)

HEROES = '--nochars' not in argv
if HEROES:
    import gpdraw  # noqa: E402
    gpdraw.build(MODE, NFRAMES, info)

# Два слоя рендера: комната (с Freestyle) и герои (только Grease Pencil, прозрачный фон), затем
# герои кладутся поверх комнаты в компоновщике. В одном слое линии Freestyle рисуются ПОВЕРХ
# Grease Pencil (Freestyle не знает о нём) и просвечивают сквозь лицо и руку.
vl_room = sc.view_layers[0]
vl_room.name = 'room'
if HEROES:
    vl_room.layer_collection.children['heroes'].exclude = True
    vl_h = sc.view_layers.new('heroes')
    vl_h.use_freestyle = False
    for ch in vl_h.layer_collection.children:
        ch.exclude = ch.name != 'heroes'
    r.film_transparent = True

# компоновка: герои поверх комнаты, затем свечение ярких мест (окна дома, луна, цифры, экран, огонёк)
sc.use_nodes = True
nt = sc.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
BG = opt('--bg')   # готовый фон комнаты (EXR): в анимации комната не рендерится заново, только герои
if BG:
    vl_room.use = False
    rl = nt.nodes.new('CompositorNodeImage')
    rl.image = bpy.data.images.load(BG)
    img = rl.outputs['Image']
else:
    rl = nt.nodes.new('CompositorNodeRLayers')
    rl.layer = 'room'
    img = rl.outputs['Image']
if HEROES:
    rh = nt.nodes.new('CompositorNodeRLayers')
    rh.layer = 'heroes'
    ao = nt.nodes.new('CompositorNodeAlphaOver')
    ao.premul = 0.0
    nt.links.new(img, ao.inputs[1])
    nt.links.new(rh.outputs['Image'], ao.inputs[2])
    img = ao.outputs['Image']
gl = nt.nodes.new('CompositorNodeGlare')
gl.glare_type = 'FOG_GLOW'
gl.quality = 'HIGH'
gl.threshold = 0.9
gl.size = 8
gl.mix = -0.55
# виньетка: края кадра темнее, как у ночных кадров образцов
em = nt.nodes.new('CompositorNodeEllipseMask')
em.width, em.height = 0.95, 0.80
bl = nt.nodes.new('CompositorNodeBlur')
bl.filter_type = 'FAST_GAUSS'
bl.use_relative = True
bl.factor_x = bl.factor_y = 30
nt.links.new(em.outputs['Mask'], bl.inputs['Image'])
vm = nt.nodes.new('CompositorNodeMixRGB')
vm.blend_type = 'MULTIPLY'
nt.links.new(bl.outputs['Image'], vm.inputs[0])
nt.links.new(gl.outputs['Image'], vm.inputs[1])
vm.inputs[2].default_value = (0.55, 0.55, 0.62, 1)
inv = nt.nodes.new('CompositorNodeMath')
inv.operation = 'SUBTRACT'
inv.inputs[0].default_value = 1.0
nt.links.new(bl.outputs['Image'], inv.inputs[1])
nt.links.new(inv.outputs[0], vm.inputs[0])
sa = nt.nodes.new('CompositorNodeSetAlpha')
sa.mode = 'REPLACE_ALPHA'
sa.inputs['Alpha'].default_value = 1.0
comp = nt.nodes.new('CompositorNodeComposite')
nt.links.new(img, gl.inputs['Image'])
nt.links.new(vm.outputs['Image'], sa.inputs['Image'])
nt.links.new(sa.outputs['Image'], comp.inputs['Image'])
r.use_compositing = True
r.image_settings.color_mode = 'RGB'

sc.frame_start = 1
sc.frame_end = NFRAMES

if opt('--border'):
    # кусок кадра для проверки деталей: --border x0,y0,x1,y1 в пикселях 1080x1920
    x0, y0, x1, y1 = [float(v) for v in opt('--border').split(',')]
    r.use_border = True
    r.use_crop_to_border = True
    r.border_min_x, r.border_max_x = x0 / 1080, x1 / 1080
    r.border_min_y, r.border_max_y = 1 - y1 / 1920, 1 - y0 / 1920

if MODE == 'still':
    sc.frame_set(int(opt('--frame', '1')))
    r.filepath = os.path.join(OUT, opt('--name', 'still.png'))
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print('RENDER_TIME %.1f s' % (time.time() - t), flush=True)
elif MODE == 'roombg':
    # одна комната без героев и без компоновки, в линейный EXR — фон для анимации
    r.use_compositing = False
    r.image_settings.file_format = 'OPEN_EXR'
    r.image_settings.color_depth = '16'
    r.image_settings.color_mode = 'RGBA'
    r.filepath = os.path.join(OUT, 'room_bg.exr')
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print('RENDER_TIME %.1f s' % (time.time() - t), flush=True)
elif MODE == 'anim':
    a, b = (opt('--frames', '1-%d' % NFRAMES)).split('-')
    sc.frame_start, sc.frame_end = int(a), int(b)
    r.image_settings.file_format = 'JPEG'   # кадры только для склейки в mp4; JPEG 95 — в 5 раз меньше места
    r.image_settings.quality = 95
    r.filepath = os.path.join(OUT, 'frames', 'f_')
    t = time.time()
    bpy.ops.render.render(animation=True)
    print('RENDER_TIME %.1f s for %d frames' % (time.time() - t, sc.frame_end - sc.frame_start + 1), flush=True)
elif MODE == 'blend':
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'scene.blend'))
