"""Reddit NSFW connector stub — allowlisted only, no live crawl.

Normalizes pasted Reddit-shaped metadata. Does not call Reddit APIs
in this scaffold (avoids open-web crawl).
"""

from __future__ import annotations

from typing import Any

from app.connectors.base import BaseConnector, ConnectorError


class RedditNsfwConnector(BaseConnector):
    name = "reddit_nsfw"

    def normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        title = (payload.get("title") or "").strip()
        outbound = (payload.get("outbound_url") or payload.get("permalink") or "").strip()
        if not title:
            raise ConnectorError("reddit_nsfw stub requires title")
        if not outbound:
            raise ConnectorError("reddit_nsfw stub requires outbound_url/permalink")

        over18 = payload.get("over_18") or payload.get("over18")
        age_proof = payload.get("age_proof")
        if not age_proof and over18 in (True, "true", "1", 1):
            age_proof = "18+ attested via Reddit over_18 flag (stub)"

        tags = list(payload.get("tags") or [])
        sub = payload.get("subreddit")
        if sub:
            tags.append(f"r/{sub.lstrip('/')}")

        return {
            "title": title,
            "media_type": payload.get("media_type") or "image",
            "source": payload.get("source") or "reddit_nsfw",
            "outbound_url": outbound,
            "tags": tags,
            "heat": float(payload.get("heat") or payload.get("score") or 0.0),
            "duration_or_length": payload.get("duration_or_length"),
            "thumb_url": payload.get("thumb_url") or payload.get("thumbnail"),
            "sample_or_summary": payload.get("sample_or_summary") or payload.get("selftext"),
            "age_proof": age_proof,
            "scores": payload.get("scores") or {},
        }
