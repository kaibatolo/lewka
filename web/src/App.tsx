import { SearchPage } from "./pages/Search";
import { GalleryPage } from "./pages/Gallery";

export function App() {
  const path = window.location.pathname.replace(/\/$/, "") || "/";
  const gallery = path === "/gallery" || path.endsWith("/gallery");
  return (
    <div className="shell">
      <header>
        <a href="/" className={gallery ? "" : "on"}>
          Lewka
        </a>
        <a href="/gallery" className={gallery ? "on" : ""}>
          Gallery
        </a>
      </header>
      <main>{gallery ? <GalleryPage /> : <SearchPage />}</main>
    </div>
  );
}
