"""GET/DELETE /item/{id}."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app import db

router = APIRouter(tags=["items"])


@router.get("/item/{item_id}")
def get_item(item_id: int) -> dict:
    with db.session() as conn:
        item = db.get_item(conn, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="item not found")
    return item


@router.delete("/item/{item_id}")
def delete_item(item_id: int) -> dict:
    with db.session() as conn:
        ok = db.delete_item(conn, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="item not found")
    return {"id": item_id, "status": "deleted"}
