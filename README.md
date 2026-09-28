# lewka

This repo **is** Lewka. Search, gallery, catalog, ingest API.

Public host: **https://lewka.kaibau.com**

Cloudflare project: **kaibau-lewka** (Workers & Pages). Git: `kaibatolo/lewka`. Root directory: `/web`.

- UI: [`web/`](./web) — vault search + filtered gallery
- API: [`app/`](./app) — FastAPI metadata index (SQLite FTS5)
- Catalog: [`catalog/sites.yaml`](./catalog/sites.yaml)
- Live tiles: vault edge `GET /v1/search?q=` and `GET /v1/gallery?filter=`

`app.kaibau.com` does not exist. Do not link it. Marketing `kaibau.com/lewka` is a bounce to this host, not the product.

> Metadata + outbound links only. No binaries. 18+ hard gate. Not a pirate host.

## Web UI

```bash
cd web
npm install
npm run dev
```

Talks to origin:
`https://emeptptdtcgeliiizxry.supabase.co/functions/v1/kaibau`

- `/` search (placeholder **lewka search**, CTA **Open Lewka**)
- `/gallery` lanes `goth white egirl ffm college-slut`

`api.kaibau.com/v1` is 404. Do not use `/v1/gallery/:filter`.

## Deploy (lewka.kaibau.com)

`web/wrangler.jsonc` name is `kaibau-lewka` so it matches the dashboard Worker. Custom domain `lewka.kaibau.com`.

Dashboard Builds should be:

| Field | Value |
| --- | --- |
| Git repository | `kaibatolo/lewka` |
| Root directory | `/web` |
| Branch | `main` |
| Build command | `npm ci && npm run build` |
| Deploy command | `npx wrangler deploy` |

Build command cannot stay `None` — `wrangler deploy` ships `web/dist`. No dist, empty Worker.

```bash
cd web
npm install
npm run deploy
```

## Local metadata API

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

`GET /health` · `POST /search` · `POST /ingest` · `GET /sources?niches=`

## Policy

18+ only. Age proof on ingest. Allowlisted connectors. No CSAM, no minors, no DRM bypass.
