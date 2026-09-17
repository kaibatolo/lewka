# lewka

Private **index + quality layer** for adult media. **Metadata only** — title, type, source, outbound URL, tags, heat, duration/length, thumb hotlink, sample/summary, age proof, scores JSON, timestamps.

> **Not a pirate host.** lewka does not download or store media binaries (no video/image/audio files on disk). No DRM bypass. No open-web crawl. Allowlisted connectors only.

## Requirements

- Python 3.10+
- SQLite (stdlib) with FTS5

## Install

```bash
cd /workspace/lewka
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
cd /workspace/lewka
source .venv/bin/activate   # if not already
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- OpenAPI docs: http://127.0.0.1:8000/docs
- Health: `GET /health`

## Policy (hard)

| Rule | Detail |
|------|--------|
| Metadata only | Store fields listed above; `thumb_url` is hotlink-only |
| No binaries | Never download or persist video/image/audio/text bodies as files |
| 18+ gate | Every `POST /ingest` rejects if `age_proof` is missing or unclear |
| Allowlisted connectors | `manual_url`, `ao3_class` (stub), `private_library`, `reddit_nsfw` (stub) |
| Not a pirate host | Index + quality layer; outbound links only |

See [GUIDELINES.md](./GUIDELINES.md) for consent/quality (muli) notes and Venice hard-fail headers.

## API

| Method | Path | Notes |
|--------|------|-------|
| POST | `/ingest` | Age-gated metadata ingest |
| POST | `/search` | FTS5 + filters |
| GET | `/item/{id}` | Fetch one item |
| DELETE | `/item/{id}` | Delete metadata row |
| GET | `/sources` | Connectors + weighted catalog (`?niches=goth,ffm`) |
| POST | `/expand` | NL → tags stub |
| POST | `/score` | Rubric stub; optional persist |
| POST | `/critique` | Store critique request (no Venice call) |
| GET | `/health` | Liveness |

### Example ingest

```bash
curl -s -X POST http://127.0.0.1:8000/ingest -H 'Content-Type: application/json' -d '{
  "title": "Example Adult Work",
  "media_type": "text",
  "source": "manual",
  "outbound_url": "https://example.com/work/1",
  "tags": ["romance", "consent"],
  "sample_or_summary": "Consensual adult fiction sample.",
  "age_proof": "18+ attested by submitter",
  "connector": "manual_url"
}'
```


## Site catalog + weighting

Allowlisted adult discovery sources live in [`catalog/sites.yaml`](./catalog/sites.yaml) (mina-ranked seed for goth/egirl/FFM/cuckquean). Ranking boost formula and hard rules are documented in [`catalog/WEIGHTING.md`](./catalog/WEIGHTING.md).

`GET /sources?niches=goth,ffm,cuckquean` returns connector stubs plus catalog cards with computed `niche_fit` and `weight`. Metadata + outbound links only.

## Tests

```bash
cd /workspace/lewka
source .venv/bin/activate
PYTHONPATH=/workspace/lewka pytest -q
```

## Media types

`video` | `image` | `text` | `audio`

## Disclaimer

Adult content (18+) only. Operators are responsible for local law compliance. lewka is a private metadata index, not a content host or piracy tool.
