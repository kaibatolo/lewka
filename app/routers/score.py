"""POST /score — quality rubric stub; optionally persist to item."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app import db
from app.models import ScoreRequest, ScoreResponse
from app.services.scoring import RUBRIC_VERSION, score_item

router = APIRouter(tags=["score"])


@router.post("/score", response_model=ScoreResponse)
def score(body: ScoreRequest) -> ScoreResponse:
    title = body.title
    tags = body.tags
    sample = body.sample_or_summary
    media_type = body.media_type.value if body.media_type else None
    item_id = body.item_id
    persisted = False

    if item_id is not None:
        with db.session() as conn:
            item = db.get_item(conn, item_id)
            if not item:
                raise HTTPException(status_code=404, detail="item not found")
            title = title or item.get("title")
            tags = tags or item.get("tags") or []
            sample = sample or item.get("sample_or_summary")
            media_type = media_type or item.get("media_type")
            scores = score_item(
                title=title, tags=tags, sample_or_summary=sample, media_type=media_type
            )
            db.update_item_scores(conn, item_id, scores)
            persisted = True
    else:
        scores = score_item(
            title=title, tags=tags, sample_or_summary=sample, media_type=media_type
        )

    return ScoreResponse(
        scores=scores,
        rubric_version=RUBRIC_VERSION,
        item_id=item_id,
        persisted=persisted,
    )
