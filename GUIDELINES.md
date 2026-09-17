# lewka Guidelines

## 18+ (country-agnostic)

- Every ingest path must supply a clear `age_proof` string affirming adult status.
- Missing, empty, `unknown`, `n/a`, `unverified`, or underage-coded values are **hard rejected**.
- This gate is **country-agnostic**: we do not encode jurisdiction-specific age numbers beyond the global 18+ floor. Local operators may add stricter overlays; they must not lower the floor.
- Connectors may map platform signals (e.g. AO3 Explicit/Mature, Reddit `over_18`) into an explicit attestation string — still subject to the same gate.

## Consent / quality — muli review lane

- Prefer tags and summaries that surface **consent**, negotiation, and clear adult framing.
- The stub scorer exposes a `consent_signal` field for the future **muli** review lane (human + model quality pass).
- Critique requests (`POST /critique`) are stored for that lane; they do **not** auto-publish or fetch binaries.
- Quality rubric dimensions (stub): `quality`, `heat_proxy`, `consent_signal`, `clarity`, `tag_richness`.

## Venice hard-fail headers (when wired later)

When a Venice (or similar) critique/scoring backend is connected, requests **must** include and backends **must** honor these hard-fail semantics:

| Header | Value | Meaning |
|--------|-------|---------|
| `X-Lewka-Age-Gate` | `required` | Refuse if age attestation absent/unclear |
| `X-Lewka-Consent-Lane` | `muli` | Route through muli consent/quality lane |
| `X-Lewka-No-Binary` | `1` | Never request or accept media binaries |
| `X-Lewka-Allowlist-Only` | `1` | Only allowlisted connectors/sources |

Hard-fail behavior: if any required header is missing or violated, the remote call must fail closed (no partial critique write-back that bypasses age/consent policy).

Until Venice is wired, `POST /critique` only persists a pending request and records these headers as reserved metadata.

## Not a pirate host

- No torrent/magnet ingestion as a binary delivery path.
- No DRM circumvention helpers.
- No open-web crawl connectors in the allowlist.
- Outbound URLs are references; lewka stores metadata and hotlinked thumbs only.

## Connector rules

1. Normalize to lewka metadata schema only.
2. Call age gate before emit.
3. Reject payloads containing binary fields (`file_bytes`, `content_base64`, etc.).
4. New connectors require explicit registry allowlisting.
