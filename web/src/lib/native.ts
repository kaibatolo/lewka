import type { Item } from "./api";

const BLOCK = /\b(loli|shota|child|underage|preteen|young.?girl)\b/i;

function clean(items: Item[]) {
  return items.filter((item) => !BLOCK.test(`${item.title || ""} ${item.id}`));
}

export async function rule34(q: string, limit = 20): Promise<Item[]> {
  const url = `https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&limit=${limit}&tags=${encodeURIComponent(q)}`;
  const res = await fetch(url);
  if (!res.ok) return [];
  const rows = (await res.json()) as Array<{ id: number; file_url?: string; sample_url?: string; preview_url?: string; tags?: string }>;
  return clean(
    (rows || []).map((row) => ({
      id: `rule34:${row.id}`,
      source: "rule34",
      kind: "image",
      title: q,
      url: row.file_url || row.sample_url || "",
      thumb: row.preview_url || row.sample_url,
    })),
  );
}

export async function epornerApi(q: string, limit = 20): Promise<Item[]> {
  const url = `https://www.eporner.com/api/v2/video/search/?query=${encodeURIComponent(q)}&per_page=${limit}&format=json&order=latest`;
  const res = await fetch(url);
  if (!res.ok) return [];
  const data = (await res.json()) as {
    videos?: Array<{ id?: string; title?: string; url?: string; default_thumb?: { src?: string }; embed?: string }>;
  };
  return clean(
    (data.videos || []).map((row) => ({
      id: `eporner:${row.id || row.url}`,
      source: "eporner",
      kind: "video",
      title: row.title,
      url: row.url || "",
      thumb: row.default_thumb?.src,
    })),
  );
}
