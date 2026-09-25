# lewka

This repo **is** Lewka. Search, gallery, catalog, ingest API.

- UI: [`web/`](./web) — vault search + filtered gallery
- API: [`app/`](./app) — FastAPI metadata index (SQLite FTS5)
- Catalog: [`catalog/sites.yaml`](./catalog/sites.yaml)
- Live tiles today: vault edge `GET /v1/search?q=` and `GET /v1/gallery?filter=`

Host intent: `lewka.kaibau.com` or `kaibau.com/lewka` mounting this UI. Not `app.kaibau.com` (that host does not exist).

> Metadata + outbound links only. No binaries. 18+ hard gate. Not a pirate host.

## Web UI

```bash
cd web
npm install
npm run dev
```

Talks to origin:
`https://emeptptdtcgeliiizxry.supabase.co/functions/v1/kaibau`

- `/` search (goth / egirl / ffm / pov / alt)
- `/gallery` lanes `goth white egirl ffm college-slut`

`api.kaibau.com/v1` is 404. Do not use `/v1/gallery/:filter`.

## Local metadata API

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

`GET /health` · `POST /search` · `POST /ingest` · `GET /sources?niches=`

## Policy

18+ only. Age proof on ingest. Allowlisted connectors. No CSAM, no minors, no DRM bypass.
