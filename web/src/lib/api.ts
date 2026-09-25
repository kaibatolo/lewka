export const ORIGIN_API =
  "https://emeptptdtcgeliiizxry.supabase.co/functions/v1/kaibau";

export const LANES = ["goth", "white", "egirl", "ffm", "college-slut"] as const;

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

export function search(q: string, limit = 24) {
  const qs = new URLSearchParams({ q, limit: String(limit) });
  return get<{ items?: Item[]; sources?: string[] }>(`/v1/search?${qs}`);
}

export function gallery(filter: string, limit = 24) {
  const qs = new URLSearchParams({ filter, limit: String(limit) });
  return get<{ items?: Item[]; count?: number }>(`/v1/gallery?${qs}`);
}
