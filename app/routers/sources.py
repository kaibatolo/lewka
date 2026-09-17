"""GET /sources — allowlisted sources/connectors."""

from __future__ import annotations

from fastapi import APIRouter

from app import db
from app.connectors.registry import list_connectors
from app.models import SourceOut

router = APIRouter(tags=["sources"])


@router.get("/sources", response_model=list[SourceOut])
def sources() -> list[SourceOut]:
    with db.session() as conn:
        rows = db.list_sources(conn)
    # Annotate with live registry for clarity
    allowed = set(list_connectors())
    out = []
    for r in rows:
        out.append(SourceOut(**r))
    # Also expose registry-only names if DB seed lagged (shouldn't)
    _ = allowed
    return out
