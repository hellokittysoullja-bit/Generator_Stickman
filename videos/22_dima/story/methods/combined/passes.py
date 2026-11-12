"""Проходы комнаты для мультиплана (Blender 4.2, без экрана). Один раз на сцену.

    bl -b --factory-startup -P passes.py -- passes --out DIR [--layout chars/layout.json] [--only far:base,...]
    bl -b --factory-startup -P passes.py -- full   --out DIR --t 1.3      # контрольный полный рендер

Слои глубины: far (стены, окно, улица, шторы, полка), floor (пол, коврик, банки, тапки), sofa (диван, подушка).
Для каждого слоя три прохода света — base (луна, окна дома, заполнение, мир, всё светящееся), screen (только свет
экрана, энергия SCREEN_E), flame (только огонёк, энергия FLAME_E). Свет линеен: кадр = base + s(t)·screen + f(t)·flame.
Объекты чужих слоёв невидимы для камеры, но отбрасывают тени, поэтому у каждого слоя нет дыр за передними.
Линии Freestyle — отдельным проходом (as_render_pass) только в base, только у предметов своего слоя.
Разрешение — OVER × 1080×1920 (запас под наезд камеры), тот же кадр, что у кадра 0 still.png Blender-пробы.
Выход — EXR half: <layer>_<pass>.exr (RGBA, премультиплицированная альфа) и <layer>_lines.exr.
"""
import json
import math
import os
import sys
import time

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import room  # noqa: E402
import timing  # noqa: E402

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['passes']
MODE = argv[0]


def opt(name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


OUT = opt('--out', os.path.join(HERE, 'passes'))
OVER = float(opt('--over', '1.5'))
SAMPLES = int(opt('--samples', '48'))
SCREEN_E = 18.0
FLAME_E = 9.0
# точки света в пикселях кадра 0 (1080×1920) и глубина (y мира); уточняются по chars/layout.json
LAYOUT = {'screen_px': [565, 755], 'flame_px': [1034, 916], 'screen_y': -0.62, 'flame_y': -0.80}
LAYERS = ('far', 'floor', 'sofa')
PASSES = ('base', 'screen', 'flame')

lay = opt('--layout')
if lay and os.path.exists(lay):
    LAYOUT.update(json.load(open(lay)))

os.makedirs(OUT, exist_ok=True)
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
sc = bpy.context.scene
cam = room.camera()          # кадр 0: та же камера, что у Blender-пробы
r = sc.render
r.resolution_x = int(round(1080 * OVER))
r.resolution_y = int(round(1920 * OVER))
r.resolution_percentage = 100


def render_ray(px, py):
    """Луч съёмочной камеры кадра 0 через пиксель (px, py) кадра 1080×1920."""
    tr, br, bl, tl = cam.data.view_frame(scene=sc)
    local = tl + (tr - tl) * (px / 1080) + (bl - tl) * (py / 1920)
    d = cam.matrix_world.to_3x3() @ local
    return cam.matrix_world.translation.copy(), d.normalized()


def on_y(px, py, y):
    o, d = render_ray(px, py)
    return o + d * ((y - o.y) / d.y)


sw = on_y(*LAYOUT['screen_px'], LAYOUT['screen_y'])
fw = on_y(*LAYOUT['flame_px'], LAYOUT['flame_y'])
info = room.build(screen_world=tuple(sw), flame_world=tuple(fw))
print('LIGHTS screen', tuple(round(v, 3) for v in sw), 'flame', tuple(round(v, 3) for v in fw), flush=True)

# ---------------------------------------------------------------- рендер

sc.view_settings.view_transform = 'Standard'
sc.view_settings.look = 'None'
r.engine = 'BLENDER_EEVEE_NEXT'
ee = sc.eevee
ee.taa_render_samples = SAMPLES
ee.use_shadows = True
ee.shadow_ray_count = 2
ee.shadow_step_count = 8
ee.use_raytracing = False
ee.use_gtao = True
ee.gtao_distance = 0.4
r.film_transparent = True
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
ls.collection_negation = 'INCLUSIVE'
lst = ls.linestyle
lst.color = (0.02, 0.018, 0.04)
lst.alpha = 0.75
lst.thickness = 2.2 * OVER
lst.chaining = 'PLAIN'
tm = lst.thickness_modifiers.new('noise', 'NOISE')
tm.amplitude = 1.0 * OVER
tm.period = 30
tm.blend = 'ADD'

COLL = {'far': [info['far'], info['outside'], info['shelf']], 'floor': [info['floor']], 'sofa': [info['sofa']]}
LINES = {'far': [info['far'], info['shelf']], 'floor': [info['floor']], 'sofa': [info['sofa']]}
# светящиеся предметы (небо, луна, дом напротив, цифры) — только в base
EMISSIVE = [o for o in info['outside'].objects] + [o for o in info['shelf'].objects if o.name.startswith(('seg', 'colon'))]
ALL_OBJ = [o for o in bpy.data.objects if o.type == 'MESH']
world = sc.world
WORLD_STR = world.node_tree.nodes['Background'].inputs[1].default_value
L = info['lights']
SL, FL = info['screen_light'], info['flame_light']


def layer_of(o):
    for k, cs in COLL.items():
        if any(o.name in c.objects for c in cs):
            return k
    return None


def lines_collection(layer):
    """Коллекция-зонтик для линий слоя (Freestyle берёт одну коллекцию)."""
    name = 'lines_' + layer
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    u = bpy.data.collections.new(name)
    for c in LINES[layer]:
        for o in c.objects:
            u.objects.link(o)
    return u


def setup(layer, light):
    """layer: имя слоя или None (вся комната); light: base/screen/flame/full."""
    for o in ALL_OBJ:
        vis = layer is None or layer_of(o) == layer
        if light in ('screen', 'flame') and o in EMISSIVE:
            vis = False
        o.visible_camera = vis
    for k in ('moon', 'fill', 'window'):
        L[k].hide_render = light in ('screen', 'flame')
    world.node_tree.nodes['Background'].inputs[1].default_value = WORLD_STR if light in ('base', 'full') else 0.0
    SL.hide_render = light not in ('screen', 'full')
    FL.hide_render = light not in ('flame', 'full')
    vl.use_freestyle = light in ('base', 'full')
    r.use_freestyle = vl.use_freestyle
    if layer is not None:
        ls.collection = lines_collection(layer)
        ls.select_by_collection = True
    else:
        ls.select_by_collection = True
        u = bpy.data.collections.get('lines_all') or bpy.data.collections.new('lines_all')
        if not u.objects:
            for lay_ in LAYERS:
                for c in LINES[lay_]:
                    for o in c.objects:
                        if o.name not in u.objects:
                            u.objects.link(o)
        ls.collection = u


def render_to(name, as_pass):
    """Рендер в EXR через компоновщик: Image и (если есть) Freestyle — отдельными файлами."""
    fs.as_render_pass = as_pass
    sc.use_nodes = True
    nt = sc.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    rl = nt.nodes.new('CompositorNodeRLayers')
    fo = nt.nodes.new('CompositorNodeOutputFile')
    fo.base_path = OUT
    fo.format.file_format = 'OPEN_EXR'
    fo.format.color_depth = '16'
    fo.format.color_mode = 'RGBA'
    fo.format.exr_codec = 'ZIP'
    fo.file_slots.clear()
    fo.file_slots.new(name + '_')
    nt.links.new(rl.outputs['Image'], fo.inputs[0])
    if as_pass and r.use_freestyle:
        fo.file_slots.new(name.rsplit('_', 1)[0] + '_lines_')
        nt.links.new(rl.outputs['Freestyle'], fo.inputs[1])
    comp = nt.nodes.new('CompositorNodeComposite')
    nt.links.new(rl.outputs['Image'], comp.inputs['Image'])
    r.use_compositing = True
    sc.frame_set(1)
    t = time.time()
    bpy.ops.render.render(write_still=False)
    dt = time.time() - t
    # компоновщик дописывает номер кадра: <name>_0001.exr -> <name>.exr
    for f in os.listdir(OUT):
        if f.endswith('_0001.exr'):
            os.replace(os.path.join(OUT, f), os.path.join(OUT, f[:-len('_0001.exr')] + '.exr'))
    print('PASS %s %.1f s' % (name, dt), flush=True)
    return dt


if MODE == 'passes':
    only = opt('--only')
    todo = [(a, b) for a in LAYERS for b in PASSES]
    if only:
        todo = [tuple(x.split(':')) for x in only.split(',')]
    total = 0.0
    for layer, light in todo:
        setup(layer, light)
        SL.data.energy = SCREEN_E
        FL.data.energy = FLAME_E
        total += render_to('%s_%s' % (layer, light), as_pass=(light == 'base'))
    meta = dict(LAYOUT, over=OVER, samples=SAMPLES, screen_e=SCREEN_E, flame_e=FLAME_E,
                screen_world=list(sw), flame_world=list(fw), cam=list(cam.location),
                principal_px=list(map(float, room.principal_px())), depths=room.LAYER_DEPTH)
    json.dump(meta, open(os.path.join(OUT, 'passes.json'), 'w'), indent=1)
    print('PASSES_TOTAL %.1f s' % total, flush=True)
elif MODE == 'full':
    # контроль линейности: вся комната одним рендером со светом момента t (линии Freestyle — в самом кадре)
    t = float(opt('--t', '1.3'))
    setup(None, 'full')
    SL.data.energy = SCREEN_E * timing.screen(t)
    FL.data.energy = FLAME_E * timing.flame(t)
    render_to('full', as_pass=False)
