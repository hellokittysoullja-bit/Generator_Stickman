# Потоковый рендер рилса 100 в Blender (турбо): fNNNN.glb из очереди по порядку; свет — по настроению плана из .json кадра
# (сцена three.js кладёт список ламп, фронт-свет у камеры, мир и экспозицию). .glb удаляется, .json уходит к кадру (искры в compose).
# blender -b --python blender_loop100.py -- <очередь> <кадры_выход> <N> [список кадров через запятую]
import bpy, sys, os, json, math, time, shutil
from mathutils import Vector
sys.path.insert(0, '/home/user/Generator_Stickman/scripts'); import blender_fast
argv = sys.argv[sys.argv.index('--') + 1:]; Q, OUT, N = argv[0], argv[1], int(argv[2]); FR = [int(x) for x in argv[3].split(',')] if len(argv) > 3 else range(N); os.makedirs(OUT, exist_ok=True)
B = lambda p: Vector((p[0], -p[2], p[1]))   # three.js → Blender
def light(sc, kind, loc, energy, color, size=0.5, aim=None, rot=None):
    d = bpy.data.lights.new(kind, kind); d.energy = energy; d.color = color
    if kind == 'AREA': d.size = size
    elif kind == 'SUN': d.angle = math.radians(size)
    elif kind == 'POINT': d.shadow_soft_size = 0.08
    o = bpy.data.objects.new(kind, d); sc.collection.objects.link(o); o.location = loc
    if aim is not None: o.rotation_euler = (aim - loc).to_track_quat('-Z', 'Y').to_euler()
    if rot is not None: o.rotation_euler = rot
    return o
for i in FR:
    g = f'{Q}/f{i:04d}.glb'; out = f'{OUT}/f{i:04d}.jpg'
    if os.path.exists(out):
        if os.path.exists(g): os.remove(g)
        continue
    while not os.path.exists(g): time.sleep(0.2)
    meta = json.load(open(g[:-4] + '.json'))
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=g)
    sc = bpy.context.scene
    cams = [o for o in sc.objects if o.type == 'CAMERA']; sc.camera = cams[-1]
    cam = sc.camera.data; cam.sensor_fit = 'VERTICAL'; cam.angle_y = math.radians(meta['fov'])
    blender_fast.apply_turbo(sc)
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']; wr = meta['world']; bg.inputs[0].default_value = (wr[0], wr[1], wr[2], 1); bg.inputs[1].default_value = wr[3]
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'Medium High Contrast'; sc.view_settings.exposure = meta['exp']
    for o in list(sc.objects):
        if o.type == 'LIGHT': bpy.data.objects.remove(o)
    for L in meta['lights']:
        light(sc, L['k'], B(L['p']), L['e'], L['c'], L.get('s', 0.5), B(L['a']) if L.get('a') else None)
    c = sc.camera; cf = meta['camf']
    light(sc, 'AREA', c.matrix_world.to_translation() + c.matrix_world.to_3x3() @ Vector((0.25, 0.3, 0.1)), cf['e'], cf['c'], cf['s'], rot=c.matrix_world.to_euler())
    if meta.get('flame'): light(sc, 'POINT', Vector(meta['flame']), 6, (1.0, 0.6, 0.25))
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    os.remove(g); shutil.move(g[:-4] + '.json', out[:-4] + '.json')
    print('FRAME', i, round(time.time() - t0, 1), flush=True)
