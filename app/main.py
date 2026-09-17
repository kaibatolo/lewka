"""lewka FastAPI application — private adult-content metadata aggregation.

METADATA ONLY. No media binaries. 18+ hard gate on ingest.
Allowlisted connectors only. Not a pirate host.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import db
from app.models import HealthResponse
from app.routers import critique, expand, ingest, items, score, search, sources


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db.init_db()
    yield


app = FastAPI(
    title="lewka",
    description=(
        "Private index + quality layer for adult media (metadata only). "
        "18+ gated. Allowlisted connectors. Not a pirate host — no binary storage, "
        "no DRM bypass, no open-web crawl."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(ingest.router)
app.include_router(search.router)
app.include_router(items.router)
app.include_router(sources.router)
app.include_router(expand.router)
app.include_router(score.router)
app.include_router(critique.router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    return HealthResponse(status="ok")
