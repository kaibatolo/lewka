"""GET /sources — allowlisted connectors + weighted site catalog."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from app import db
from app.connectors.registry import list_connectors
from app.models import CatalogEntryOut, SourceOut, SourcesResponse
from app.services.catalog import parse_niches_param, weighted_catalog

router = APIRouter(tags=["sources"])


@router.get("/sources", response_model=SourcesResponse)
def sources(
    niches: Optional[str] = Query(
        default=None,
        description="Comma-separated niches for weight boost, e.g. goth,ffm,cuckquean",
    ),
) -> SourcesResponse:
    with db.session() as conn:
        rows = db.list_sources(conn)
    # Keep registry visibility (stubs stay wired)
    _ = set(list_connectors())
    connectors = [SourceOut(**r) for r in rows]

    niche_list = parse_niches_param(niches)
    catalog_rows = weighted_catalog(niche_list)
    catalog = [CatalogEntryOut(**row) for row in catalog_rows]
    return SourcesResponse(connectors=connectors, catalog=catalog)
