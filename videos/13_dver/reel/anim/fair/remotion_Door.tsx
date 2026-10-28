// Хук рилса 13 в Remotion: тот же мир сцены, что в HyperFrames (слои kit/, окно 1440×1920 от (230, 740) в ×2),
// те же моменты и амплитуды. Анимация — средствами Remotion: функция номера кадра, interpolate/Easing, spring.
import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig, interpolate, Easing, spring } from "remotion";
import { CameraMotionBlur } from "@remotion/motion-blur";

const PRE = 0.14, STEP = 0.36;
const FOOT = "840px 1780px", TAIL_PIVOT = "311px 501px", CLOUD_C = "732px 303px";
const INK = "#18181a";
const p2o = Easing.out(Easing.cubic), p2i = Easing.in(Easing.cubic), p3o = Easing.out(Easing.poly(4)), p3i = Easing.in(Easing.poly(4));
const sio = Easing.inOut(Easing.sin), p2io = Easing.inOut(Easing.cubic);
const backOut = (c: number) => Easing.out(Easing.back(c));
const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// ключи [t, значение, кривая до этого ключа]: держит значение до первого и после последнего
type K = [number, number, ((x: number) => number)?];
const kf = (t: number, ks: K[]) => {
  if (t <= ks[0][0]) return ks[0][1];
  for (let i = 1; i < ks.length; i++) {
    const [t1, v1, e] = ks[i]; const [t0, v0] = ks[i - 1];
    if (t <= t1) return interpolate(t, [t0, t1], [v0, v1], { ...cl, easing: e ?? Easing.linear });
  }
  return ks[ks.length - 1][1];
};
// качание «туда-обратно» c периодом half*2, как yoyo
const yoyo = (t: number, t0: number, a: number, b: number, half: number, n: number) => {
  if (t < t0) return a;
  const k = Math.min((t - t0) / half, n); const i = Math.floor(k); const f = k - i;
  const u = sio(f); return i % 2 === 0 ? a + (b - a) * u : b + (a - b) * u;
};

const Scene: React.FC<{ hit: number }> = ({ hit: H }) => {
  const frame = useCurrentFrame(); const { fps } = useVideoConfig();
  const t = frame / fps;
  const spr = (t0: number, damping: number) => spring({ frame: (t - t0) * fps, fps, config: { damping, stiffness: 260, mass: 0.6 } });

  // кот: подход, шаги вперевалку, присед перед ударом, испуг на ударе
  const approach = interpolate(t, [0, H - PRE], [0.95, 1.04], cl);
  const steps: K[] = [[0, -8]], sY: K[] = [[0, 1]], sX: K[] = [[0, 1]], rot: K[] = [[0, 1.1]];
  let s = 0, side = 1;
  while (s + STEP <= H - PRE + 1e-6) {
    steps.push([s + STEP * 0.45, -20, p2o], [s + STEP, 0, p2i]);
    sY.push([s + STEP * 0.45, 1.025, p2o], [s + STEP, 0.962, p2i]);
    sX.push([s + STEP * 0.45, 0.985, p2o], [s + STEP, 1.03, p2i]);
    rot.push([s + STEP * 0.45, 2.4 * side, p2o], [s + STEP, 0, p2i]);
    s += STEP; side = -side;
  }
  steps.push([H, 6, p2io], [H + 0.07, 0, p3o]); sY.push([H, 0.94, p2io], [H + 0.07, 1, p3o]);
  sX.push([H, 1.045, p2io], [H + 0.07, 1, p3o]); rot.push([H, -1.2, p2io], [H + 0.07, 0, p3o]);
  const up = t < H ? 0 : t < H + 0.07 ? interpolate(t, [H, H + 0.07], [0, 1], { ...cl, easing: p3o }) : 1 - spr(H + 0.07, 7);
  const stY = -48 * up, stSY = 1 + 0.1 * up, stSX = 1 - 0.07 * up;
  // хвост: качается с запаздыванием, на ударе хлёст и пружина
  const tailSwing = yoyo(t, 0.05, -7, 9, STEP, Math.max(1, Math.floor((H - 0.05) / STEP)));
  const tailHit = t < H ? 0 : t < H + 0.1 ? interpolate(t, [H, H + 0.1], [0, 1], { ...cl, easing: p2o }) : 1 - spr(H + 0.1, 6);
  const tailRot = t < H ? tailSwing : tailSwing + (14 - tailSwing) * tailHit;

  // мысль: надувается с кадра 0, плывёт за головой, раздувается перед ударом, лопается
  const pop = t < H - PRE ? interpolate(t, [0, 0.28], [0.8, 1], { ...cl, easing: backOut(2.2) }) : interpolate(t, [H - PRE, H], [1, 1.12], { ...cl, easing: p2i });
  const popY = interpolate(t, [0, 0.28], [34, 0], { ...cl, easing: backOut(2.2) });
  const follow = yoyo(t, 0.08, -4, -16, STEP, Math.max(1, Math.floor((H - PRE - 0.08) / STEP)));
  const followR = yoyo(t, 0.08, -1.5, 1.8, STEP, Math.max(1, Math.floor((H - PRE - 0.08) / STEP)));
  const cloudS = interpolate(t, [H, H + 0.1], [1, 1.35], { ...cl, easing: p2o }), cloudO = interpolate(t, [H, H + 0.1], [1, 0], { ...cl, easing: p2o });
  // карандаш: качается, дрожит, всасывается в точку
  let pr = yoyo(t, 0, -12, 12, 0.25, Math.floor((H - PRE) / 0.25)), py = yoyo(t, 0, -6, 8, 0.25, Math.floor((H - PRE) / 0.25)), px = 0;
  if (t >= H - PRE && t < H - 0.02) { const k = Math.floor((t - (H - PRE)) * 30); px = k % 2 ? 6 : 0; pr += k % 2 ? 4 : 0; }
  const pk = interpolate(t, [H - 0.02, H + 0.07], [0, 1], { ...cl, easing: p3i });
  const pS = 1 - pk, pRot = pr + 220 * pk;
  // пузырьки
  const b1 = t < H ? interpolate(t, [0, 0.16], [0.35, 1], { ...cl, easing: backOut(3) }) : interpolate(t, [H, H + 0.06], [1, 0], { ...cl, easing: p2i });
  const b2 = t < H - 0.03 ? interpolate(t, [0.05, 0.21], [0, 1], { ...cl, easing: backOut(3) }) : interpolate(t, [H - 0.03, H + 0.02], [1, 0], { ...cl, easing: p2i });

  // обрывки облачка и лучи: тот же генератор, что в HyperFrames
  let seed = 13; const rnd = () => { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; };
  const shards = Array.from({ length: 10 }, (_, i) => { const a = (2 * Math.PI * i) / 10 + (rnd() - 0.5) * 0.4; const r = 0.92 + rnd() * 0.1; const L = 46 + rnd() * 26; return { a, r, L, i }; });
  const rays = Array.from({ length: 8 }, (_, i) => ({ a: (2 * Math.PI * (i + 0.5)) / 8 + (rnd() - 0.5) * 0.25 }));
  const sk = interpolate(t, [H + 0.02, H + 0.44], [0, 1], { ...cl, easing: p2o });
  const rIn = interpolate(t, [H + 0.03, H + 0.11], [0, 1], { ...cl, easing: p3o }), rOut = interpolate(t, [H + 0.12, H + 0.32], [0, 1], { ...cl, easing: p2i });
  const q = (t0: number, rot0: number) => ({
    s: t < t0 ? 0 : interpolate(t, [t0, t0 + 0.3], [0.6, 1], { ...cl, easing: backOut(2.5) }),
    r: interpolate(t, [t0, t0 + 0.3], [-rot0, rot0], { ...cl, easing: backOut(2.5) }),
    d: interpolate(t, [t0, t0 + 0.16], [400, 0], { ...cl, easing: p2o }),
    ds: t < t0 + 0.14 ? 0 : interpolate(t, [t0 + 0.14, t0 + 0.26], [0, 1], { ...cl, easing: backOut(3) }),
  });
  const q1 = q(H + 0.14, -9), q2 = q(H + 0.26, 8);
  const abs = (l: number, tp: number): React.CSSProperties => ({ position: "absolute", left: l, top: tp });
  const full: React.CSSProperties = { position: "absolute", left: 0, top: 0, width: 1440, height: 1920 };

  return (
    <AbsoluteFill style={{ background: "#f7f3ea" }}>
      <Img src={staticFile("bg.png")} style={abs(0, 0)} />
      <div style={{ ...full, transformOrigin: FOOT, transform: `scale(${approach})` }}>
        <div style={{ ...full, transformOrigin: FOOT, transform: `translateY(${stY}px) scale(${stSX}, ${stSY})` }}>
          <div style={{ ...full, transformOrigin: FOOT, transform: `translateY(${kf(t, steps)}px) rotate(${kf(t, rot)}deg) scale(${kf(t, sX)}, ${kf(t, sY)})` }}>
            <Img src={staticFile("tail.png")} style={{ ...abs(194, 989), transformOrigin: TAIL_PIVOT, transform: `rotate(${tailRot}deg)` }} />
            <Img src={staticFile("body.png")} style={abs(433, 657)} />
          </div>
        </div>
      </div>
      <div style={{ ...full, transformOrigin: CLOUD_C, transform: `translateY(${follow}px) rotate(${followR}deg)` }}>
        <div style={{ ...full, transformOrigin: CLOUD_C, transform: `translateY(${popY}px) scale(${pop})` }}>
          <Img src={staticFile("cloud.png")} style={{ ...abs(380, 27), opacity: cloudO, transform: `scale(${cloudS})` }} />
          <Img src={staticFile("pencil.png")} style={{ ...abs(612, 153), opacity: pS, transform: `translate(${px}px, ${py}px) rotate(${pRot}deg) scale(${pS})` }} />
        </div>
        <Img src={staticFile("bubble1.png")} style={{ ...abs(737, 588), transform: `scale(${b1})` }} />
        <Img src={staticFile("bubble2.png")} style={{ ...abs(764, 677), transform: `scale(${b2})` }} />
      </div>
      <svg width={1440} height={1920} style={full}>
        {t >= H + 0.02 && shards.map((sh) => (
          <g key={sh.i} transform={`translate(${732 + 330 * sh.r * Math.cos(sh.a) + 260 * sk * Math.cos(sh.a)} ${303 + 250 * sh.r * Math.sin(sh.a) + 260 * sk * Math.sin(sh.a)}) rotate(${(sh.i % 2 ? 1 : -1) * 70 * sk})`} opacity={1 - sk}>
            <path d={`M ${-sh.L} 0 Q 0 ${-0.75 * sh.L} ${sh.L} 0`} transform={`rotate(${(sh.a * 180) / Math.PI + 90})`} fill="none" stroke={INK} strokeWidth={11} strokeLinecap="round" />
          </g>))}
        {t >= H + 0.03 && rays.map((r, i) => (
          <g key={i} transform={`translate(${732 + 400 * Math.cos(r.a)} ${303 + 330 * Math.sin(r.a)}) rotate(${(r.a * 180) / Math.PI})`} opacity={1 - rOut}>
            <line x1={60 * rOut} y1={0} x2={60 * rOut + 120 * rIn} y2={0} stroke={INK} strokeWidth={13} strokeLinecap="round" />
          </g>))}
        {[[q1, 600, 330, "M -42 -52 C -42 -112 46 -118 46 -58 C 46 -18 2 -12 2 34", 17, 78, 12],
          [q2, 880, 270, "M -34 -42 C -34 -92 38 -96 38 -48 C 38 -15 2 -10 2 28", 14, 64, 10]].map(([qq, x, y, d, w, dy, rr]: any, i) => (
          <g key={i} transform={`translate(${x} ${y}) rotate(${qq.r}) scale(${qq.s})`}>
            <path d={d} fill="none" stroke={INK} strokeWidth={w} strokeLinecap="round" strokeDasharray={400} strokeDashoffset={qq.d} />
            <circle cx={2} cy={dy} r={rr * qq.ds} fill={INK} />
          </g>))}
      </svg>
    </AbsoluteFill>
  );
};

export const Door: React.FC<{ hit: number; blur: boolean }> = ({ hit, blur }) =>
  blur ? <CameraMotionBlur shutterAngle={180} samples={24}><Scene hit={hit} /></CameraMotionBlur> : <Scene hit={hit} />;
