// Точная копия timing26.py (рилс 26, сцена room). Браузер: window.Timing26; node: require('./timing26.js').
(function (root) {
  const FPS = 30, PROMISE = 1.44, RUN = 2.56, WHY = 6.48;
  const frac = x => x - Math.floor(x);
  const hash01 = (i, s) => frac(Math.sin(i * 127.1 + s * 311.7) * 43758.5453123);
  function vnoise(t, hz, seed) { const x = t * hz, i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
    const a = hash01(i, seed), b = hash01(i + 1, seed); return a + (b - a) * u; }
  function smoothstep(e0, e1, x) { const u = Math.min(1, Math.max(0, (x - e0) / (e1 - e0))); return u * u * (3 - 2 * u); }
  function flame(t, shot) { return 0.85 + 0.30 * vnoise(t, 7, 7); }
  function lamp(t, shot) { return 1.0; }
  function tv(t, shot) { return 0.0; }
  const T = { FPS, PROMISE, RUN, WHY, flame, lamp, tv, vnoise, smoothstep, hash01 };
  if (typeof module !== 'undefined' && module.exports) { module.exports = T;
    if (require.main === module && process.argv.includes('--dump')) { const o = {};
      for (const s of ['s02', 's05', 's13', 's17']) { o[s] = {};
        for (const n of ['flame', 'lamp']) { o[s][n] = []; for (let f = 0; f <= 37 * FPS; f++) o[s][n].push(T[n](f / FPS, s)); } }
      process.stdout.write(JSON.stringify(o)); } } else root.Timing26 = T;
})(typeof window !== 'undefined' ? window : this);
