import { useMemo, useRef, useState, type FormEvent } from "react";
import { federatedSearch, type Item } from "../lib/api";
import { LEWKA_TAGS } from "../lib/tags";
import { Player } from "./Player";

const FEATURED = LEWKA_TAGS.slice(0, 16);
const PRIORITY = ["reddit", "instagram", "erome", "xhamster", "pornhub", "chaturbate"];

export function SearchPage({ onPlay }: { onPlay?: (on: boolean) => void }) {
  const [q, setQ] = useState("");
  const [items, setItems] = useState<Item[]>([]);
  const [note, setNote] = useState("federated index · 20% cap per source");
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);
  const [more, setMore] = useState(false);
  const [want, setWant] = useState<string[]>(PRIORITY);
  const [active, setActive] = useState<Item | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const chips = useMemo(() => (more ? LEWKA_TAGS : FEATURED), [more]);

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
      const data = await federatedSearch(t, 24, want);
      const next = data.items || [];
      setItems(next);
      const mix = Object.entries(
        next.reduce<Record<string, number>>((acc, item) => {
          acc[item.source] = (acc[item.source] || 0) + 1;
          return acc;
        }, {}),
      )
        .map(([src, n]) => `${src} ${n}`)
        .join(" · ");
      setNote(`${next.length} shown · ${mix || "empty"} · cap 20%`);
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

  function toggleSource(name: string) {
    setWant((cur) => (cur.includes(name) ? cur.filter((s) => s !== name) : [...cur, name]));
  }

  function open(item: Item) {
    setActive(item);
    onPlay?.(true);
  }

  function close() {
    setActive(null);
    onPlay?.(false);
  }

  return (
    <div className={done ? "stage stage-results" : "stage"}>
      <form className="lewka-bar" onSubmit={onSubmit} role="search">
        <p className="mark">Lewka</p>
        <h1 className="hero">find it. play it.</h1>
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
          {PRIORITY.map((s) => (
            <button key={s} type="button" className={want.includes(s) ? "tag on" : "tag"} onClick={() => toggleSource(s)}>
              {s}
            </button>
          ))}
        </div>
        <div className="tags">
          {chips.map((h) => (
            <button key={h} type="button" className={q === h ? "tag on" : "tag"} onClick={() => void run(h)}>
              {h}
            </button>
          ))}
          {LEWKA_TAGS.length > FEATURED.length ? (
            <button type="button" className="tag more" onClick={() => setMore((v) => !v)}>
              {more ? "less" : `+${LEWKA_TAGS.length - FEATURED.length}`}
            </button>
          ) : null}
        </div>
        <p className="meta">{note}</p>
      </form>
      {done ? (
        <div className="grid">
          {items.map((item) => (
            <button key={item.id} type="button" className="tile" onClick={() => open(item)}>
              {item.thumb ? <img src={item.thumb} alt="" /> : <div className="ph" />}
              {item.kind === "video" || item.source === "eporner" ? <span className="play">play</span> : null}
              <p>{item.source}</p>
              <h3>{(item.title || item.id).slice(0, 80)}</h3>
            </button>
          ))}
        </div>
      ) : null}
      {active ? <Player item={active} onClose={close} /> : null}
    </div>
  );
}
