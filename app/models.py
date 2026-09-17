"""Pydantic models for lewka API (metadata only)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class MediaType(str, Enum):
    video = "video"
    image = "image"
    text = "text"
    audio = "audio"


class IngestRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    media_type: MediaType
    source: str = Field(..., min_length=1, max_length=100)
    outbound_url: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)
    heat: float = Field(default=0.0, ge=0.0)
    duration_or_length: Optional[str] = None
    thumb_url: Optional[str] = None  # hotlink only
    sample_or_summary: Optional[str] = None
    age_proof: str = Field(..., min_length=1, description="Required 18+ proof / attestation")
    scores: dict[str, Any] = Field(default_factory=dict)
    connector: Optional[str] = Field(
        default=None,
        description="Allowlisted connector name; defaults to manual_url",
    )

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, v: list[str]) -> list[str]:
        return [t.strip().lower() for t in v if t and t.strip()]


class IngestResponse(BaseModel):
    id: int
    status: str = "ingested"
    item: dict[str, Any]


class SearchRequest(BaseModel):
    query: str = ""
    media_type: Optional[MediaType] = None
    source: Optional[str] = None
    tags: Optional[list[str]] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class SearchResponse(BaseModel):
    count: int
    results: list[dict[str, Any]]


class ExpandRequest(BaseModel):
    text: str = Field(..., min_length=1)
    media_type: Optional[MediaType] = None


class ExpandResponse(BaseModel):
    tags: list[str]
    suggested_media_type: Optional[str] = None
    notes: str = ""


class ScoreRequest(BaseModel):
    item_id: Optional[int] = None
    title: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    sample_or_summary: Optional[str] = None
    media_type: Optional[MediaType] = None


class ScoreResponse(BaseModel):
    scores: dict[str, Any]
    rubric_version: str
    item_id: Optional[int] = None
    persisted: bool = False


class CritiqueRequest(BaseModel):
    item_id: Optional[int] = None
    notes: str = ""
    focus: Optional[list[str]] = None
    payload: dict[str, Any] = Field(default_factory=dict)


class CritiqueResponse(BaseModel):
    critique_id: int
    status: str
    message: str


class SourceOut(BaseModel):
    id: int
    name: str
    connector: str
    description: Optional[str] = None
    allowlisted: int
    created_at: str


class HealthResponse(BaseModel):
    status: str
    service: str = "lewka"
    policy: str = "metadata-only; 18+ gated; allowlisted connectors"


class CatalogEntryOut(BaseModel):
    id: str
    name: str
    url: str
    kinds: list[str]
    niches: list[str]
    age_floor: int
    age_gate_clarity: float
    signal_to_noise: float
    metadata_richness: float
    indexability: float
    spam_risk: float
    notes: str = ""
    enabled: bool = True
    niche_fit: float
    weight: float


class SourcesResponse(BaseModel):
    connectors: list[SourceOut]
    catalog: list[CatalogEntryOut]
