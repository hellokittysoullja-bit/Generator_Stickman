# Потоковый рендер ролика в Blender (турбо-профиль): берёт fNNNN.glb из очереди по порядку, рендерит, удаляет .glb.
# blender -b --python blender_loop99.py -- <очередь> <кадры_выход> <N> [список кадров через запятую]
import bpy, sys, os, json, math, time
sys.path.insert(0, '/home/user/Generator_Stickman/scripts'); import blender_fast
argv = sys.argv[sys.argv.index('--') + 1:]; Q, OUT, N = argv[0], argv[1], int(argv[2]); FR = [int(x) for x in argv[3].split(',')] if len(argv) > 3 else range(N); os.makedirs(OUT, exist_ok=True)
def light(sc, kind, loc, rot, energy, color, size):
    d = bpy.data.lights.new(kind, kind); d.energy = energy; d.color = color
    if kind == 'AREA': d.size = size
    elif kind == 'SUN': d.angle = math.radians(size)
    o = bpy.data.objects.new(kind, d); sc.collection.objects.link(o); o.location = loc; o.rotation_euler = rot; return o
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
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (1.0, 0.86, 0.68, 1); bg.inputs[1].default_value = 0.15
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'Medium High Contrast'; sc.view_settings.exposure = -1.1
    for o in list(sc.objects):
        if o.type == 'LIGHT': bpy.data.objects.remove(o)
    light(sc, 'SUN', (-3.5, -1.2, 3.2), (math.radians(55), math.radians(-35), math.radians(-60)), 2.5, (1.0, 0.94, 0.85), 8)
    light(sc, 'AREA', (0, 0.3, 2.3), (0, 0, 0), 150, (1.0, 0.88, 0.7), 1.2)
    c = sc.camera; light(sc, 'AREA', c.location, c.rotation_euler, 24, (1.0, 0.95, 0.9), 0.8)
    light(sc, 'AREA', (1.8, 1.5, 2.4), (math.radians(-60), math.radians(30), 0), 120, (1.0, 0.95, 0.85), 1.0)
    if meta.get('flame'): light(sc, 'POINT', meta['flame'], (0, 0, 0), 6, (1.0, 0.6, 0.25), 0)
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    os.remove(g); os.remove(g[:-4] + '.json')
    print('FRAME', i, round(time.time() - t0, 1), flush=True)
