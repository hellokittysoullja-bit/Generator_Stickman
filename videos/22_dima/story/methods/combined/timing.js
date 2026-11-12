// Точная копия timing.py (общая таблица времени сцены «Дима, 01:47»). Подключение:
//   браузер: <script src="timing.js"></script> -> window.Timing.screen(t) …
//   node:    const T = require('./timing.js');
// Проверка совпадения с Python: python3 timing.py --check
(function (root) {
  const FPS = 30, DURATION = 3.0;
  const SWIPES = [0.55, 1.45, 2.35], SWIPE_UP = 0.18, SWIPE_BACK = 0.25;
  const FLASH_DELAY = 0.12, FLASH_ATTACK = 0.04, FLASH_DECAY = 0.35, FLASH_GAIN = 0.6, JITTER = 0.06;
  const DIMA_BLINKS = [1.15, 2.70], CAT_BLINK = 2.30, CAT_BLINK_DUR = 0.35;
  const TAIL_DEG = 4.0, TAIL_PERIOD = 2.2, PUSH = 0.06;

  const frac = x => x - Math.floor(x);
  const hash01 = (i, seed) => frac(Math.sin(i * 127.1 + seed * 311.7) * 43758.5453123);
  function vnoise(t, hz, seed) {
    const x = t * hz, i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
    const a = hash01(i, seed), b = hash01(i + 1, seed);
    return a + (b - a) * u;
  }
  function smoothstep(e0, e1, x) {
    const u = Math.min(1, Math.max(0, (x - e0) / (e1 - e0)));
    return u * u * (3 - 2 * u);
  }
  function flash(t) {
    let best = 0;
    for (const s of SWIPES) {
      const dt = t - (s + FLASH_DELAY);
      if (dt < 0) continue;
      let v;
      if (dt < FLASH_ATTACK) v = dt / FLASH_ATTACK;
      else if (dt < FLASH_ATTACK + FLASH_DECAY) { const u = 1 - (dt - FLASH_ATTACK) / FLASH_DECAY; v = u * u; }
      else v = 0;
      best = Math.max(best, v);
    }
    return best;
  }
  const screen = t => (1 + JITTER * (2 * vnoise(t, 7, 3) - 1)) * (1 + FLASH_GAIN * flash(t));
  const flame = t => 0.85 + 0.30 * vnoise(t, 9, 7);
  function thumb(t) {
    let best = 0;
    for (const s of SWIPES) {
      const dt = t - s;
      let v = 0;
      if (dt >= 0 && dt < SWIPE_UP) v = smoothstep(0, SWIPE_UP, dt);
      else if (dt >= SWIPE_UP && dt < SWIPE_UP + SWIPE_BACK) v = 1 - smoothstep(SWIPE_UP, SWIPE_UP + SWIPE_BACK, dt);
      best = Math.max(best, v);
    }
    return best;
  }
  function dima_blink(t) {
    let best = 0;
    for (const b of DIMA_BLINKS) {
      const dt = t - b;
      let v = 0;
      if (dt >= 0 && dt < 0.08) v = smoothstep(0, 0.08, dt);
      else if (dt >= 0.08 && dt < 0.17) v = 1 - smoothstep(0.08, 0.17, dt);
      best = Math.max(best, v);
    }
    return best;
  }
  function cat_blink(t) {
    const dt = t - CAT_BLINK, h = CAT_BLINK_DUR / 2;
    if (dt >= 0 && dt < h) return smoothstep(0, h, dt);
    if (dt >= h && dt < CAT_BLINK_DUR) return 1 - smoothstep(h, CAT_BLINK_DUR, dt);
    return 0;
  }
  const tail = t => TAIL_DEG * Math.sin(2 * Math.PI * t / TAIL_PERIOD);
  function pupils(t) {
    const marks = [0.0, ...SWIPES, DURATION + 0.6];
    for (let k = 0; k < marks.length - 1; k++) {
      const a = marks[k], b = marks[k + 1];
      if (a <= t && t < b) {
        const p = (t - a) / (b - a);
        let y = -1 + 2 * p;
        if (k > 0 && t - a < 0.1) { const prev = 1.0; y = prev + (y - prev) * smoothstep(0, 0.1, t - a); }
        return y;
      }
    }
    return 1.0;
  }
  const push = t => PUSH * smoothstep(0, DURATION, t);

  const T = { FPS, DURATION, SWIPES, DIMA_BLINKS, CAT_BLINK, screen, flame, thumb, dima_blink, cat_blink, tail,
              pupils, push, flash, vnoise, smoothstep };
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = T;
    if (require.main === module && process.argv.includes('--dump')) {
      const names = ['screen', 'flame', 'thumb', 'dima_blink', 'cat_blink', 'tail', 'pupils', 'push', 'flash'];
      const out = {};
      for (const n of names) { out[n] = []; for (let f = 0; f <= 90; f++) out[n].push(T[n](f / FPS)); }
      process.stdout.write(JSON.stringify(out));
    }
  } else root.Timing = T;
})(typeof window !== 'undefined' ? window : this);
