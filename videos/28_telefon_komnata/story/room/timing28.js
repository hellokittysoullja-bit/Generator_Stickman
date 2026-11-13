// Точная копия timing28.py (рилс 28, сцена room). Браузер: window.Timing28; node: require('./timing28.js').
(function (root) {
  const FPS = 30, DENSE = 1.6, HIT = 1.78, WHY = 8.0, SMILE = 30.72;
  const frac = x => x - Math.floor(x);
  const hash01 = (i, s) => frac(Math.sin(i * 127.1 + s * 311.7) * 43758.5453123);
  function vnoise(t, hz, seed) { const x = t * hz, i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
    const a = hash01(i, seed), b = hash01(i + 1, seed); return a + (b - a) * u; }
  function flame(t, shot) { return shot === 's01' ? 0 : 0.85 + 0.30 * vnoise(t, 7, 7); }
  function lamp(t, shot) { return 1.0; }
  function tv(t, shot) { return 0.0; }
  const T = { FPS, DENSE, HIT, WHY, SMILE, flame, lamp, tv, vnoise, hash01 };
  if (typeof module !== 'undefined' && module.exports) { module.exports = T;
    if (require.main === module && process.argv.includes('--dump')) { const o = {};
      for (const s of ['s01', 's04', 's14']) { o[s] = {};
        for (const n of ['flame', 'lamp']) { o[s][n] = []; for (let f = 0; f <= 38 * FPS; f++) o[s][n].push(T[n](f / FPS, s)); } }
      process.stdout.write(JSON.stringify(o)); } } else root.Timing28 = T;
})(typeof window !== 'undefined' ? window : this);
