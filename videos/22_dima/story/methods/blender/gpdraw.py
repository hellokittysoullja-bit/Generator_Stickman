"""Перенос 2D-рисунка chars.py в Grease Pencil (Blender 4.2, GP v2).

Каждый пиксель (px, py) ложится на плоскость y = PLANE_Y перед диваном точно в свой пиксель кадра
(луч из камеры), поэтому 2D-слой и 3D-комната совпадают без подгонки. Толщина линий — в пикселях экрана.
Неподвижные слои — один кадр; анимированные — свой кадр на каждый кадр ролика.
"""
import bpy

import chars
import room

PLANE_Y = -1.02   # перед подушками и краем сиденья: рисунок не прячется за 3D


def _lin(c):
    def f(x):
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    return (f(c[0]), f(c[1]), f(c[2]), c[3])


class Mats:
    def __init__(self, gpd):
        self.gpd = gpd
        self.cache = {}

    def get(self, kind, rgba):
        key = (kind, tuple(round(v, 3) for v in rgba))
        if key in self.cache:
            return self.cache[key]
        m = bpy.data.materials.new('%s_%d' % (kind, len(self.cache)))
        bpy.data.materials.create_gpencil_data(m)
        g = m.grease_pencil
        col = _lin(rgba)
        if kind == 'fill':
            g.show_stroke = False
            g.show_fill = True
            g.fill_color = col
        else:
            g.show_stroke = True
            g.show_fill = False
            g.color = col
            g.mode = 'LINE'
            g.stroke_style = 'SOLID'
        self.gpd.materials.append(m)
        self.cache[key] = len(self.gpd.materials) - 1
        return self.cache[key]


class Projector:
    def __init__(self):
        self.cache = {}

    def __call__(self, p):
        key = (round(p[0], 1), round(p[1], 1))
        v = self.cache.get(key)
        if v is None:
            w = room.px_on_plane_y(key[0], key[1], PLANE_Y)
            v = (w.x, w.y, w.z)
            if len(self.cache) < 400000:
                self.cache[key] = v
        return v


def add_items(frame, items, mats, proj, scale):
    for it in items:
        s = frame.strokes.new()
        s.display_mode = '3DSPACE'
        s.material_index = mats.get(it['kind'], it['rgba'])
        pts = it['pts']
        n = len(pts)
        s.points.add(n)
        co = [v for p in pts for v in proj(p)]
        s.points.foreach_set('co', co)
        if it['kind'] == 'fill':
            s.use_cyclic = True
            s.line_width = 1
            s.points.foreach_set('pressure', [0.0] * n)
        else:
            s.use_cyclic = bool(it.get('closed'))
            s.line_width = max(1, int(round(it['w'] * 2 * scale)))
            s.points.foreach_set('pressure', [x * 0.5 for x in it['press']])
        s.points.foreach_set('strength', [1.0] * n)
        s.points.update()   # пересчёт треугольников заливки: без него вогнутая форма заливается веером
        s.start_cap_mode = 'ROUND'
        s.end_cap_mode = 'ROUND'


def build(mode, nframes, info):
    sc = bpy.context.scene
    scale = sc.render.resolution_percentage / 100.0
    gpd = bpy.data.grease_pencils.new('heroes')
    gpd.stroke_thickness_space = 'SCREENSPACE'
    gpd.stroke_depth_order = '2D'
    ob = bpy.data.objects.new('heroes', gpd)
    ob.use_grease_pencil_lights = False
    sc.collection.objects.link(ob)
    mats = Mats(gpd)
    proj = Projector()
    layers = {}
    for name in chars.LAYERS:
        L = gpd.layers.new(name)
        L.use_lights = False
        if name in chars.ADD_LAYERS:
            L.blend_mode = 'ADD'
        elif name in chars.MUL_LAYERS:
            L.blend_mode = 'MULTIPLY'
        layers[name] = L

    def by_layer(items):
        out = {n: [] for n in chars.LAYERS}
        for it in items:
            out[it['layer']].append(it)
        return out

    t0 = float(sc.frame_current - 1) / sc.render.fps
    if mode != 'anim':
        groups = by_layer(chars.draw(t0))
        for name, L in layers.items():
            add_items(L.frames.new(1), groups[name], mats, proj, scale)
        _lights(info, t0)
        return ob

    first = by_layer(chars.draw(0.0))
    for name, L in layers.items():
        if name not in chars.ANIM_LAYERS:
            add_items(L.frames.new(1), first[name], mats, proj, scale)
    for f in range(1, nframes + 1):
        t = (f - 1) / sc.render.fps
        groups = by_layer(chars.draw(t))
        for name in chars.ANIM_LAYERS:
            add_items(layers[name].frames.new(f), groups[name], mats, proj, scale)
        _lights(info, t, keyframe=f)
    return ob


def _lights(info, t, keyframe=None):
    """3D-свет экрана и огонька мигает вместе с 2D-светом."""
    k = chars.screen_flicker(t)
    sl = info['screen_light'].data
    sl.energy = 18 * k
    fl = info['flame_light'].data
    fl.energy = 9 * chars.flame_flicker(t)
    if keyframe is not None:
        sl.keyframe_insert('energy', frame=keyframe)
        fl.keyframe_insert('energy', frame=keyframe)
