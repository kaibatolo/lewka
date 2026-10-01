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

    let raf = 0;
    let running = true;

    const fit = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      canvas.width = Math.floor(window.innerWidth * dpr);
      canvas.height = Math.floor(window.innerHeight * dpr);
      canvas.style.width = "100%";
      canvas.style.height = "100%";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    fit();
    window.addEventListener("resize", fit);

    const draw = (now: number) => {
      if (!running) return;
      const w = window.innerWidth;
      const h = window.innerHeight;
      const time = now * 0.001;
      const dim = pausedRef.current ? 0.45 : 1;

      ctx.fillStyle = "#061018";
      ctx.fillRect(0, 0, w, h);
      const sky = ctx.createLinearGradient(0, 0, 0, h);
      sky.addColorStop(0, "#03080d");
      sky.addColorStop(0.22, "#07141e");
      sky.addColorStop(1, "#0a1c28");
      ctx.fillStyle = sky;
      ctx.fillRect(0, 0, w, h);

      const horizon = h * 0.12;
      const rows = 78;
      for (let i = 0; i < rows; i++) {
        const t = i / (rows - 1);
        const y = horizon + t * t * (h - horizon);
        const amp = 1.2 + t * t * 26;
        const freq = 0.0035 + t * 0.011;
        const speed = 0.45 + t * 1.1;
        const body = ctx.createLinearGradient(0, y - amp, 0, y + amp * 1.4);
        body.addColorStop(0, "rgba(4,12,18,0)");
        body.addColorStop(0.55, `rgba(10,28,40,${0.35 + t * 0.4})`);
        body.addColorStop(1, "rgba(4,10,16,0)");
        ctx.strokeStyle = body;
        ctx.lineWidth = 2 + t * 7;
        ctx.beginPath();
        for (let x = 0; x <= w; x += 10) {
          const yy =
            y +
            Math.sin(x * freq + time * speed + i * 0.7) * amp +
            Math.sin(x * freq * 2.2 + time * 1.15 + i) * amp * 0.28;
          if (x === 0) ctx.moveTo(x, yy);
          else ctx.lineTo(x, yy);
        }
        ctx.stroke();

        ctx.lineWidth = 0.7 + t * 1.6;
        ctx.strokeStyle = `rgba(226, 186, 96, ${(0.08 + t * 0.62) * dim})`;
        ctx.beginPath();
        let pen = false;
        for (let x = 0; x <= w; x += 5) {
          const phase = x * freq + time * speed + i * 0.7;
          const crest = Math.sin(phase);
          const yy =
            y +
            crest * amp +
            Math.sin(x * freq * 2.2 + time * 1.15 + i) * amp * 0.28;
          if (crest > 0.62) {
            if (!pen) {
              ctx.moveTo(x, yy);
              pen = true;
            } else ctx.lineTo(x, yy);
          } else if (pen) {
            ctx.stroke();
            ctx.beginPath();
            pen = false;
          }
        }
        if (pen) ctx.stroke();
      }

      ctx.globalCompositeOperation = "lighter";
      for (let i = 0; i < 18; i++) {
        const t = (i + 1) / 19;
        const y = horizon + t * t * (h - horizon) + Math.sin(time * 0.4 + i) * 6;
        const x = (0.08 + ((i * 0.37) % 0.84)) * w + Math.sin(time * 0.25 + i) * 30;
        const rw = 18 + t * 70;
        const g = ctx.createRadialGradient(x, y, 0, x, y, rw);
        g.addColorStop(0, `rgba(255, 226, 150, ${0.22 * dim})`);
        g.addColorStop(0.4, `rgba(210, 170, 80, ${0.08 * dim})`);
        g.addColorStop(1, "rgba(0,0,0,0)");
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.ellipse(x, y, rw, 2 + t * 5, 0, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalCompositeOperation = "source-over";

      const vignette = ctx.createRadialGradient(w * 0.5, h * 0.42, h * 0.2, w * 0.5, h * 0.5, h * 0.85);
      vignette.addColorStop(0, "rgba(0,0,0,0)");
      vignette.addColorStop(1, "rgba(2,6,10,0.45)");
      ctx.fillStyle = vignette;
      ctx.fillRect(0, 0, w, h);

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
