// Честное сравнение: тот же хук по тем же числам движения, что снял extract.js с HyperFrames (шаг 1/10 кадра).
// Remotion рисует слои своими средствами и размывает своим CameraMotionBlur (180°, 10 подкадров — по умолчанию).
import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { CameraMotionBlur } from "@remotion/motion-blur";
import T from "./tracks_sub10.json";

const FILES: Record<string, string> = { bg: "bg.png", tail: "tail.png", body: "body.png", cloud: "cloud.png", pencil: "pencil.png", b1: "bubble1.png", b2: "bubble2.png" };
type Fr = { layers: { id: string; m: number[]; o: number }[]; strokes: { pts: number[][]; w: number; o: number }[]; dots: { x: number; y: number; r: number; o: number }[] };

const Scene: React.FC = () => {
  const f = useCurrentFrame();
  const i = Math.max(0, Math.min(T.frames.length - 1, Math.round(f * (T as any).sub)));
  const fr = (T.frames as Fr[])[i];
  return (
    <AbsoluteFill style={{ background: "#f7f3ea" }}>
      {fr.layers.map((l) => (
        <Img key={l.id} src={staticFile(FILES[l.id])}
             style={{ position: "absolute", left: 0, top: 0, transformOrigin: "0 0", opacity: l.o,
                      transform: `matrix(${l.m.join(",")})` }} />
      ))}
      <svg width={1440} height={1920} style={{ position: "absolute", left: 0, top: 0 }}>
        {fr.strokes.map((s, k) => (
          <polyline key={k} points={s.pts.map((p) => p.join(",")).join(" ")} fill="none" stroke="#18181a"
                    strokeWidth={s.w} strokeLinecap="round" strokeLinejoin="round" opacity={s.o} />
        ))}
        {fr.dots.map((d, k) => <circle key={k} cx={d.x} cy={d.y} r={d.r} fill="#18181a" opacity={d.o} />)}
      </svg>
    </AbsoluteFill>
  );
};

export const Fair: React.FC<{ blur: boolean }> = ({ blur }) =>
  blur ? <CameraMotionBlur shutterAngle={180} samples={10}><Scene /></CameraMotionBlur> : <Scene />;
