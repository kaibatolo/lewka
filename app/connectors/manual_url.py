"""Manual URL / paste connector — metadata only."""

from __future__ import annotations

from typing import Any

from app.connectors.base import BaseConnector, ConnectorError


class ManualUrlConnector(BaseConnector):
    name = "manual_url"

    def normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        title = (payload.get("title") or "").strip()
        outbound = (payload.get("outbound_url") or "").strip()
        media_type = payload.get("media_type")
        if not title:
            raise ConnectorError("title required")
        if not outbound:
            raise ConnectorError("outbound_url required")
        if not media_type:
            raise ConnectorError("media_type required")

        return {
            "title": title,
            "media_type": media_type if isinstance(media_type, str) else str(media_type),
            "source": payload.get("source") or "manual",
            "outbound_url": outbound,
            "tags": payload.get("tags") or [],
            "heat": float(payload.get("heat") or 0.0),
            "duration_or_length": payload.get("duration_or_length"),
            "thumb_url": payload.get("thumb_url"),  # hotlink only
            "sample_or_summary": payload.get("sample_or_summary"),
            "age_proof": payload.get("age_proof"),
            "scores": payload.get("scores") or {},
        }
