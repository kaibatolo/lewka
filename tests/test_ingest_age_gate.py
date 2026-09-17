"""Ingest must reject without clear age_proof; accept with 18+ proof."""

from __future__ import annotations


VALID_BASE = {
    "title": "Example Adult Story",
    "media_type": "text",
    "source": "manual",
    "outbound_url": "https://example.com/work/1",
    "tags": ["romance", "consent"],
    "sample_or_summary": "A short sample of consensual adult fiction.",
    "connector": "manual_url",
}


def test_ingest_rejects_missing_age_proof(client):
    # Pydantic requires age_proof field — send empty string to hit gate
    payload = {**VALID_BASE, "age_proof": ""}
    r = client.post("/ingest", json=payload)
    assert r.status_code == 422 or r.status_code == 400


def test_ingest_rejects_unclear_age_proof(client):
    payload = {**VALID_BASE, "age_proof": "unknown"}
    r = client.post("/ingest", json=payload)
    assert r.status_code == 400
    assert "age_proof" in r.json()["detail"].lower() or "18+" in r.json()["detail"]


def test_ingest_rejects_unclear_n_a(client):
    payload = {**VALID_BASE, "age_proof": "n/a"}
    r = client.post("/ingest", json=payload)
    assert r.status_code == 400


def test_ingest_accepts_with_age_proof(client):
    payload = {**VALID_BASE, "age_proof": "18+ attested by submitter"}
    r = client.post("/ingest", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "ingested"
    assert data["id"] >= 1
    assert data["item"]["age_proof"].startswith("18+")
    assert data["item"]["media_type"] == "text"
