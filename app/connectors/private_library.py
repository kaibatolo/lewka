"""Private library connector — local catalog metadata import (no binaries)."""

from __future__ import annotations

from typing import Any

from app.connectors.base import BaseConnector, ConnectorError


class PrivateLibraryConnector(BaseConnector):
    name = "private_library"

    def normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        title = (payload.get("title") or "").strip()
        outbound = (payload.get("outbound_url") or payload.get("path_ref") or "").strip()
        if not title:
            raise ConnectorError("private_library requires title")
        if not outbound:
            raise ConnectorError("private_library requires outbound_url or path_ref (reference only)")

        # Explicitly refuse binary fields if someone tries to sneak them in
        for banned in ("file_bytes", "binary", "content_base64", "video_data", "image_data"):
            if banned in payload:
                raise ConnectorError(f"media binaries not allowed ({banned}); metadata only")

        return {
            "title": title,
            "media_type": payload.get("media_type") or "video",
            "source": payload.get("source") or "private_library",
            "outbound_url": outbound,
            "tags": payload.get("tags") or [],
            "heat": float(payload.get("heat") or 0.0),
            "duration_or_length": payload.get("duration_or_length"),
            "thumb_url": payload.get("thumb_url"),
            "sample_or_summary": payload.get("sample_or_summary"),
            "age_proof": payload.get("age_proof"),
            "scores": payload.get("scores") or {},
        }
