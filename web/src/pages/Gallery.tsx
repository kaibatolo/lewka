import { useEffect, useState } from "react";
import { LANES, federate, gallery, type Item } from "../lib/api";
import { Player } from "./Player";

export function GalleryPage({ onPlay }: { onPlay?: (on: boolean) => void }) {
  const [lane, setLane] = useState<string>(LANES[0]);
  const [items, setItems] = useState<Item[]>([]);
  const [note, setNote] = useState("warming");
  const [active, setActive] = useState<Item | null>(null);

  useEffect(() => {
    let live = true;
    void gallery(lane, 80)
      .then((data) => {
        if (!live) return;
        const next = federate(data.items || [], 24);
        setItems(next);
        setNote(`${next.length} tiles · ${lane} · cap 20%`);
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

  function open(item: Item) {
    setActive(item);
    onPlay?.(true);
  }

  function close() {
    setActive(null);
    onPlay?.(false);
  }

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
          <button key={item.id} type="button" className="tile" onClick={() => open(item)}>
            {item.thumb ? <img src={item.thumb} alt="" /> : <div className="ph" />}
            {item.kind === "video" || item.source === "eporner" ? <span className="play">play</span> : null}
            <p>{item.source}</p>
            <h3>{(item.title || item.id).slice(0, 72)}</h3>
          </button>
        ))}
      </div>
      {active ? <Player item={active} onClose={close} /> : null}
    </div>
  );
}
