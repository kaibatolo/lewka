import { epornerApi, rule34 } from "./native";

export const ORIGIN_API =
  "https://emeptptdtcgeliiizxry.supabase.co/functions/v1/kaibau";

export const LANES = ["goth", "white", "egirl", "ffm", "college-slut"] as const;
export const SOURCE_CAP = 0.2;

export type Item = {
  id: string;
  source: string;
  kind?: string;
  title?: string;
  url: string;
  thumb?: string;
  filter_key?: string;
};

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${ORIGIN_API}${path}`, { headers: { accept: "application/json" } });
  const text = await res.text();
  const data = text ? JSON.parse(text) : {};
  if (!res.ok) {
    const err = data.error;
    throw new Error((typeof err === "string" ? err : err?.message) || data.message || `${res.status} ${path}`);
  }
  return data as T;
}

export function sources() {
  return get<{ sources?: string[] }>("/v1/sources");
}

export function search(q: string, limit = 80, source?: string) {
  const qs = new URLSearchParams({ q, limit: String(limit) });
  if (source) qs.set("source", source);
  return get<{ items?: Item[]; sources?: string[] }>(`/v1/search?${qs}`);
}

export function gallery(filter: string, limit = 80) {
  const qs = new URLSearchParams({ filter, limit: String(limit) });
  return get<{ items?: Item[]; count?: number }>(`/v1/gallery?${qs}`);
}

export function federate(items: Item[], limit = 24, cap = SOURCE_CAP): Item[] {
  const buckets = new Map<string, Item[]>();
  for (const item of items) {
    const key = (item.source || "unknown").toLowerCase();
    const list = buckets.get(key) || [];
    list.push(item);
    buckets.set(key, list);
  }
  const maxEach = Math.max(1, Math.floor(limit * cap));
  const queues = [...buckets.values()].map((list) => list.slice(0, maxEach));
  const out: Item[] = [];
  let added = true;
  while (out.length < limit && added) {
    added = false;
    for (const q of queues) {
      if (!q.length || out.length >= limit) continue;
      out.push(q.shift() as Item);
      added = true;
    }
  }
  return out;
}

export async function federatedSearch(q: string, limit = 24) {
  const listed = await sources().catch(() => ({ sources: ["danbooru", "eporner"] }));
  const names = [...new Set([...(listed.sources || []), "rule34"])];
  const pages = await Promise.all([
    ...names.map((name) => search(q, Math.max(40, limit * 2), name).catch(() => ({ items: [] as Item[] }))),
    rule34(q, 24).then((items) => ({ items })).catch(() => ({ items: [] as Item[] })),
    epornerApi(q, 24).then((items) => ({ items })).catch(() => ({ items: [] as Item[] })),
  ]);
  const pool: Item[] = [];
  const seen = new Set<string>();
  for (const page of pages) {
    for (const item of page.items || []) {
      if (!item?.id || seen.has(item.id)) continue;
      seen.add(item.id);
      pool.push(item);
    }
  }
  return {
    items: federate(pool, limit),
    sources: [...new Set(pool.map((i) => i.source))],
    pooled: pool.length,
  };
}
