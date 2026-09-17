"""POST /critique — stub: store critique request; do not call real Venice."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app import db
from app.models import CritiqueRequest, CritiqueResponse

router = APIRouter(tags=["critique"])


@router.post("/critique", response_model=CritiqueResponse)
def critique(body: CritiqueRequest) -> CritiqueResponse:
    if body.item_id is not None:
        with db.session() as conn:
            item = db.get_item(conn, body.item_id)
            if not item:
                raise HTTPException(status_code=404, detail="item not found")

    payload = {
        "notes": body.notes,
        "focus": body.focus or [],
        **(body.payload or {}),
        # Venice hard-fail headers reserved for when wired later (see GUIDELINES.md)
        "venice_headers_reserved": {
            "X-Lewka-Age-Gate": "required",
            "X-Lewka-Consent-Lane": "muli",
            "X-Lewka-No-Binary": "1",
        },
    }

    with db.session() as conn:
        critique_id = db.insert_critique(conn, body.item_id, payload)

    return CritiqueResponse(
        critique_id=critique_id,
        status="pending",
        message="critique request stored; Venice not called (stub)",
    )
