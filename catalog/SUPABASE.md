# lewka_search_pages (kaiba-vault)

Searchable tagged **page index** for the lewka adult aggregation stack. Lives in Supabase project **kaiba-vault** (`emeptptdtcgeliiizxry`). **Metadata and outbound links only** — no media binaries.

## Table

`public.lewka_search_pages`

| Column | Type | Notes |
|--------|------|--------|
| `id` | text PK | Slug (e.g. `mygothgf`, `tpd-goth`) |
| `title` | text | Display name |
| `url` | text unique | Outbound / discovery URL |
| `kind` | text | `site` \| `directory` \| `category` \| `search_engine` \| `lookup` \| `creator_platform` \| `studio` \| `audio` \| `text` |
| `tags` | text[] | Exactly 5–8 lowercase kebab/simple tags |
| `niches` | text[] | Niche facets (may overlap tags) |
| `age_floor` | int ≥ 18 | Prefer **21** for mina-lane goth/egirl/FFM/cuckquean pages |
| `enabled` | bool | Soft-exclude spam farms with `false` |
| `weight_hint` | numeric | Optional static 0–100 ranking hint |
| `spam_risk` | numeric | Default 0.3; high farms ≥ ~0.7 |
| `notes` | text | Curator notes |
| `source` | text | `lewka` \| `porndude` \| `user` |
| `payload` | jsonb | Extra catalog signals (S/N, indexability, …) |
| `created_at` / `updated_at` | timestamptz | |

**RLS:** enabled, no public/anon policies (service role / dashboard / MCP only — private vault).

**Indexes:** GIN on `tags`, GIN on `niches`; btree on `enabled`, `kind`.

Migration name: `create_lewka_search_pages`.

## Seed sources

1. Enabled (and soft-disabled spam) sites from [`sites.yaml`](./sites.yaml) → `source = lewka`.
2. ThePornDude home + ~30 category/discovery pages → mostly `source = porndude`.
3. Lewka synthetic directories for goth studios / FFM+cuckquean / audio / creators.

Mina dig-aligned tags (use when fitting among the 5–8): **goth, egirl, ffm, cuckquean, jealous, mean, alt, pov**. Biased onto BurningAngel, MyGothGF, Clips4Sale, ManyVids, MissaX, Audiodesires, Fansly, Perfect Girlfriend, and goth/FFM/cuckquean category pages.

Hard excludes: CSAM, "teen" niche pages, extreme gore, revenge/doxxing.

## How mina / muli query it

Use the Supabase JS/Python client with the **service role** key (vault is RLS-locked).

### Tag / niche discovery (mina dig)

```sql
-- Pages matching any mina dig tags, enabled, age-safe
SELECT id, title, url, kind, tags, niches, weight_hint, spam_risk
FROM public.lewka_search_pages
WHERE enabled = true
  AND age_floor >= 18
  AND (
    tags && ARRAY['goth','egirl','ffm','cuckquean','jealous','mean','alt','pov']
    OR niches && ARRAY['goth','egirl','ffm','cuckquean','alt']
  )
ORDER BY weight_hint DESC NULLS LAST, spam_risk ASC
LIMIT 40;
```

### Single niche (e.g. goth)

```sql
SELECT id, title, url, tags, niches, weight_hint
FROM public.lewka_search_pages
WHERE enabled
  AND ('goth' = ANY(tags) OR 'goth' = ANY(niches))
ORDER BY weight_hint DESC NULLS LAST
LIMIT 20;
```

### Kind filter (studios + creator platforms for ranking)

```sql
SELECT id, title, url, kind, tags, weight_hint
FROM public.lewka_search_pages
WHERE enabled
  AND kind IN ('studio','creator_platform','audio','text','lookup')
  AND spam_risk < 0.5
ORDER BY weight_hint DESC NULLS LAST;
```

### Client sketch (Python)

```python
from supabase import create_client
sb = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)
res = (
    sb.table("lewka_search_pages")
    .select("id,title,url,kind,tags,niches,weight_hint,spam_risk")
    .eq("enabled", True)
    .overlaps("tags", ["goth", "egirl", "ffm", "cuckquean"])
    .order("weight_hint", desc=True)
    .limit(40)
    .execute()
)
# mina: boost cards by niche_fit × (1 - spam_risk) × weight_hint
# muli: same rows as quality/consent critique targets — outbound only, no media fetch
```

Local lewka still uses SQLite FTS for **items**; this table is the **page/site discovery index** synced to kaiba-vault for cross-agent (mina/muli) search. Prefer `enabled=true` and low `spam_risk`; never ingest per-clip URLs as sources.

## Ops

- DDL: MCP `apply_migration` (or SQL editor).
- Upserts: MCP `execute_sql` / service role.
- Re-seed from catalog: regenerate from `sites.yaml` + category list, then `INSERT … ON CONFLICT (id) DO UPDATE`.
