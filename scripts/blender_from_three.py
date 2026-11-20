# Рендер кадра 3D-сцены three.js в Blender Cycles (20.11): сцена выгружается из браузера в .glb (exportGLB в scene98.js, exp98.mjs),
# свет ставится заново (свет three.js при переносе слабеет), быстрые настройки — blender_fast.
# blender -b --python scripts/blender_from_three.py -- scene.glb out.jpg CYCLES 16   (замер 20.11: 35 с на кадр 720×1280)
import bpy, sys, json, math, time
sys.path.insert(0, '/home/user/Generator_Stickman/scripts'); import blender_fast
argv = sys.argv[sys.argv.index('--') + 1:]; glb, out = argv[0], argv[1]; engine = argv[2] if len(argv) > 2 else 'CYCLES'; spp = int(argv[3]) if len(argv) > 3 else 48
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
sc = bpy.context.scene
cams = [o for o in sc.objects if o.type == 'CAMERA']; sc.camera = cams[-1]
cam = sc.camera.data; cam.sensor_fit = 'VERTICAL'; cam.angle_y = math.radians(32)
blender_fast.apply(sc, samples=spp)
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (1.0, 0.86, 0.68, 1); bg.inputs[1].default_value = 0.15
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'Medium High Contrast'; sc.view_settings.exposure = -1.1
for o in list(sc.objects):
    if o.type == 'LIGHT': bpy.data.objects.remove(o)
def light(kind, loc, rot, energy, color, size):
    d = bpy.data.lights.new(kind, kind); d.energy = energy; d.color = color
    if kind == 'AREA': d.size = size
    else: d.angle = math.radians(size) if kind == 'SUN' else 0; 
    o = bpy.data.objects.new(kind, d); sc.collection.objects.link(o); o.location = loc; o.rotation_euler = rot; return o
# ключ из окна (слева), мягкий: x три.js -> x, z три.js -> -y, y -> z
light('SUN', (-3.5, -1.2, 3.2), (math.radians(55), math.radians(-35), math.radians(-60)), 2.5, (1.0, 0.94, 0.85), 8)
light('AREA', (0, 0, 2.3), (0, 0, 0), 150, (1.0, 0.88, 0.7), 1.2)  # люстра
cam_o = sc.camera; fl = light('AREA', cam_o.location, cam_o.rotation_euler, 2, (1.0, 0.95, 0.9), 0.8)  # мягкий фронт от камеры
light('AREA', (1.8, 1.5, 2.4), (math.radians(-60), math.radians(30), 0), 120, (1.0, 0.95, 0.85), 1.0)  # контровой
sc.render.filepath = out
if engine == 'EEVEE':
    sc.render.engine = 'BLENDER_EEVEE_NEXT'; e = sc.eevee; e.taa_render_samples = spp; e.use_shadows = True; e.use_raytracing = True
    e.ray_tracing_method = 'SCREEN'; e.use_gtao = True
t0 = time.time(); bpy.ops.render.render(write_still=True); print('RENDER_SEC', round(time.time() - t0, 1))
