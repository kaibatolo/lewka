import { useRef, useState, type FormEvent } from "react";
import { search, type Item } from "../lib/api";
import { LEWKA_TAGS } from "../lib/tags";

export function SearchPage() {
  const [q, setQ] = useState("");
  const [items, setItems] = useState<Item[]>([]);
  const [note, setNote] = useState("Adult index. 62 tags live. Type a lane and open Lewka.");
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  async function run(term: string) {
    const t = term.trim();
    if (!t) {
      inputRef.current?.focus();
      return;
    }
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
      <form className="lewka-bar" onSubmit={onSubmit} role="search">
        <p className="mark">Lewka</p>
        <div className="row lewka-input">
          <input
            ref={inputRef}
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="lewka search"
            aria-label="lewka search"
            autoFocus
            autoComplete="off"
            spellCheck={false}
          />
          <button type="submit" disabled={busy}>
            {busy ? "Searching…" : "Open Lewka"}
          </button>
        </div>
        <div className="tags">
          {LEWKA_TAGS.map((h) => (
            <button key={h} type="button" className={q === h ? "tag on" : "tag"} onClick={() => void run(h)}>
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
