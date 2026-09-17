"""AO3 class stub normalizer — no live scrape.

Accepts already-fetched or manually pasted AO3-shaped metadata and
normalizes to lewka item fields. Does NOT fetch pages or download media.
"""

from __future__ import annotations

from typing import Any

from app.connectors.base import BaseConnector, ConnectorError


class Ao3ClassConnector(BaseConnector):
    name = "ao3_class"

    def normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        title = (payload.get("title") or payload.get("work_title") or "").strip()
        outbound = (payload.get("outbound_url") or payload.get("url") or "").strip()
        if not title:
            raise ConnectorError("AO3 stub requires title/work_title")
        if not outbound:
            raise ConnectorError("AO3 stub requires outbound_url")

        tags = list(payload.get("tags") or [])
        for key in ("fandoms", "warnings", "categories", "additional_tags"):
            extra = payload.get(key) or []
            if isinstance(extra, str):
                tags.append(extra)
            else:
                tags.extend(list(extra))

        rating = (payload.get("rating") or "").lower()
        age_proof = payload.get("age_proof")
        if not age_proof and ("explicit" in rating or "mature" in rating):
            age_proof = "18+ attested via AO3 rating (stub)"

        summary = payload.get("sample_or_summary") or payload.get("summary")
        words = payload.get("words") or payload.get("duration_or_length")
        if words is not None and not isinstance(words, str):
            words = f"{words} words"

        return {
            "title": title,
            "media_type": payload.get("media_type") or "text",
            "source": payload.get("source") or "ao3",
            "outbound_url": outbound,
            "tags": tags,
            "heat": float(payload.get("heat") or 0.0),
            "duration_or_length": words,
            "thumb_url": payload.get("thumb_url"),
            "sample_or_summary": summary,
            "age_proof": age_proof,
            "scores": payload.get("scores") or {},
        }
