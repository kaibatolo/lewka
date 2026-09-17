"""NL → tags expansion stub.

Deterministic keyword extraction; no external LLM required for scaffold.
"""

from __future__ import annotations

import re
from typing import Optional

# Simple adult-safe topical vocabulary for stub expansion
_VOCAB = {
    "romance": ["romance", "romantic", "love", "relationship"],
    "explicit": ["explicit", "nsfw", "erotica", "erotic"],
    "audio": ["audio", "asmr", "podcast", "voice"],
    "video": ["video", "clip", "scene", "footage"],
    "image": ["image", "photo", "illustration", "art"],
    "text": ["story", "fic", "fiction", "prose", "chapter"],
    "bdsm": ["bdsm", "bondage", "dom", "sub"],
    "consent": ["consent", "consensual", "negotiated"],
    "slowburn": ["slowburn", "slow-burn", "slow burn"],
    "oneshot": ["oneshot", "one-shot", "one shot"],
}


def expand_text(text: str, media_type: Optional[str] = None) -> dict:
    lowered = text.lower()
    tags: list[str] = []
    for tag, keywords in _VOCAB.items():
        if any(kw in lowered for kw in keywords):
            tags.append(tag)

    # Token leftovers as soft tags (alphanumeric words length >= 4)
    tokens = re.findall(r"[a-z0-9]{4,}", lowered)
    stop = {"with", "that", "this", "from", "have", "been", "were", "their", "about", "into"}
    for t in tokens:
        if t not in stop and t not in tags and len(tags) < 20:
            # only add if appears in vocab values somewhere or is repeated
            if tokens.count(t) > 1:
                tags.append(t)

    suggested = media_type
    if not suggested:
        if "audio" in tags:
            suggested = "audio"
        elif "video" in tags:
            suggested = "video"
        elif "image" in tags:
            suggested = "image"
        elif "text" in tags or "romance" in tags:
            suggested = "text"

    return {
        "tags": sorted(set(tags)),
        "suggested_media_type": suggested,
        "notes": "stub NL→tags expander; swap for model later",
    }
