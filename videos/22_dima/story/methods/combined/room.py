"""3D-комната для сцены «Дима, 01:47» — Blender 4.2, всё из кода.

Стена с проёмом окна, небо с луной, дом напротив со светящимися окнами (процедурный шейдер), шторы,
полка с книгами и часами 01:47 (сегменты — кодом), диван с подушкой, пол из досок, коврик.
Свет: луна (солнце через окно), тусклое синее заполнение, экран телефона, огонёк кота.
Координаты: задняя стена y=0, пол z=0, камера смотрит вдоль +Y.
"""
import math
import random

import bpy
from mathutils import Vector

# ---------------------------------------------------------------- помощники

def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def nodes_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    return m, nt, out


class N:
    """Короткая запись графа узлов: N(nt).math('MULTIPLY', a, 2.0) и т.п."""

    def __init__(self, nt):
        self.nt = nt

    def node(self, kind, **props):
        n = self.nt.nodes.new(kind)
        for k, v in props.items():
            setattr(n, k, v)
        return n

    def inp(self, n, key, v):
        if v is None:
            return
        sock = n.inputs[key]
        if hasattr(v, 'is_output') or hasattr(v, 'links'):
            self.nt.links.new(v, sock)
        else:
            sock.default_value = v

    def math(self, op, a, b=None, clamp=False):
        n = self.node('ShaderNodeMath', operation=op, use_clamp=clamp)
        self.inp(n, 0, a)
        if b is not None:
            self.inp(n, 1, b)
        return n.outputs[0]

    def vmath(self, op, a, b=None):
        n = self.node('ShaderNodeVectorMath', operation=op)
        self.inp(n, 0, a)
        if b is not None:
            self.inp(n, 1, b)
        return n.outputs[0] if op not in ('DOT_PRODUCT', 'LENGTH', 'DISTANCE') else n.outputs[1]

    def mix(self, fac, a, b):
        n = self.node('ShaderNodeMix', data_type='RGBA')
        self.inp(n, 'Factor', fac)
        self.inp(n, 6, a)
        self.inp(n, 7, b)
        return n.outputs[2]

    def coord(self, kind='Object'):
        if kind == 'World':
            return self.node('ShaderNodeNewGeometry').outputs['Position']
        return self.node('ShaderNodeTexCoord').outputs[kind]

    def sep(self, v):
        n = self.node('ShaderNodeSeparateXYZ')
        self.inp(n, 0, v)
        return n.outputs

    def noise(self, v, scale, detail=2.0):
        n = self.node('ShaderNodeTexNoise')
        self.inp(n, 'Vector', v)
        n.inputs['Scale'].default_value = scale
        n.inputs['Detail'].default_value = detail
        return n.outputs['Fac']

    def white(self, v):
        n = self.node('ShaderNodeTexWhiteNoise', noise_dimensions='3D')
        self.inp(n, 'Vector', v)
        return n.outputs['Value']

    def bsdf(self, color, rough=0.85, emission=None, estr=0.0):
        n = self.node('ShaderNodeBsdfPrincipled')
        self.inp(n, 'Base Color', color)
        n.inputs['Roughness'].default_value = rough
        n.inputs['Specular IOR Level'].default_value = 0.25
        if emission is not None:
            self.inp(n, 'Emission Color', emission)
            self.inp(n, 'Emission Strength', estr)
        return n.outputs[0]

    def emit(self, color, strength):
        n = self.node('ShaderNodeEmission')
        self.inp(n, 'Color', color)
        self.inp(n, 'Strength', strength)
        return n.outputs[0]


def plain(name, color, rough=0.85, emit=None, estr=0.0):
    m, nt, out = nodes_mat(name)
    g = N(nt)
    nt.links.new(g.bsdf(color + (1,), rough, (emit + (1,)) if emit else None, estr), out.inputs[0])
    return m


def emission_mat(name, color, strength):
    m, nt, out = nodes_mat(name)
    g = N(nt)
    nt.links.new(g.emit(color + (1,), strength), out.inputs[0])
    return m


def box(name, x0, x1, y0, y1, z0, z1, mat, coll=None, bevel=0.0, seg=3):
    me = bpy.data.meshes.new(name)
    v = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    c = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    v = [(a - c[0], b - c[1], d - c[2]) for a, b, d in v]
    me.from_pydata(v, [], f)
    me.update()
    ob = link(bpy.data.objects.new(name, me), coll)
    ob.location = c
    ob.data.materials.append(mat)
    if bevel > 0:
        b = ob.modifiers.new('bevel', 'BEVEL')
        b.width = bevel
        b.segments = seg
        b.limit_method = 'NONE'
        for p in me.polygons:
            p.use_smooth = True
    return ob


def soft(ob, levels=2):
    s = ob.modifiers.new('sub', 'SUBSURF')
    s.levels = levels
    s.render_levels = levels
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


# ---------------------------------------------------------------- камера и пиксели

W, H = 1080, 1920


ZOOM = 1.15                 # кадр съёмочной камеры крупнее «чертёжной» (рисунок в пикселях чертёжной)
CROP_CENTER = (572, 1040)
SHELF_DX = 0.36             # полка с часами ближе к центру, чтобы 01:47 не срезалось кадром


# расстояние от камеры кадра 0 (y = -4.25) до слоя, м — по нему масштаб слоя при наезде (мультиплан)
LAYER_DEPTH = {'far': 4.25, 'sofa': 3.85, 'floor': 2.75, 'L_dima': 3.75, 'L_plaid': 3.33, 'L_cat': 3.42}
CAM_Y = -4.25


def principal_px():
    """Пиксель (1080×1920) оптической оси съёмочной камеры: центр масштаба при наезде вперёд."""
    cd = bpy.data.objects['cam'].data
    return (W / 2 - cd.shift_x * H, H / 2 + cd.shift_y * H)


def _cam(name, lens, sx, sy):
    cd = bpy.data.cameras.new(name)
    cd.sensor_fit = 'VERTICAL'
    cd.sensor_height = 24.0
    cd.lens = lens
    cd.shift_x = sx
    cd.shift_y = sy
    cd.clip_start = 0.05
    cd.clip_end = 80
    co = link(bpy.data.objects.new(name, cd))
    co.location = (0.0, -4.25, 1.45)
    co.rotation_euler = (math.radians(90), 0, 0)
    return co


def camera():
    """Две камеры с одной точкой: «чертёжная» (по ней пиксели рисунка) и съёмочная (крупнее, со сдвигом)."""
    sc = bpy.context.scene
    sc.render.resolution_x = W
    sc.render.resolution_y = H
    L1, sx1, sy1 = 24.0, 0.0, -0.10
    _cam('design', L1, sx1, sy1)
    cx, cy = CROP_CENTER
    k = ZOOM
    co = _cam('cam', L1 * k, k * ((cx - W / 2) / H + sx1), k * ((H / 2 - cy) / H + sy1))
    sc.camera = co
    bpy.context.view_layer.update()   # иначе matrix_world камер ещё единичная и лучи из пикселей идут мимо
    return co


def pixel_ray(px, py):
    """Луч чертёжной камеры через пиксель (px, py) кадра 1080×1920."""
    sc = bpy.context.scene
    co = bpy.data.objects['design']
    tr, br, bl, tl = co.data.view_frame(scene=sc)
    u, v = px / W, py / H
    local = tl + (tr - tl) * u + (bl - tl) * v
    d = co.matrix_world.to_3x3() @ local
    return co.matrix_world.translation.copy(), d.normalized()


def px_on_plane_y(px, py, y):
    """Точка мира на плоскости y=const, которая видна в пикселе (px, py)."""
    o, d = pixel_ray(px, py)
    t = (y - o.y) / d.y
    return o + d * t


def px_on_plane_z(px, py, z):
    o, d = pixel_ray(px, py)
    t = (z - o.z) / d.z
    return o + d * t


# ---------------------------------------------------------------- материалы комнаты

def wallpaper_mat():
    """Старые обои: полосы и веточки, но не по линейке — полотна со швами и сдвигом рисунка,
    дрожь полос, выцветание пятнами, подтёк у потолка, грязь внизу, фактура бумаги (рельеф)."""
    m, nt, out = nodes_mat('wallpaper')
    g = N(nt)
    p = g.coord('World')
    x, y, z = g.sep(p)
    wob = g.math('MULTIPLY', g.math('SUBTRACT', g.noise(p, 1.7, 3.0), 0.5), 0.022)
    xw = g.math('ADD', x, wob)
    # полотна по 0.53 м: шов и сдвиг рисунка по высоте у каждого полотна
    sheet = g.math('FLOOR', g.math('DIVIDE', x, 0.53))
    fs = g.math('FRACT', g.math('DIVIDE', x, 0.53))
    seam = g.math('LESS_THAN', g.math('MINIMUM', fs, g.math('SUBTRACT', 1.0, fs)), 0.006)
    zs = g.math('ADD', z, g.math('MULTIPLY', g.math('FRACT', g.math('MULTIPLY', sheet, 0.37)), 0.11))
    fx = g.math('FRACT', g.math('DIVIDE', xw, 0.16))
    stripe = g.math('MULTIPLY', g.math('GREATER_THAN', fx, 0.02), g.math('LESS_THAN', fx, 0.30))
    cx = g.math('DIVIDE', xw, 0.16)
    cz = g.math('DIVIDE', zs, 0.24)
    shift = g.math('MULTIPLY', g.math('FLOOR', cz), 0.5)
    ux = g.math('SUBTRACT', g.math('FRACT', g.math('ADD', cx, shift)), 0.66)
    uz = g.math('SUBTRACT', g.math('FRACT', cz), 0.5)
    d1 = g.math('ADD', g.math('ABSOLUTE', ux), g.math('ABSOLUTE', g.math('MULTIPLY', uz, 0.6)))
    motif = g.math('LESS_THAN', d1, 0.085)
    stem = g.math('MULTIPLY', g.math('LESS_THAN', g.math('ABSOLUTE', ux), 0.012),
                  g.math('LESS_THAN', g.math('ABSOLUTE', g.math('ADD', uz, 0.17)), 0.12))
    motif = g.math('MAXIMUM', motif, stem)
    # рисунок местами стёрт
    worn = g.math('GREATER_THAN', g.noise(g.vmath('MULTIPLY', p, (3.0, 3.0, 3.0)), 4.0, 5.0), 0.62)
    motif = g.math('MULTIPLY', motif, g.math('SUBTRACT', 1.0, g.math('MULTIPLY', worn, 0.7)))
    c = g.mix(g.math('MULTIPLY', stripe, 0.8), (0.36, 0.31, 0.36, 1), (0.30, 0.255, 0.30, 1))
    c = g.mix(g.math('MULTIPLY', motif, 0.85), c, (0.24, 0.19, 0.25, 1))
    c = g.mix(g.math('MULTIPLY', seam, 0.6), c, (0.17, 0.14, 0.17, 1))
    # подтёк под потолком и грязь у пола
    stain = g.math('MULTIPLY', g.math('GREATER_THAN', g.noise(g.vmath('MULTIPLY', p, (1.3, 1.3, 0.7)), 2.0, 6.0), 0.60),
                   g.math('GREATER_THAN', z, 2.35))
    c = g.mix(g.math('MULTIPLY', stain, 0.45), c, (0.33, 0.27, 0.17, 1))
    low = g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', z, 1.1), clamp=True), 0.35)
    c = g.mix(low, c, (0.12, 0.10, 0.11, 1))
    # пятнистое выцветание + зерно бумаги
    mott = g.math('ADD', 0.86, g.math('MULTIPLY', g.noise(p, 1.1, 6.0), 0.28))
    grain = g.math('ADD', 0.97, g.math('MULTIPLY', g.noise(p, 260.0, 2.0), 0.06))
    hs = g.node('ShaderNodeHueSaturation')
    g.inp(hs, 'Color', c)
    g.inp(hs, 'Value', g.math('MULTIPLY', mott, grain))
    bump = g.node('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.12
    g.inp(bump, 'Height', g.math('ADD', g.noise(p, 90.0, 3.0), g.math('MULTIPLY', seam, 0.6)))
    bs = g.node('ShaderNodeBsdfPrincipled')
    g.inp(bs, 'Base Color', hs.outputs[0])
    bs.inputs['Roughness'].default_value = 0.95
    bs.inputs['Specular IOR Level'].default_value = 0.15
    nt.links.new(bump.outputs[0], bs.inputs['Normal'])
    nt.links.new(bs.outputs[0], out.inputs[0])
    return m


def floor_mat():
    m, nt, out = nodes_mat('floor')
    g = N(nt)
    p = g.coord('World')
    mp = g.node('ShaderNodeMapping')
    g.inp(mp, 'Vector', p)
    mp.inputs['Scale'].default_value = (0.9, 6.0, 1.0)
    b = g.node('ShaderNodeTexBrick')
    g.inp(b, 'Vector', mp.outputs[0])
    b.inputs['Color1'].default_value = (0.20, 0.12, 0.075, 1)
    b.inputs['Color2'].default_value = (0.15, 0.09, 0.055, 1)
    b.inputs['Mortar'].default_value = (0.05, 0.03, 0.02, 1)
    b.inputs['Scale'].default_value = 1.0
    b.inputs['Mortar Size'].default_value = 0.012
    b.inputs['Brick Width'].default_value = 1.3
    b.inputs['Row Height'].default_value = 0.5
    grain = g.noise(g.vmath('MULTIPLY', p, (1.0, 18.0, 1.0)), 6.0, 3.0)
    c = g.mix(g.math('MULTIPLY', grain, 0.35), b.outputs['Color'], (0.09, 0.05, 0.03, 1))
    nt.links.new(g.bsdf(c, 0.55), out.inputs[0])
    return m


def rug_mat():
    """Коврик: бордовый с орнаментом — кольца, ромбы и кайма, всё из координат."""
    m, nt, out = nodes_mat('rug')
    g = N(nt)
    p = g.coord('Generated')
    x, y, z = g.sep(p)
    ux = g.math('ABSOLUTE', g.math('SUBTRACT', x, 0.5))
    uy = g.math('ABSOLUTE', g.math('SUBTRACT', y, 0.5))
    edge = g.math('MAXIMUM', ux, uy)
    border = g.math('MULTIPLY', g.math('GREATER_THAN', edge, 0.40), g.math('LESS_THAN', edge, 0.46))
    rhomb = g.math('ADD', g.math('MULTIPLY', ux, 1.0), g.math('MULTIPLY', uy, 1.7))
    medal = g.math('LESS_THAN', rhomb, 0.30)
    rings = g.math('MULTIPLY', g.math('LESS_THAN', g.math('FRACT', g.math('MULTIPLY', rhomb, 14.0)), 0.22), medal)
    # поле: мелкие ромбики по диагональной сетке
    dx = g.math('FRACT', g.math('MULTIPLY', g.math('ADD', x, y), 14.0))
    dy = g.math('FRACT', g.math('MULTIPLY', g.math('SUBTRACT', x, y), 14.0))
    dots = g.math('LESS_THAN', g.math('ADD', g.math('ABSOLUTE', g.math('SUBTRACT', dx, 0.5)),
                                      g.math('ABSOLUTE', g.math('SUBTRACT', dy, 0.5))), 0.16)
    field = g.math('MULTIPLY', dots, g.math('LESS_THAN', edge, 0.38))
    inner_b = g.math('MULTIPLY', g.math('GREATER_THAN', edge, 0.38), g.math('LESS_THAN', edge, 0.40))
    bdots = g.math('MULTIPLY', g.math('LESS_THAN', g.math('FRACT', g.math('MULTIPLY', g.math('ADD', x, y), 30.0)), 0.35), border)
    fringe = g.math('GREATER_THAN', edge, 0.485)
    c = g.mix(field, (0.20, 0.035, 0.045, 1), (0.30, 0.10, 0.07, 1))
    c = g.mix(medal, c, (0.14, 0.03, 0.05, 1))
    c = g.mix(rings, c, (0.42, 0.26, 0.13, 1))
    c = g.mix(border, c, (0.05, 0.06, 0.14, 1))
    c = g.mix(bdots, c, (0.36, 0.24, 0.14, 1))
    c = g.mix(inner_b, c, (0.40, 0.28, 0.16, 1))
    c = g.mix(fringe, c, (0.45, 0.42, 0.36, 1))
    fuzz = g.math('MULTIPLY', g.noise(p, 60.0, 2.0), 0.25)
    hs = g.node('ShaderNodeHueSaturation')
    g.inp(hs, 'Color', c)
    g.inp(hs, 'Value', g.math('ADD', fuzz, 0.88))
    nt.links.new(g.bsdf(hs.outputs[0], 1.0), out.inputs[0])
    return m


def fabric_mat(name, c1, c2, scale=40.0):
    m, nt, out = nodes_mat(name)
    g = N(nt)
    p = g.coord('Object')
    n = g.noise(p, scale, 6.0)
    c = g.mix(n, c1 + (1,), c2 + (1,))
    sh = g.node('ShaderNodeBsdfSheen') if 'ShaderNodeBsdfSheen' in dir(bpy.types) else None
    bs = g.bsdf(c, 0.95)
    if sh is not None:
        pass
    nt.links.new(bs, out.inputs[0])
    return m


def curtain_mat():
    """Плотная штора: продольное плетение, выгоревшие полосы, неровный тон."""
    m, nt, out = nodes_mat('curtain')
    g = N(nt)
    p = g.coord('World')
    weave = g.noise(g.vmath('MULTIPLY', p, (60.0, 60.0, 4.0)), 3.0, 2.0)
    fade = g.noise(g.vmath('MULTIPLY', p, (3.0, 3.0, 0.4)), 2.0, 3.0)
    c = g.mix(fade, (0.44, 0.39, 0.33, 1), (0.30, 0.27, 0.25, 1))
    c = g.mix(g.math('MULTIPLY', weave, 0.4), c, (0.24, 0.21, 0.19, 1))
    bs = g.node('ShaderNodeBsdfPrincipled')
    g.inp(bs, 'Base Color', c)
    bs.inputs['Roughness'].default_value = 1.0
    bs.inputs['Specular IOR Level'].default_value = 0.05
    bs.inputs['Subsurface Weight'].default_value = 0.0
    nt.links.new(bs.outputs[0], out.inputs[0])
    return m


def pillow_mat():
    """Наволочка в мелкий розовый цветочек, как у образца."""
    m, nt, out = nodes_mat('pillow')
    g = N(nt)
    p = g.coord('Object')
    v = g.node('ShaderNodeTexVoronoi')
    g.inp(v, 'Vector', p)
    v.inputs['Scale'].default_value = 14.0
    dots = g.math('LESS_THAN', v.outputs['Distance'], 0.18)
    c = g.mix(dots, (0.62, 0.58, 0.62, 1), (0.62, 0.33, 0.40, 1))
    nt.links.new(g.bsdf(c, 0.95), out.inputs[0])
    return m


def sky_mat(moon_dir):
    """Небо как написанное: глубокий градиент, рваные облака мазками, засветка города у горизонта,
    звёзды разной величины."""
    m, nt, out = nodes_mat('sky')
    g = N(nt)
    p = g.coord('Object')
    x, y, z = g.sep(p)
    t = g.math('MULTIPLY', g.math('ADD', z, 2.0), 0.055, clamp=True)
    c = g.mix(t, (0.07, 0.10, 0.24, 1), (0.010, 0.016, 0.06, 1))
    glow = g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ADD', z, 6.0), 0.11), clamp=True), 0.8)
    c = g.mix(glow, c, (0.16, 0.10, 0.12, 1))
    pc = g.vmath('MULTIPLY', p, (0.045, 0.045, 0.16))
    cl = g.noise(pc, 2.2, 8.0)
    cloud = g.node('ShaderNodeMapRange')
    g.inp(cloud, 'Value', cl)
    cloud.inputs['From Min'].default_value = 0.50
    cloud.inputs['From Max'].default_value = 0.66
    c = g.mix(g.math('MULTIPLY', cloud.outputs[0], 0.75), c, (0.035, 0.045, 0.10, 1))
    edge = g.math('MULTIPLY', g.math('MULTIPLY', cloud.outputs[0], g.math('SUBTRACT', 1.0, cloud.outputs[0])), 1.6)
    c = g.mix(edge, c, (0.16, 0.19, 0.32, 1))
    v = g.node('ShaderNodeTexVoronoi')
    g.inp(v, 'Vector', p)
    v.inputs['Scale'].default_value = 1.6
    rnd = g.white(v.outputs['Position'])
    rad = g.math('ADD', 0.012, g.math('MULTIPLY', g.math('POWER', rnd, 6.0), 0.05))
    star = g.math('LESS_THAN', v.outputs['Distance'], rad)
    star = g.math('MULTIPLY', star, g.math('GREATER_THAN', rnd, 0.45))
    star = g.math('MULTIPLY', star, g.math('SUBTRACT', 1.0, cloud.outputs[0]))
    c = g.mix(g.math('MULTIPLY', star, 0.9), c, (0.95, 0.93, 1.0, 1))
    nt.links.new(g.emit(c, 1.0), out.inputs[0])
    return m


def moon_mat():
    """Луна с морями (пятна шума), чуть тёплая."""
    m, nt, out = nodes_mat('moon')
    g = N(nt)
    p = g.coord('Object')
    mar = g.math('GREATER_THAN', g.noise(p, 2.2, 4.0), 0.56)
    c = g.mix(g.math('MULTIPLY', mar, 0.55), (1.0, 0.96, 0.84, 1), (0.62, 0.62, 0.66, 1))
    nt.links.new(g.emit(c, 6.0), out.inputs[0])
    return m


def facade_mat(name, base, seed, lit_share=0.35, cols=1.15, rows=1.0):
    """Дом напротив: панели с неровной фактурой; окна разного тепла и яркости, со шторами и переплётом,
    часть — голубым светом телевизора, остальные тёмные с бликом неба."""
    m, nt, out = nodes_mat(name)
    g = N(nt)
    p = g.coord('Object')
    x, y, z = g.sep(p)
    gx = g.math('DIVIDE', x, cols)
    gz = g.math('DIVIDE', z, rows)
    fx = g.math('FRACT', gx)
    fz = g.math('FRACT', gz)
    cell = g.node('ShaderNodeCombineXYZ')
    g.inp(cell, 0, g.math('FLOOR', gx))
    g.inp(cell, 1, g.math('FLOOR', gz))
    g.inp(cell, 2, float(seed))
    r = g.white(cell.outputs[0])
    cell2 = g.node('ShaderNodeCombineXYZ')
    g.inp(cell2, 0, g.math('FLOOR', gx))
    g.inp(cell2, 1, g.math('FLOOR', gz))
    g.inp(cell2, 2, float(seed) + 17.0)
    r2 = g.white(cell2.outputs[0])
    win = g.math('MULTIPLY',
                 g.math('MULTIPLY', g.math('GREATER_THAN', fx, 0.27), g.math('LESS_THAN', fx, 0.73)),
                 g.math('MULTIPLY', g.math('GREATER_THAN', fz, 0.24), g.math('LESS_THAN', fz, 0.78)))
    # переплёт: крест тёмной рамы
    mull = g.math('MAXIMUM', g.math('LESS_THAN', g.math('ABSOLUTE', g.math('SUBTRACT', fx, 0.5)), 0.018),
                  g.math('LESS_THAN', g.math('ABSOLUTE', g.math('SUBTRACT', fz, 0.60)), 0.018))
    lit = g.math('LESS_THAN', r, lit_share)
    tv = g.math('LESS_THAN', r, lit_share * 0.22)
    # штора: тёмные края и складки поперёк окна, у каждого окна своя
    curt = g.math('ADD', 0.45, g.math('MULTIPLY', g.noise(g.vmath('MULTIPLY', p, (2.0, 2.0, 0.3)), 3.0, 2.0), 0.9))
    warmc = g.mix(r2, (1.0, 0.55, 0.20, 1), (1.0, 0.78, 0.45, 1))
    col_lit = g.mix(tv, warmc, (0.40, 0.62, 1.0, 1))
    em = g.math('MULTIPLY', g.math('MULTIPLY', win, lit), g.math('MULTIPLY', curt, g.math('SUBTRACT', 1.0, mull)))
    em = g.math('MULTIPLY', em, g.math('ADD', 1.2, g.math('MULTIPLY', r2, 1.6)))
    panel = g.math('ADD', g.math('MULTIPLY', g.noise(p, 1.4, 5.0), 0.7), g.math('MULTIPLY', g.noise(p, 14.0, 2.0), 0.3))
    wall = g.mix(panel, base + (1,), tuple(c * 0.45 for c in base) + (1,))
    glass = g.mix(g.math('MULTIPLY', fz, 0.8), (0.05, 0.07, 0.13, 1), (0.015, 0.02, 0.04, 1))
    col = g.mix(win, wall, glass)
    bs = g.node('ShaderNodeBsdfPrincipled')
    g.inp(bs, 'Base Color', col)
    bs.inputs['Roughness'].default_value = 0.9
    g.inp(bs, 'Emission Color', col_lit)
    g.inp(bs, 'Emission Strength', em)
    nt.links.new(bs.outputs[0], out.inputs[0])
    return m


def old_paint_mat(name, base):
    """Старая краска на дереве: не пластик — грязно-серая, местами потёрта, тёмная грязь в швах."""
    m, nt, out = nodes_mat(name)
    g = N(nt)
    p = g.coord('World')
    wear = g.math('GREATER_THAN', g.noise(p, 9.0, 6.0), 0.63)
    grime = g.noise(p, 3.0, 4.0)
    c = g.mix(g.math('MULTIPLY', grime, 0.5), base + (1,), tuple(v * 0.7 for v in base) + (1,))
    c = g.mix(g.math('MULTIPLY', wear, 0.7), c, (0.22, 0.16, 0.11, 1))
    bump = g.node('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.25
    g.inp(bump, 'Height', g.noise(p, 40.0, 4.0))
    bs = g.node('ShaderNodeBsdfPrincipled')
    g.inp(bs, 'Base Color', c)
    bs.inputs['Roughness'].default_value = 0.75
    bs.inputs['Specular IOR Level'].default_value = 0.2
    nt.links.new(bump.outputs[0], bs.inputs['Normal'])
    nt.links.new(bs.outputs[0], out.inputs[0])
    return m


def glass_mat():
    """Мутное стекло: едва заметная голубая плёнка с разводами (не прячет улицу)."""
    m, nt, out = nodes_mat('glass')
    g = N(nt)
    p = g.coord('World')
    smudge = g.math('ADD', 0.02, g.math('MULTIPLY', g.math('GREATER_THAN', g.noise(p, 5.0, 6.0), 0.58), 0.04))
    bs = g.node('ShaderNodeBsdfPrincipled')
    bs.inputs['Base Color'].default_value = (0.55, 0.62, 0.75, 1)
    bs.inputs['Roughness'].default_value = 0.25
    g.inp(bs, 'Alpha', smudge)
    nt.links.new(bs.outputs[0], out.inputs[0])
    m.surface_render_method = 'BLENDED'
    return m


# ---------------------------------------------------------------- сегментные часы

SEG = {  # a b c d e f g
    '0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd',
    '6': 'afgedc', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg'}


def seven_seg(text, x0, z0, y, h, mat, coll):
    """Цифры часов — прямоугольные сегменты; возвращает правый край."""
    w = h * 0.52
    t = h * 0.12
    x = x0
    for ch in text:
        if ch == ':':
            for dz in (0.3, 0.7):
                box('colon', x + t * 0.2, x + t * 1.2, y - 0.002, y, z0 + h * dz - t / 2, z0 + h * dz + t / 2, mat, coll)
            x += t * 2.2
            continue
        segs = SEG[ch]
        rect = {
            'a': (x + t, x + w - t, z0 + h - t, z0 + h),
            'g': (x + t, x + w - t, z0 + h / 2 - t / 2, z0 + h / 2 + t / 2),
            'd': (x + t, x + w - t, z0, z0 + t),
            'f': (x, x + t, z0 + h / 2 + t / 2, z0 + h - t),
            'b': (x + w - t, x + w, z0 + h / 2 + t / 2, z0 + h - t),
            'e': (x, x + t, z0 + t, z0 + h / 2 - t / 2),
            'c': (x + w - t, x + w, z0 + t, z0 + h / 2 - t / 2)}
        for s in segs:
            a, b, c, d = rect[s]
            box('seg', a + 0.001, b - 0.001, y - 0.002, y, c + 0.001, d - 0.001, mat, coll)
        x += w + t * 1.0
    return x


# ---------------------------------------------------------------- сборка комнаты

def build(screen_world=(0.1, -0.6, 1.1), flame_world=(0.9, -0.7, 0.6), moon_px=(930, 330)):
    random.seed(7)
    sc = bpy.context.scene
    far = collection('far')          # дальний план: стены, окно, шторы, полка
    outside = collection('outside')  # за окном (без линий Freestyle)
    floorc = collection('floor')     # пол, коврик, банки, тапки
    sofac = collection('sofa')       # диван и подушка
    room = far

    wallm = wallpaper_mat()
    white = old_paint_mat('frame_paint', (0.40, 0.39, 0.37))
    wood = plain('wood', (0.16, 0.09, 0.05), 0.6)
    dark = plain('dark', (0.02, 0.02, 0.025), 0.4)

    # --- стены, пол, потолок (закрыто, чтобы луна шла только через окно)
    WX0, WX1, WZ0, WZ1 = 0.34, 1.30, 1.28, 2.50       # проём окна
    T = 0.16
    box('wall_l', -3.0, WX0, 0, T, 0, 3.0, wallm, room)
    box('wall_r', WX1, 3.0, 0, T, 0, 3.0, wallm, room)
    box('wall_b', WX0, WX1, 0, T, 0, WZ0, wallm, room)
    box('wall_t', WX0, WX1, 0, T, WZ1, 3.0, wallm, room)
    box('side_l', -3.1, -3.0, -6, T, 0, 3.0, wallm, room)
    box('side_r', 3.0, 3.1, -6, T, 0, 3.0, wallm, room)
    box('ceil', -3.1, 3.1, -6, T, 3.0, 3.1, plain('ceil', (0.3, 0.3, 0.33)), room)
    box('floor', -3.0, 3.0, -6, 0, -0.05, 0, floor_mat(), floorc)
    box('plinth', -3.0, 3.0, -0.02, 0, 0, 0.07, plain('plinth', (0.25, 0.2, 0.17), 0.6), room)

    # --- окно: рама, импост, подоконник
    fw = 0.045
    box('fr_l', WX0, WX0 + fw, 0.05, 0.11, WZ0, WZ1, white, room)
    box('fr_r', WX1 - fw, WX1, 0.05, 0.11, WZ0, WZ1, white, room)
    box('fr_t', WX0, WX1, 0.05, 0.11, WZ1 - fw, WZ1, white, room)
    box('fr_b', WX0, WX1, 0.05, 0.11, WZ0, WZ0 + fw, white, room)
    mid = (WX0 + WX1) / 2
    box('fr_m', mid - fw / 2, mid + fw / 2, 0.05, 0.11, WZ0, WZ1, white, room)
    box('fr_h', WX0, WX1, 0.05, 0.11, 2.12, 2.12 + fw, white, room)
    gl_ = box('glass', WX0, WX1, 0.075, 0.08, WZ0, WZ1, glass_mat(), room)
    gl_.visible_shadow = False   # стекло не заслоняет лунный луч
    box('sill', WX0 - 0.08, WX1 + 0.08, -0.20, 0.12, WZ0 - 0.04, WZ0, white, room, bevel=0.01)
    # горшок с кактусом на подоконнике
    pot = box('pot', 0.50, 0.62, -0.13, -0.03, WZ0, WZ0 + 0.10, plain('pot', (0.35, 0.13, 0.08)), room, bevel=0.01)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=(0.56, -0.08, WZ0 + 0.17))
    cact = bpy.context.object
    cact.scale = (1, 1, 1.5)
    cact.data.materials.append(plain('cactus', (0.08, 0.22, 0.12)))
    for p in cact.data.polygons:
        p.use_smooth = True
    for c in cact.users_collection:
        c.objects.unlink(cact)
    room.objects.link(cact)

    # --- карниз и шторы (складки — синус по x)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=1.6, location=(0.82, -0.08, 2.66), rotation=(0, math.radians(90), 0))
    rod = bpy.context.object
    rod.data.materials.append(dark)
    for c in rod.users_collection:
        c.objects.unlink(rod)
    room.objects.link(rod)
    curtain_m = curtain_mat()
    for (xa, xb, folds, ph) in ((0.10, 0.44, 6, 0.0), (1.20, 1.60, 6, 1.3)):
        me = bpy.data.meshes.new('curtain')
        nx, nz = 60, 30
        verts, faces = [], []
        for j in range(nz + 1):
            z = 2.66 - (2.66 - 0.95) * j / nz
            v = j / nz
            spread = 1.0 + 0.35 * v
            for i in range(nx + 1):
                u = i / nx
                # складки не по линейке: частота плывёт, у карниза собрано, внизу расходится
                ph2 = ph + 0.9 * math.sin(u * 3.1 + v * 2.0) + 0.4 * math.sin(v * 5.0 + u * 7.0)
                x = xa + (xb - xa) * u + 0.03 * v * (u - 0.5)
                amp = 0.020 + 0.010 * math.sin(u * 2.3 + ph)
                yy = -0.10 - (amp * math.sin(u * folds * 2 * math.pi + ph2) + 0.010 * math.sin(u * folds * 4.7 + ph * 2.1)) * spread
                zz = z + (0.03 * math.sin(u * 9.0 + ph) if j == nz else 0.0)
                verts.append((x, yy, zz))
        for j in range(nz):
            for i in range(nx):
                a = j * (nx + 1) + i
                faces.append((a, a + 1, a + nx + 2, a + nx + 1))
        me.from_pydata(verts, [], faces)
        me.update()
        ob = link(bpy.data.objects.new('curtain', me), room)
        ob.data.materials.append(curtain_m)
        for p in me.polygons:
            p.use_smooth = True
        sol = ob.modifiers.new('sol', 'SOLIDIFY')
        sol.thickness = 0.006

    # --- за окном: небо, луна, дом напротив
    sky = box('sky', -40, 40, 40, 40.5, -10, 40, sky_mat(None), outside)
    sky.visible_shadow = False
    mo, md = pixel_ray(moon_px[0], moon_px[1])
    ml = mo + md * (38.0 / md.y)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=ml)
    moon = bpy.context.object
    moon.data.materials.append(moon_mat())
    for c in moon.users_collection:
        c.objects.unlink(moon)
    outside.objects.link(moon)
    moon.visible_shadow = False
    fac1 = box('house1', -6, 7.2, 14, 22, -6, 3.6, facade_mat('facade1', (0.07, 0.075, 0.11), 3, 0.32), outside)
    fac2 = box('house2', 6.0, 20, 24, 30, -6, 6.5, facade_mat('facade2', (0.05, 0.055, 0.09), 9, 0.22, 1.3, 1.1), outside)
    for o in (fac1, fac2):
        o.visible_shadow = False
    # крыша-силуэт и антенна
    box('roof1', -6, 7.2, 14, 22, 3.6, 3.85, plain('roof', (0.01, 0.012, 0.02)), outside)
    box('ant', 2.0, 2.06, 17, 17.06, 3.85, 5.2, plain('ant', (0.01, 0.01, 0.02)), outside)

    # --- полка с книгами, растением и часами (своя коллекция, сдвигается целиком)
    shelfc = collection('shelf')
    SY0 = -0.24
    box('shelf', -1.20, -0.30, SY0, 0, 2.02, 2.05, wood, shelfc, bevel=0.004)
    box('shelf2', -1.20, -0.55, SY0, 0, 1.62, 1.65, wood, shelfc, bevel=0.004)
    cols = [(0.10, 0.16, 0.30), (0.35, 0.08, 0.07), (0.45, 0.38, 0.18), (0.12, 0.25, 0.18), (0.25, 0.12, 0.30),
            (0.40, 0.40, 0.42), (0.08, 0.10, 0.16)]
    x = -1.18
    for i in range(9):
        w = random.uniform(0.028, 0.05)
        h = random.uniform(0.17, 0.25)
        c = cols[i % len(cols)]
        b = box('book', x, x + w, SY0 + 0.03, -0.02, 2.05, 2.05 + h, plain('book%d' % i, c, 0.7), shelfc, bevel=0.003)
        if i == 8:
            b.rotation_euler = (0, math.radians(-18), 0)
            b.location.x += 0.03
        x += w + 0.004
    # лежащая стопка
    for k in range(3):
        box('flat', -0.70, -0.46 - k * 0.015, SY0 + 0.04, -0.03, 2.05 + k * 0.035, 2.085 + k * 0.035,
            plain('flat%d' % k, cols[(k + 3) % 7], 0.7), shelfc, bevel=0.003)
    # кружка
    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.09, location=(-0.40, -0.12, 2.095))
    mug = bpy.context.object
    mug.data.materials.append(plain('mug', (0.45, 0.47, 0.50), 0.4))
    for c in mug.users_collection:
        c.objects.unlink(mug)
    shelfc.objects.link(mug)
    # нижняя полка: часы и растение
    ck = box('clock', -1.08, -0.80, -0.16, -0.06, 1.65, 1.77, plain('clockbody', (0.015, 0.015, 0.02), 0.3), shelfc, bevel=0.012)
    red = emission_mat('digits', (1.0, 0.12, 0.06), 9.0)
    seven_seg('01:47', -1.055, 1.675, -0.161, 0.07, red, shelfc)
    pot2 = box('pot2', -0.72, -0.60, -0.18, -0.06, 1.65, 1.76, plain('pot2', (0.55, 0.45, 0.38)), shelfc, bevel=0.01)
    leafm = plain('leaf', (0.06, 0.20, 0.10), 0.6)
    for k in range(9):
        a = -1.2 + k * 0.3
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04, location=(-0.66 + 0.10 * math.sin(a), -0.12, 1.80 + 0.06 * math.cos(a * 1.3) - k * 0.03))
        lf = bpy.context.object
        lf.scale = (1.6, 0.6, 0.7)
        lf.rotation_euler = (0, a, 0)
        lf.data.materials.append(leafm)
        for c in lf.users_collection:
            c.objects.unlink(lf)
        shelfc.objects.link(lf)
    # свисающая плеть
    for k in range(7):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.028, location=(-0.58 + 0.02 * math.sin(k), -0.08, 1.64 - k * 0.075))
        lf = bpy.context.object
        lf.scale = (1.5, 0.5, 0.8)
        lf.rotation_euler = (0, 0.8 * (-1) ** k, 0)
        lf.data.materials.append(leafm)
        for c in lf.users_collection:
            c.objects.unlink(lf)
        shelfc.objects.link(lf)

    for o in shelfc.objects:
        o.location.x += SHELF_DX
    # --- диван у стены
    sofa_m = fabric_mat('sofa', (0.22, 0.095, 0.085), (0.13, 0.055, 0.06), 90.0)
    SX0, SX1 = -1.30, 1.30
    box('sofa_base', SX0, SX1, -0.92, -0.02, 0.10, 0.30, sofa_m, sofac, bevel=0.03)
    box('sofa_seat1', SX0 + 0.20, 0.0, -0.92, -0.20, 0.30, 0.46, sofa_m, sofac, bevel=0.05, seg=4)
    box('sofa_seat2', 0.0, SX1 - 0.20, -0.92, -0.20, 0.30, 0.46, sofa_m, sofac, bevel=0.05, seg=4)
    box('sofa_back', SX0 + 0.10, SX1 - 0.10, -0.16, -0.02, 0.30, 0.98, sofa_m, sofac, bevel=0.06, seg=4)
    # спинка — две продавленные подушки
    for (a, b, tilt) in ((SX0 + 0.22, -0.01, 4), (0.01, SX1 - 0.22, -3)):
        bc = box('back_cushion', a, b, -0.34, -0.12, 0.42, 0.92, sofa_m, sofac, bevel=0.08, seg=5)
        bc.rotation_euler = (math.radians(-8), 0, math.radians(tilt * 0.3))
    box('arm_l', SX0, SX0 + 0.22, -0.95, -0.02, 0.10, 0.70, sofa_m, sofac, bevel=0.07, seg=4)
    box('arm_r', SX1 - 0.22, SX1, -0.95, -0.02, 0.10, 0.70, sofa_m, sofac, bevel=0.07, seg=4)
    for xx in (SX0 + 0.06, SX1 - 0.10):
        box('leg', xx, xx + 0.05, -0.88, -0.83, 0.0, 0.10, wood, sofac)
    # подушка у левого подлокотника
    pil = box('pillow', -1.10, -0.62, -0.36, -0.16, 0.42, 0.86, pillow_mat(), sofac, bevel=0.08, seg=6)
    sm = pil.modifiers.new('round', 'SUBSURF')
    sm.levels = sm.render_levels = 1
    pil.rotation_euler = (math.radians(-12), math.radians(-14), 0)

    # --- банки энергетика у дивана (кто-то не спит не первую ночь)
    canm = [plain('can1', (0.05, 0.25, 0.30), 0.3), plain('can2', (0.35, 0.33, 0.36), 0.3)]
    for k, (x, y, ang) in enumerate(((0.62, -1.22, 0), (0.80, -1.30, 75))):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.033, depth=0.12, location=(x, y, 0.06 if ang == 0 else 0.033),
                                            rotation=(math.radians(ang), 0, math.radians(30)))
        can = bpy.context.object
        can.data.materials.append(canm[k])
        for c in can.users_collection:
            c.objects.unlink(can)
        floorc.objects.link(can)

    # --- коврик на полу
    rug = box('rug', -0.75, 0.95, -2.25, -1.05, 0.0, 0.006, rug_mat(), floorc)

    # --- тапки на коврике: подошва + мягкий верх
    solem = plain('sole', (0.04, 0.04, 0.06), 0.8)
    fleece = fabric_mat('fleece', (0.30, 0.33, 0.42), (0.22, 0.24, 0.32), 140.0)
    for (x, y, rz) in ((-0.30, -1.40, 18), (-0.06, -1.48, -8)):
        so_ = box('slipper_sole', x - 0.055, x + 0.055, y - 0.13, y + 0.13, 0.0, 0.025, solem, floorc, bevel=0.03, seg=4)
        so_.rotation_euler = (0, 0, math.radians(rz))
        up = box('slipper_top', x - 0.06, x + 0.06, y - 0.14, y + 0.02, 0.02, 0.075, fleece, floorc, bevel=0.035, seg=5)
        up.rotation_euler = (0, 0, math.radians(rz))
        a_ = math.radians(rz)
        up.location = (x + 0.06 * math.sin(a_), y - 0.06 * math.cos(a_), up.location.z)
        sm1 = so_.modifiers.new('round', 'SUBSURF')
        sm1.levels = sm1.render_levels = 1
        sm2 = up.modifiers.new('round', 'SUBSURF')
        sm2.levels = sm2.render_levels = 1

    # --- свет
    world = bpy.data.worlds.new('night')
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs[0].default_value = (0.010, 0.013, 0.030, 1)
    bg.inputs[1].default_value = 1.0
    sc.world = world

    sun = bpy.data.lights.new('moonlight', 'SUN')
    sun.color = (0.55, 0.68, 1.0)
    sun.energy = 3.2
    sun.angle = math.radians(1.5)
    so = link(bpy.data.objects.new('moonlight', sun), room)
    so.rotation_euler = (math.radians(-38), math.radians(-28), math.radians(0))
    # направление: луч идёт из окна (+y, сверху, справа) в комнату
    so.rotation_euler = Vector((0.0, 0.0, 0.0)).to_track_quat('Z', 'Y').to_euler()
    dirv = Vector((-0.35, -1.0, -0.75)).normalized()   # пятно окна ложится на пол перед диваном
    so.rotation_euler = (-dirv).to_track_quat('Z', 'Y').to_euler()

    fill = bpy.data.lights.new('fill', 'AREA')
    fill.color = (0.35, 0.45, 0.85)
    fill.energy = 55
    fill.size = 3.0
    fo = link(bpy.data.objects.new('fill', fill), room)
    fo.location = (0.0, -2.6, 2.95)

    win_glow = bpy.data.lights.new('window_glow', 'AREA')
    win_glow.color = (0.45, 0.58, 1.0)
    win_glow.energy = 30
    win_glow.shape = 'RECTANGLE'
    win_glow.size = WX1 - WX0
    win_glow.size_y = WZ1 - WZ0
    wo = link(bpy.data.objects.new('window_glow', win_glow), room)
    wo.location = ((WX0 + WX1) / 2, 0.12, (WZ0 + WZ1) / 2)
    wo.rotation_euler = (math.radians(-90), 0, 0)
    win_glow.use_shadow = False

    # экран телефона и огонёк кота: точки в мире задаёт сборщик (по раскладке слоёв героев)
    phone = bpy.data.lights.new('screen', 'POINT')
    phone.color = (0.55, 0.78, 1.0)
    phone.energy = 18
    phone.shadow_soft_size = 0.08
    po = link(bpy.data.objects.new('screen', phone), far)
    po.location = screen_world

    fl = bpy.data.lights.new('flame', 'POINT')
    fl.color = (1.0, 0.45, 0.12)
    fl.energy = 9
    fl.shadow_soft_size = 0.05
    flo = link(bpy.data.objects.new('flame', fl), far)
    flo.location = flame_world
    for o in (so, fo, wo):
        for c in o.users_collection:
            c.objects.unlink(o)
        far.objects.link(o)
    return {'far': far, 'outside': outside, 'floor': floorc, 'sofa': sofac, 'shelf': shelfc,
            'screen_light': po, 'flame_light': flo, 'lights': {'moon': so, 'fill': fo, 'window': wo}}
