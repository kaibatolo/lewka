import { useEffect, useState } from "react";
import { LANES, gallery, type Item } from "../lib/api";

export function GalleryPage() {
  const [lane, setLane] = useState<string>(LANES[0]);
  const [items, setItems] = useState<Item[]>([]);
  const [note, setNote] = useState("warming");

  useEffect(() => {
    let live = true;
    void gallery(lane, 24)
      .then((data) => {
        if (!live) return;
        const next = data.items || [];
        setItems(next);
        setNote(`${next.length} tiles · ${lane}`);
      })
      .catch((err: unknown) => {
        if (!live) return;
        setItems([]);
        setNote(err instanceof Error ? err.message : "gallery missed");
      });
    return () => {
      live = false;
    };
  }, [lane]);

  return (
    <div>
      <h1>Gallery</h1>
      <p className="meta">{note}</p>
      <div className="tags">
        {LANES.map((f) => (
          <button key={f} type="button" className={lane === f ? "tag on" : "tag"} onClick={() => setLane(f)}>
            {f}
          </button>
        ))}
      </div>
      <div className="grid">
        {items.map((item) => (
          <a key={item.id} className="tile" href={item.url} target="_blank" rel="noopener noreferrer">
            {item.thumb ? <img src={item.thumb} alt="" /> : <div className="ph" />}
            <p>{item.source}</p>
            <h3>{(item.title || item.id).slice(0, 72)}</h3>
          </a>
        ))}
      </div>
    </div>
  );
}
