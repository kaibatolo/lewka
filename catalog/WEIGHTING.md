# Source catalog weighting

Allowlisted discovery sources live in [`sites.yaml`](./sites.yaml) as **metadata-only cards** (title-like fields, outbound URL, niches, quality scores). lewka never hosts binaries and never treats catalog rows as download mirrors.

## Formula

Source weight used for ranking / search boost:

```
weight = 100 * (
  0.25 * niche_fit +          # computed at query time vs requested niches
  0.20 * signal_to_noise +
  0.20 * age_gate_clarity +
  0.15 * metadata_richness +
  0.15 * indexability +
  0.05 * (1 - spam_risk)
)
```

All static scores are in `[0.0, 1.0]`. Resulting `weight` is in `[0, 100]` (approximately; exact bounds depend on inputs).

### `niche_fit` (query-time)

Given query niches `Q` (e.g. `goth,ffm`) and site niches `S`:

1. Normalize both sets to lowercase stripped tokens.
2. If `Q` is empty → **`niche_fit = 0.5`** (neutral).
3. Else use **simple overlap** (fraction of query niches present on the site):

```
niche_fit = |Q ∩ S| / |Q|
```

Optional Jaccard form (not the default API path, but documented for experiments):

```
niche_fit_jaccard = |Q ∩ S| / |Q ∪ S|
```

Default API / ranking path uses **simple overlap**.

## Hard rules

| Rule | Detail |
|------|--------|
| Stack floor | Product age floor remains **18+**, country-agnostic |
| mina dig lane | May filter catalog to `age_floor >= 21` when that lane is active |
| Age clarity | Reject / `enabled: false` any source failing age-gate clarity expectations |
| Metadata only | Cards + **outbound links** only — no binary fetch/store, no pirate hosts |

Connectors remain separately allowlisted in `app/connectors/registry.py`. Catalog entries boost discovery ranking; they do not auto-enable live scrapers.

## API

`GET /sources?niches=goth,ffm,cuckquean` returns connector stubs plus catalog entries with computed `niche_fit` and `weight`. Omit `niches` for neutral `niche_fit=0.5`.
