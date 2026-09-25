import { useState, type FormEvent } from "react";
import { search, type Item } from "../lib/api";

const HINTS = ["goth", "egirl", "ffm", "pov", "alt"] as const;

export function SearchPage() {
  const [q, setQ] = useState("");
  const [items, setItems] = useState<Item[]>([]);
  const [note, setNote] = useState("Adult index. Type a lane.");
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);

  async function run(term: string) {
    const t = term.trim();
    if (!t) return;
    setBusy(true);
    setQ(t);
    setDone(true);
    try {
      const data = await search(t, 24);
      const next = data.items || [];
      setItems(next);
      setNote(`${next.length} hits · ${t}${(data.sources || []).length ? ` · ${data.sources?.join(", ")}` : ""}`);
    } catch (err) {
      setItems([]);
      setNote(err instanceof Error ? err.message : "search missed");
    } finally {
      setBusy(false);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    void run(q);
  }

  return (
    <div>
      <form onSubmit={onSubmit}>
        <p className="mark">Lewka</p>
        <div className="row">
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search the vault" autoFocus />
          <button type="submit" disabled={busy}>
            {busy ? "Searching…" : "Search"}
          </button>
        </div>
        <div className="tags">
          {HINTS.map((h) => (
            <button key={h} type="button" className="tag" onClick={() => void run(h)}>
              {h}
            </button>
          ))}
        </div>
        <p className="meta">{note}</p>
      </form>
      {done ? (
        <div className="grid">
          {items.map((item) => (
            <a key={item.id} className="tile" href={item.url} target="_blank" rel="noopener noreferrer">
              {item.thumb ? <img src={item.thumb} alt="" /> : <div className="ph" />}
              <p>{item.source}</p>
              <h3>{(item.title || item.id).slice(0, 80)}</h3>
            </a>
          ))}
        </div>
      ) : null}
    </div>
  );
}
