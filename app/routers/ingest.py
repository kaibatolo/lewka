"""POST /ingest — age-gated metadata ingest via allowlisted connectors."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app import db
from app.connectors.base import ConnectorError
from app.connectors.registry import get_connector
from app.models import IngestRequest, IngestResponse
from app.services.age_gate import AgeGateError, require_adult

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
def ingest(body: IngestRequest) -> IngestResponse:
    connector_name = body.connector or "manual_url"
    try:
        connector = get_connector(connector_name)
        normalized = connector.normalize(body.model_dump())
        # Hard 18+ gate — reject if missing/unclear
        normalized["age_proof"] = require_adult(normalized.get("age_proof"))
    except AgeGateError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except ConnectorError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    # Ensure media_type is string value
    mt = normalized.get("media_type")
    if hasattr(mt, "value"):
        normalized["media_type"] = mt.value

    with db.session() as conn:
        item_id = db.insert_item(conn, normalized)
        item = db.get_item(conn, item_id)

    return IngestResponse(id=item_id, status="ingested", item=item or {})
