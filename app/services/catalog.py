"""Load catalog/sites.yaml and compute source weights for ranking boost."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Optional

import yaml

CATALOG_PATH = Path(__file__).resolve().parents[2] / "catalog" / "sites.yaml"

# Coefficients from catalog/WEIGHTING.md
_W_NICHE = 0.25
_W_SIGNAL = 0.20
_W_AGE = 0.20
_W_META = 0.15
_W_INDEX = 0.15
_W_SPAM = 0.05

AGE_GATE_CLARITY_MIN = 0.50  # below this → treat as failing age clarity


def niche_fit(query_niches: Iterable[str], site_niches: Iterable[str]) -> float:
    """Fraction of query niches present in site.niches; 0.5 if query empty."""
    q = {n.strip().lower() for n in query_niches if n and str(n).strip()}
    if not q:
        return 0.5
    s = {n.strip().lower() for n in site_niches if n and str(n).strip()}
    return len(q & s) / len(q)


def niche_fit_jaccard(query_niches: Iterable[str], site_niches: Iterable[str]) -> float:
    """Optional Jaccard niche_fit for experiments."""
    q = {n.strip().lower() for n in query_niches if n and str(n).strip()}
    s = {n.strip().lower() for n in site_niches if n and str(n).strip()}
    if not q and not s:
        return 0.5
    union = q | s
    if not union:
        return 0.5
    return len(q & s) / len(union)


def compute_weight(
    *,
    niche_fit_value: float,
    signal_to_noise: float,
    age_gate_clarity: float,
    metadata_richness: float,
    indexability: float,
    spam_risk: float,
) -> float:
    """Return 0–100 weight per WEIGHTING.md formula."""
    raw = (
        _W_NICHE * niche_fit_value
        + _W_SIGNAL * signal_to_noise
        + _W_AGE * age_gate_clarity
        + _W_META * metadata_richness
        + _W_INDEX * indexability
        + _W_SPAM * (1.0 - spam_risk)
    )
    return round(100.0 * raw, 4)


def _validate_site(raw: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Normalize one site row; return None if disabled or fails age clarity."""
    if not raw.get("enabled", True):
        return None
    clarity = float(raw.get("age_gate_clarity", 0.0))
    if clarity < AGE_GATE_CLARITY_MIN:
        return None
    return {
        "id": str(raw["id"]),
        "name": str(raw["name"]),
        "url": str(raw["url"]),
        "kinds": list(raw.get("kinds") or []),
        "niches": [str(n).lower() for n in (raw.get("niches") or [])],
        "age_floor": int(raw.get("age_floor", 18)),
        "age_gate_clarity": clarity,
        "signal_to_noise": float(raw.get("signal_to_noise", 0.0)),
        "metadata_richness": float(raw.get("metadata_richness", 0.0)),
        "indexability": float(raw.get("indexability", 0.0)),
        "spam_risk": float(raw.get("spam_risk", 0.0)),
        "notes": str(raw.get("notes") or ""),
        "enabled": True,
    }


@lru_cache(maxsize=1)
def load_sites(path: Optional[str] = None) -> list[dict[str, Any]]:
    """Load enabled, age-clarity-passing sites from YAML."""
    p = Path(path) if path else CATALOG_PATH
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    sites_raw = data.get("sites") or []
    out: list[dict[str, Any]] = []
    for raw in sites_raw:
        site = _validate_site(raw)
        if site:
            out.append(site)
    return out


def clear_catalog_cache() -> None:
    load_sites.cache_clear()


def weighted_catalog(
    niches: Optional[Iterable[str]] = None,
    *,
    age_floor_min: Optional[int] = None,
    path: Optional[str] = None,
) -> list[dict[str, Any]]:
    """
    Return catalog entries with niche_fit + weight.

    age_floor_min: if set (e.g. 21 for mina dig lane), filter age_floor >= that value.
    """
    query = list(niches or [])
    sites = load_sites(path) if path else load_sites()
    rows: list[dict[str, Any]] = []
    for site in sites:
        if age_floor_min is not None and site["age_floor"] < age_floor_min:
            continue
        nf = niche_fit(query, site["niches"])
        w = compute_weight(
            niche_fit_value=nf,
            signal_to_noise=site["signal_to_noise"],
            age_gate_clarity=site["age_gate_clarity"],
            metadata_richness=site["metadata_richness"],
            indexability=site["indexability"],
            spam_risk=site["spam_risk"],
        )
        row = dict(site)
        row["niche_fit"] = round(nf, 4)
        row["weight"] = w
        rows.append(row)
    rows.sort(key=lambda r: (-r["weight"], r["id"]))
    return rows


def parse_niches_param(raw: Optional[str]) -> list[str]:
    """Parse comma-separated niches query param."""
    if not raw or not raw.strip():
        return []
    return [p.strip().lower() for p in raw.split(",") if p.strip()]
