"""POST /expand — NL → tags stub."""

from __future__ import annotations

from fastapi import APIRouter

from app.models import ExpandRequest, ExpandResponse
from app.services.expand import expand_text

router = APIRouter(tags=["expand"])


@router.post("/expand", response_model=ExpandResponse)
def expand(body: ExpandRequest) -> ExpandResponse:
    mt = body.media_type.value if body.media_type else None
    result = expand_text(body.text, media_type=mt)
    return ExpandResponse(**result)
