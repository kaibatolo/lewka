"""Quality scoring rubric stub for lewka.

Produces a scores JSON dict. Not a live LLM call — deterministic stub.
"""

from __future__ import annotations

from typing import Any, Optional

RUBRIC_VERSION = "lewka-rubric-0.1-stub"


def score_item(
    *,
    title: Optional[str] = None,
    tags: Optional[list[str]] = None,
    sample_or_summary: Optional[str] = None,
    media_type: Optional[str] = None,
) -> dict[str, Any]:
    tags = tags or []
    title = title or ""
    sample = sample_or_summary or ""

    # Stub heuristic: tag richness, title length, sample presence
    tag_score = min(1.0, len(tags) / 8.0)
    title_score = min(1.0, len(title.strip()) / 40.0)
    sample_score = 0.8 if len(sample.strip()) > 40 else (0.4 if sample.strip() else 0.1)
    type_bonus = 0.05 if media_type else 0.0

    quality = round(min(1.0, 0.35 * tag_score + 0.25 * title_score + 0.35 * sample_score + type_bonus), 3)
    heat_proxy = round(min(1.0, tag_score * 0.6 + sample_score * 0.4), 3)
    consent_signal = 0.7 if any("consent" in t.lower() for t in tags) else 0.5
    clarity = round(min(1.0, title_score * 0.5 + sample_score * 0.5), 3)

    return {
        "quality": quality,
        "heat_proxy": heat_proxy,
        "consent_signal": consent_signal,
        "clarity": clarity,
        "tag_richness": round(tag_score, 3),
        "rubric": RUBRIC_VERSION,
        "notes": "stub rubric; replace with Venice/muli lane later",
    }
