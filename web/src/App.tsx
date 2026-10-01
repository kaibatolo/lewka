import { useState } from "react";
import { SearchPage } from "./pages/Search";
import { GalleryPage } from "./pages/Gallery";
import { Water } from "./pages/Water";

export function App() {
  const path = window.location.pathname.replace(/\/$/, "") || "/";
  const gallery = path === "/gallery" || path.endsWith("/gallery");
  const [paused, setPaused] = useState(false);
  return (
    <div className="shell">
      <Water paused={paused} />
      <header>
        <a href="/" className={gallery ? "" : "on"}>
          Lewka
        </a>
        <a href="/gallery" className={gallery ? "on" : ""}>
          Gallery
        </a>
      </header>
      <main>
        {gallery ? (
          <GalleryPage onPlay={(on) => setPaused(on)} />
        ) : (
          <SearchPage onPlay={(on) => setPaused(on)} />
        )}
      </main>
    </div>
  );
}
