# --- кэш чистых функций штриха (ускорение рендера, вывод байт в байт тот же) ---
def _memo(fn, size=50000):
    cache = {}

    def w(pts, *a, **k):
        try:
            P = np.asarray(pts, dtype=float)
            key = (P.shape, P.tobytes(), a, tuple(sorted(k.items())))
            hash(key)
        except (TypeError, ValueError):
            return fn(pts, *a, **k)
        r = cache.get(key)
        if r is None:
            if len(cache) > size:
                cache.clear()
            r = cache[key] = fn(pts, *a, **k)
        return r
    w.__wrapped__ = fn
    return w


ink_closed = _memo(ink_closed)
ink_open = _memo(ink_open)
fill_d = _memo(fill_d)
