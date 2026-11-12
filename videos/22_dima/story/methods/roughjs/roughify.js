// Rough.js поверх композиции night.html: каждая фигура SVG перерисовывается «от руки».
// Заливка исходной фигуры остаётся (плоский цвет), сверху — штриховка тоном темнее и рукописный контур.
// window.render(t, mode) — кадр анимации в момент t (с), mode: 'color' (заливка+штриховка) | 'pure' (только Rough).
(function () {
  const svg = document.getElementById('scene');
  const PRISTINE = svg.innerHTML;
  const NS = 'http://www.w3.org/2000/svg';

  function rgb(s) {
    const m = s.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    return m[1].split(',').map(Number);
  }
  function shade(c, k) {
    return `rgb(${Math.round(c[0] * k)},${Math.round(c[1] * k)},${Math.round(c[2] * k)})`;
  }
  function num(el, a) { return parseFloat(el.getAttribute(a) || '0'); }

  function toD(el) {
    const t = el.tagName;
    if (t === 'path') return el.getAttribute('d');
    if (t === 'line') return `M${num(el, 'x1')} ${num(el, 'y1')} L${num(el, 'x2')} ${num(el, 'y2')}`;
    if (t === 'circle' || t === 'ellipse') {
      const cx = num(el, 'cx'), cy = num(el, 'cy');
      const rx = t === 'circle' ? num(el, 'r') : num(el, 'rx');
      const ry = t === 'circle' ? num(el, 'r') : num(el, 'ry');
      return { ellipse: [cx, cy, rx * 2, ry * 2] };
    }
    if (t === 'rect') {
      const x = num(el, 'x'), y = num(el, 'y'), w = num(el, 'width'), h = num(el, 'height');
      const r = Math.min(num(el, 'rx'), w / 2, h / 2);
      if (!r) return `M${x} ${y} h${w} v${h} h${-w} z`;
      return `M${x + r} ${y} h${w - 2 * r} a${r} ${r} 0 0 1 ${r} ${r} v${h - 2 * r} a${r} ${r} 0 0 1 ${-r} ${r}` +
        ` h${-(w - 2 * r)} a${r} ${r} 0 0 1 ${-r} ${-r} v${-(h - 2 * r)} a${r} ${r} 0 0 1 ${r} ${-r} z`;
    }
    return null;
  }

  function roughify(seed, mode) {
    const rc = rough.svg(svg);
    const els = [...svg.querySelectorAll('rect,circle,ellipse,path,line')];
    for (const el of els) {
      const pat = el.closest('pattern');
      if (el.closest('defs') && !(pat && /^(check|floor|floor2)$/.test(pat.id))) continue;
      if (el.classList.contains('night') || el.classList.contains('glow')) continue;
      const fa = el.getAttribute('fill') || '';
      if (/url\(#(phoneGlow|flameGlow|moonGlow|sky|grain)/.test(fa)) continue;
      let bb;
      try { bb = el.getBBox(); } catch (e) { continue; }
      if (pat) bb = { width: num(el, 'width') || Math.abs(num(el, 'x2') - num(el, 'x1')) + 20, height: num(el, 'height') || Math.abs(num(el, 'y2') - num(el, 'y1')) + 20 };
      if (bb.width < 14 && bb.height < 14) continue;          // щетина, мелкие точки — как есть
      const cs = getComputedStyle(el);
      const sw = parseFloat(cs.strokeWidth) || 0;
      const hasStroke = cs.stroke !== 'none' && sw > 0 && sw <= 12;
      const fillSolid = rgb(cs.fill);
      const fillPattern = cs.fill.startsWith('url(');
      if (!hasStroke && !fillSolid) continue;
      if (sw > 12) continue;                                   // толстый хвост-штрих — как есть
      const geom = toD(el);
      if (!geom) continue;
      const big = bb.width * bb.height > 900;
      const o = {
        seed, roughness: 1.15, bowing: 1.2, disableMultiStroke: false,
        stroke: hasStroke ? cs.stroke : 'none', strokeWidth: hasStroke ? Math.max(1.6, sw * 0.62) : 0,
        fill: undefined, preserveVertices: false,
      };
      if (fillSolid && big) {
        if (mode === 'pure') {
          o.fill = cs.fill; o.fillStyle = 'cross-hatch'; o.hachureGap = 7; o.fillWeight = 1.8; o.hachureAngle = -41;
        } else {
          o.fill = shade(fillSolid, 0.8); o.fillStyle = 'hachure'; o.hachureGap = 10; o.fillWeight = 1.2;
          o.hachureAngle = -41;
        }
      }
      if (fillPattern && mode === 'pure') {
        // в «чистом» режиме узор пледа/обоев остаётся, но под штриховкой цвета-основы
      }
      const node = geom.ellipse ? rc.ellipse(...geom.ellipse, o) : rc.path(geom, o);
      const tr = el.getAttribute('transform');
      if (tr) node.setAttribute('transform', tr);
      const op = el.getAttribute('opacity');
      if (op) node.setAttribute('opacity', op);
      if (mode === 'color' && fillSolid && big) node.setAttribute('opacity', String((op ? +op : 1)));
      el.after(node);
      if (mode === 'pure' && fillSolid && big) el.style.fillOpacity = '0.5';
      el.style.stroke = 'none';
    }
  }

  // ---------- анимация ----------
  const blink = (t, at, dur = 0.2) => {
    const x = (t - at) / dur;
    return x < 0 || x > 1 ? 0 : Math.sin(Math.PI * x);
  };
  const smooth = (x) => x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x);

  function animate(t) {
    const q = (s) => svg.querySelector(s);
    // Дима моргает (0.9 с и 2.5 с): веко опускается до низа глаза
    const b = Math.max(blink(t, 0.9), blink(t, 2.5));
    const lids = [q('#lidL'), q('#lidR')];
    lids.forEach((r) => r.setAttribute('height', String(48 + 48 * b)));
    svg.querySelectorAll('#eyes > path').forEach((p) => p.setAttribute('transform', `translate(0 ${44 * b})`));
    svg.querySelectorAll('#eyes > circle').forEach((c) => c.setAttribute('opacity', String(1 - b)));
    // большой палец листает: два свайпа вверх
    const sw = (a) => { const x = (t - a) / 0.35; return x < 0 || x > 1 ? 0 : Math.sin(Math.PI * x); };
    const s = Math.max(sw(0.4), sw(1.7));
    q('#thumb').setAttribute('transform', `translate(${-4 * s} ${-16 * s})`);
    // свет экрана: ровное мерцание + вспышка после свайпа (новый ролик)
    const flash = Math.max(smooth(1 - Math.abs(t - 0.75) / 0.2), smooth(1 - Math.abs(t - 2.05) / 0.2));
    const g = q('#phoneGlowEl');
    g.setAttribute('opacity', String(0.82 + 0.08 * Math.sin(t * 23) * Math.sin(t * 7.3) + 0.25 * flash));
    // огонёк: колышется от основания
    const fx = 968, fy = 1212;
    const sk = 7 * Math.sin(t * 9.0) + 3 * Math.sin(t * 15.7);
    const sy = 1 + 0.07 * Math.sin(t * 11.3);
    q('#flame').setAttribute('transform', `translate(30 30) translate(${fx - 30} ${fy - 30}) skewX(${sk}) scale(1 ${sy}) translate(${-(fx - 30)} ${-(fy - 30)})`);
    // кот моргает (1.6 с)
    const cb = blink(t, 1.6, 0.24);
    ['#catLidL', '#catLidR'].forEach((id) => q(id).setAttribute('height', String(56 * cb)));
  }

  window.render = function (t = 0, mode = 'color', boil = true) {
    svg.innerHTML = PRISTINE;
    animate(t);
    roughify(boil ? 1 + Math.floor(t * 12) : 7, mode);   // «кипение» линий 12 раз в секунду
    return true;
  };
})();
