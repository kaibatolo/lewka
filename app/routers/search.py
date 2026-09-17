"""POST /search — FTS5 + filter search over metadata."""

from __future__ import annotations

from fastapi import APIRouter

from app import db
from app.models import SearchRequest, SearchResponse

router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
def search(body: SearchRequest) -> SearchResponse:
    media_type = body.media_type.value if body.media_type else None
    with db.session() as conn:
        results = db.search_items(
            conn,
            query=body.query or "",
            media_type=media_type,
            source=body.source,
            tags=body.tags,
            limit=body.limit,
            offset=body.offset,
        )
    return SearchResponse(count=len(results), results=results)
