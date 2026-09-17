# kaibau-gateway

OpenAI-compatible Cloudflare Worker for the kaibau.com lewd gateway.

Routes model IDs to upstream APIs:

| Client model prefix | Upstream | Secret |
|---------------------|----------|--------|
| `venice/*` `venice-*` | Venice AI | `VENICE_API_KEY` |
| `featherless/*` `featherless-*` | Featherless | `FEATHERLESS_API_KEY` |
| `grok/*` `grok-*` | xAI Grok | `XAI_API_KEY` |

Always injects 18+ / no-minors hard rules. Accepts `X-User-Id` / `X-Agent-Id` (or body `metadata`) for session tagging and optional Supabase memory recall stub.

## Endpoints

- `GET /v1/models`
- `POST /v1/chat/completions` (OpenAI-compatible; streaming passthrough supported)
- `GET /health`

## Local setup

```bash
cd kaibau-gateway   # or gateway/ if cloned from lewka
npm install
cp .dev.vars.example .dev.vars
# fill .dev.vars — never commit it
npx wrangler dev
```

## Deploy secrets (never commit real values)

```bash
npx wrangler secret put VENICE_API_KEY
npx wrangler secret put FEATHERLESS_API_KEY
npx wrangler secret put XAI_API_KEY
# optional memory
npx wrangler secret put SUPABASE_URL
npx wrangler secret put SUPABASE_SERVICE_ROLE
```

Missing provider keys return **503** with a clear `provider_not_configured` message.

## Deploy Worker

```bash
npx wrangler deploy
```

Requires a Cloudflare API token with **Workers Scripts:Edit** (and Account read). An R2-only token will fail deploy.

Account ID is read from `CLOUDFLARE_ACCOUNT_ID` or wrangler login / `wrangler.toml` `[account_id]` if you add it locally (do not commit secrets).

## Custom domain: api.kaibau.com

1. In Cloudflare Dashboard → Workers & Pages → **kaibau-gateway** → Triggers → Custom Domains → add `api.kaibau.com`.
2. Or uncomment `routes` in `wrangler.toml` and redeploy (zone must be `kaibau.com` on the same account).
3. DNS: ensure `api` is proxied (orange cloud) on zone **kaibau.com`.

## Example request

```bash
curl -s https://api.kaibau.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user_123" \
  -H "X-Agent-Id: agent_abc" \
  -d '{
    "model": "venice/llama-3.3-70b",
    "messages": [{"role":"user","content":"Hello"}],
    "stream": false
  }'
```

## R2 (optional)

Account R2 bucket `kaiba-vault` exists for agent memory/config objects. Uncomment the `[[r2_buckets]]` block in `wrangler.toml` to bind as `VAULT` when you need object storage from the Worker.

## Memory stub

If `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE` are set, the Worker tries:

1. RPC `lewka_search_pages`
2. Fallback table `memories`

Failures are soft (empty recall). Safe to leave unset.

## Security

- Never commit API tokens, `.dev.vars`, or `.env` files.
- Use `wrangler secret put` for production.
- Hard rules always prepend: 18+ only, no minors, per-agent no-repeat note.
