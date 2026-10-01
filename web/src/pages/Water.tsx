import { useEffect, useRef } from "react";

export function Water({ paused }: { paused?: boolean }) {
  const ref = useRef<HTMLCanvasElement>(null);
  const pausedRef = useRef(paused);
  pausedRef.current = paused;

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d", { alpha: false });
    if (!ctx) return;

    const sparks = Array.from({ length: 90 }, (_, i) => ({
      x: Math.random(),
      y: Math.random(),
      r: 6 + Math.random() * 28,
      s: 0.15 + Math.random() * 0.55,
      p: Math.random() * Math.PI * 2,
      warm: i % 5 !== 0,
    }));

    let raf = 0;
    let running = true;

    const fit = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.floor(window.innerWidth * dpr);
      canvas.height = Math.floor(window.innerHeight * dpr);
      canvas.style.width = `${window.innerWidth}px`;
      canvas.style.height = `${window.innerHeight}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    fit();
    window.addEventListener("resize", fit);

    const draw = (t: number) => {
      if (!running) return;
      const w = window.innerWidth;
      const h = window.innerHeight;
      const time = t * 0.001;
      const dim = pausedRef.current ? 0.35 : 1;

      ctx.fillStyle = "#071018";
      ctx.fillRect(0, 0, w, h);

      const sky = ctx.createLinearGradient(0, 0, 0, h);
      sky.addColorStop(0, "#102033");
      sky.addColorStop(0.45, "#0a1824");
      sky.addColorStop(1, "#050b12");
      ctx.fillStyle = sky;
      ctx.fillRect(0, 0, w, h);

      ctx.globalCompositeOperation = "lighter";
      ctx.globalAlpha = 0.22 * dim;
      for (let band = 0; band < 8; band++) {
        const y = h * (0.18 + band * 0.1) + Math.sin(time * 0.35 + band) * 18;
        const wave = ctx.createLinearGradient(0, y - 30, 0, y + 30);
        wave.addColorStop(0, "rgba(0,0,0,0)");
        wave.addColorStop(0.5, band % 2 ? "rgba(210,190,130,0.35)" : "rgba(180,210,230,0.2)");
        wave.addColorStop(1, "rgba(0,0,0,0)");
        ctx.fillStyle = wave;
        ctx.beginPath();
        ctx.moveTo(0, y);
        for (let x = 0; x <= w; x += 18) {
          const yy =
            y +
            Math.sin(x * 0.008 + time * 0.8 + band) * 10 +
            Math.sin(x * 0.02 + time * 1.4 + band * 2) * 4;
          ctx.lineTo(x, yy);
        }
        ctx.lineTo(w, y + 26);
        ctx.lineTo(0, y + 26);
        ctx.closePath();
        ctx.fill();
      }

      for (const spark of sparks) {
        spark.x += Math.sin(time * spark.s + spark.p) * 0.00035;
        spark.y += Math.cos(time * spark.s * 0.7 + spark.p) * 0.00022;
        if (spark.x < -0.05) spark.x = 1.05;
        if (spark.x > 1.05) spark.x = -0.05;
        if (spark.y < -0.05) spark.y = 1.05;
        if (spark.y > 1.05) spark.y = -0.05;
        const x = spark.x * w + Math.sin(time * 0.9 + spark.p) * 24;
        const y = spark.y * h + Math.cos(time * 0.6 + spark.p) * 10;
        const pulse = 0.45 + 0.55 * (0.5 + 0.5 * Math.sin(time * 2.2 + spark.p));
        const g = ctx.createRadialGradient(x, y, 0, x, y, spark.r * 2.2);
        if (spark.warm) {
          g.addColorStop(0, `rgba(255,236,190,${0.55 * pulse * dim})`);
          g.addColorStop(0.35, `rgba(227,196,120,${0.18 * pulse * dim})`);
        } else {
          g.addColorStop(0, `rgba(220,236,255,${0.4 * pulse * dim})`);
          g.addColorStop(0.35, `rgba(160,190,220,${0.12 * pulse * dim})`);
        }
        g.addColorStop(1, "rgba(0,0,0,0)");
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.ellipse(x, y, spark.r * 2.4, spark.r * 0.7, 0, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.globalCompositeOperation = "source-over";
      ctx.globalAlpha = 1;
      raf = requestAnimationFrame(draw);
    };

    raf = requestAnimationFrame(draw);
    return () => {
      running = false;
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", fit);
    };
  }, []);

  return <canvas ref={ref} className={paused ? "water paused" : "water"} aria-hidden="true" />;
}
