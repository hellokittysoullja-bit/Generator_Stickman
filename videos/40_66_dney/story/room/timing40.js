// Точная копия timing40.py (рилс 40, сцена room). Браузер: window.Timing40; node: require('./timing40.js').
(function (root) {
  const FPS = 30, OVERSLEPT = 3.04, WAVE = 6.32, GIVEUP = 6.64, WHY = 8.08, WRITE = 34.76, CAT_WORD = 35.28;
  const frac = x => x - Math.floor(x);
  const hash01 = (i, s) => frac(Math.sin(i * 127.1 + s * 311.7) * 43758.5453123);
  function vnoise(t, hz, seed) { const x = t * hz, i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
    const a = hash01(i, seed), b = hash01(i + 1, seed); return a + (b - a) * u; }
  function smoothstep(e0, e1, x) { const u = Math.min(1, Math.max(0, (x - e0) / (e1 - e0))); return u * u * (3 - 2 * u); }
  function flame(t, shot) { return 0.85 + 0.30 * vnoise(t, 7, 7); }
  function lamp(t, shot) { return shot === 's03' ? 0.55 : 1.0; }
  function tv(t, shot) { return 0.0; }
  const T = { FPS, OVERSLEPT, WAVE, GIVEUP, WHY, WRITE, CAT_WORD, flame, lamp, tv, vnoise, smoothstep, hash01 };
  if (typeof module !== 'undefined' && module.exports) { module.exports = T;
    if (require.main === module && process.argv.includes('--dump')) { const o = {};
      for (const s of ['s03', 's05', 's06', 's18']) { o[s] = {};
        for (const n of ['flame', 'lamp']) { o[s][n] = []; for (let f = 0; f <= 39 * FPS; f++) o[s][n].push(T[n](f / FPS, s)); } }
      process.stdout.write(JSON.stringify(o)); } } else root.Timing40 = T;
})(typeof window !== 'undefined' ? window : this);
