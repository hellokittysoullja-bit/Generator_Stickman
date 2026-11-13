// Точная копия timing25.py (рилс 25, сцена room). Браузер: window.Timing25; node: require('./timing25.js').
(function (root) {
  const FPS = 30, WHY = 7.52, TOMORROW = 6.20, NOTSLEEP = 3.28, CATTOO = 27.92, EYES = 29.45, SLOWBLINK = 30.55;
  const frac = x => x - Math.floor(x);
  const hash01 = (i, s) => frac(Math.sin(i * 127.1 + s * 311.7) * 43758.5453123);
  function vnoise(t, hz, seed) { const x = t * hz, i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
    const a = hash01(i, seed), b = hash01(i + 1, seed); return a + (b - a) * u; }
  function smoothstep(e0, e1, x) { const u = Math.min(1, Math.max(0, (x - e0) / (e1 - e0))); return u * u * (3 - 2 * u); }
  function flame(t, shot) {
    const base = 0.85 + 0.30 * vnoise(t, 7, 7);
    let k;
    if (shot === 's10') k = 1.0;
    else if (shot === 's13') k = 0.78 - 0.33 * smoothstep(CATTOO, CATTOO + 0.6, t);
    else if (shot === 's14') k = 0.45 + 0.17 * smoothstep(EYES, EYES + 0.5, t);
    else if (shot === 's04') k = 0.64;
    else k = 0.52;
    return base * k;
  }
  function lamp(t, shot) { return shot === 's10' ? 1.0 : 0.0; }
  function tv(t, shot) { return 0.0; }
  const T = { FPS, WHY, TOMORROW, NOTSLEEP, CATTOO, EYES, SLOWBLINK, flame, lamp, tv, vnoise, smoothstep, hash01 };
  if (typeof module !== 'undefined' && module.exports) { module.exports = T;
    if (require.main === module && process.argv.includes('--dump')) { const o = {};
      for (const s of ['s02', 's03', 's04', 's10', 's13', 's14']) { o[s] = {};
        for (const n of ['flame', 'lamp']) { o[s][n] = []; for (let f = 0; f <= 33 * FPS; f++) o[s][n].push(T[n](f / FPS, s)); } }
      process.stdout.write(JSON.stringify(o)); } } else root.Timing25 = T;
})(typeof window !== 'undefined' ? window : this);
