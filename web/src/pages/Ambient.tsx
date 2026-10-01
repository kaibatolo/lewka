const LOCAL = "/bg.loop.mp4";
const FALLBACK = "https://assets.mixkit.co/videos/preview/mixkit-stars-in-space-1610-large.mp4";

export function Ambient({ paused }: { paused?: boolean }) {
  return (
    <video
      className={paused ? "ambient paused" : "ambient"}
      autoPlay
      muted
      loop
      playsInline
      preload="auto"
      aria-hidden="true"
    >
      <source src={LOCAL} type="video/mp4" />
      <source src={FALLBACK} type="video/mp4" />
    </video>
  );
}
