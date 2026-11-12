// Точная копия timing23.py (рилс 23). Браузер: window.Timing23; node: require('./timing23.js').
(function (root) {
  const FPS = 30, END = 34.10, FLASH_ATTACK = 0.03, FLASH_DECAY = 0.25, FLASH_GAIN = 0.7, JITTER = 0.05, PLAY_AT = 25.72;
  function panic() {
    const out = []; let t = 18.62;
    while (t < 22.60) { out.push(Math.round(t * 1e4) / 1e4); const u = (t - 18.62) / (22.60 - 18.62); t += 0.34 - 0.24 * u; }
    return out;
  }
  const SWITCHES = [0.42, 0.98, 1.50, 1.82, 2.12, 2.42, 4.92, 5.40, 5.90, 6.30, ...panic(), 23.20, 23.95, 24.62];
  const frac = x => x - Math.floor(x);
  const hash01 = (i, s) => frac(Math.sin(i * 127.1 + s * 311.7) * 43758.5453123);
  function vnoise(t, hz, seed) { const x = t * hz, i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
    const a = hash01(i, seed), b = hash01(i + 1, seed); return a + (b - a) * u; }
  function smoothstep(e0, e1, x) { const u = Math.min(1, Math.max(0, (x - e0) / (e1 - e0))); return u * u * (3 - 2 * u); }
  function switch_flash(t) { let best = 0;
    for (const s of SWITCHES) { const dt = t - s; if (dt < 0 || dt > FLASH_ATTACK + FLASH_DECAY) continue;
      const v = dt < FLASH_ATTACK ? dt / FLASH_ATTACK : Math.pow(1 - (dt - FLASH_ATTACK) / FLASH_DECAY, 2); best = Math.max(best, v); }
    return best; }
  function tv(t) { let base = 1 + JITTER * (2 * vnoise(t, 7, 11) - 1); const film = smoothstep(PLAY_AT, PLAY_AT + 0.4, t);
    base = base * (1 - film) + film * (1.08 + 0.10 * (2 * vnoise(t, 1.3, 5) - 1)); return base * (1 + FLASH_GAIN * switch_flash(t)); }
  const flame = t => (0.85 + 0.30 * vnoise(t, 9, 7)) * (1 + 0.35 * smoothstep(28.9, 29.6, t));
  const T = { FPS, END, SWITCHES, PLAY_AT, tv, flame, switch_flash, vnoise, smoothstep };
  if (typeof module !== 'undefined' && module.exports) { module.exports = T;
    if (require.main === module && process.argv.includes('--dump')) { const o = {};
      for (const n of ['tv', 'flame', 'switch_flash']) { o[n] = []; for (let f = 0; f <= Math.floor(END * FPS); f++) o[n].push(T[n](f / FPS)); }
      process.stdout.write(JSON.stringify(o)); } } else root.Timing23 = T;
})(typeof window !== 'undefined' ? window : this);
