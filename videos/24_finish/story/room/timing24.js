// Точная копия timing24.py (рилс 24, сцена room). Браузер: window.Timing24; node: require('./timing24.js').
(function (root) {
  const FPS = 30, END = 37.30, GOT = 2.427, ZERO = 4.08, WHY = 8.24, EVENING = 24.0, JOY = 29.56, CELEB = 31.84;
  const frac = x => x - Math.floor(x);
  const hash01 = (i, s) => frac(Math.sin(i * 127.1 + s * 311.7) * 43758.5453123);
  function vnoise(t, hz, seed) { const x = t * hz, i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
    const a = hash01(i, seed), b = hash01(i + 1, seed); return a + (b - a) * u; }
  function smoothstep(e0, e1, x) { const u = Math.min(1, Math.max(0, (x - e0) / (e1 - e0))); return u * u * (3 - 2 * u); }
  function flash(t) { const dt = t - GOT; if (dt < 0 || dt > 0.49) return 0;
    return dt < 0.04 ? dt / 0.04 : Math.pow(1 - (dt - 0.04) / 0.45, 2); }
  function tv(t) { if (t >= EVENING) return 0; return (1 + 0.04 * (2 * vnoise(t, 5, 11) - 1)) * (1 + 1.2 * flash(t)); }
  function lamp(t) { if (t < EVENING) return 0; return 1.0 + 0.35 * smoothstep(JOY, JOY + 0.8, t); }
  function warm(t) { return t >= EVENING ? smoothstep(JOY, JOY + 0.8, t) : 0; }
  function flame(t) { const base = 0.85 + 0.30 * vnoise(t, 9, 7); const up = smoothstep(CELEB - 0.06, CELEB + 0.12, t);
    const calm = smoothstep(CELEB + 0.5, CELEB + 1.6, t); return base * (1 + up * (0.8 - 0.4 * calm)); }
  function hop(t, t0, dur, h) { if (t < t0 || t > t0 + dur) return 0; const u = (t - t0) / dur; return -4 * h * u * (1 - u); }
  function cat_jump(t) {
    const t1 = CELEB, d1 = 0.5, t2 = CELEB + 0.66, d2 = 0.3;
    const dy = hop(t, t1, d1, 170) + hop(t, t2, d2, 38);
    let sq = 0;
    sq += 0.10 * smoothstep(t1 - 0.2, t1 - 0.04, t) * (1 - smoothstep(t1 - 0.04, t1 + 0.04, t));
    sq -= 0.07 * smoothstep(t1, t1 + 0.06, t) * (1 - smoothstep(t1 + 0.16, t1 + 0.32, t));
    for (const [land, k] of [[t1 + d1, 0.11], [t2 + d2, 0.06]])
      if (land - 0.01 <= t && t <= land + 0.22) sq += k * Math.sin(Math.PI * (t - land + 0.01) / 0.23);
    return [dy, 1 + 0.6 * sq, 1 - sq];
  }
  const T = { FPS, END, GOT, ZERO, WHY, EVENING, JOY, CELEB, tv, flame, lamp, warm, flash, cat_jump, vnoise, smoothstep };
  if (typeof module !== 'undefined' && module.exports) { module.exports = T;
    if (require.main === module && process.argv.includes('--dump')) { const o = {};
      for (const n of ['tv', 'flame', 'lamp', 'warm', 'flash', 'cat_jump']) { o[n] = []; for (let f = 0; f <= Math.floor(END * FPS); f++) o[n].push(T[n](f / FPS)); }
      process.stdout.write(JSON.stringify(o)); } } else root.Timing24 = T;
})(typeof window !== 'undefined' ? window : this);
