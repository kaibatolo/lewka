"""Ingest + search happy path."""

from __future__ import annotations


def test_ingest_and_search_happy_path(client):
    ingest = {
        "title": "Velvet Night Audio",
        "media_type": "audio",
        "source": "manual",
        "outbound_url": "https://example.com/audio/velvet",
        "tags": ["audio", "asmr", "consent"],
        "heat": 0.8,
        "duration_or_length": "12:04",
        "thumb_url": "https://cdn.example.com/thumbs/velvet.jpg",
        "sample_or_summary": "Soft spoken adult ASMR with clear consent framing.",
        "age_proof": "18+ age_verified attestation",
        "connector": "manual_url",
    }
    r = client.post("/ingest", json=ingest)
    assert r.status_code == 200, r.text
    item_id = r.json()["id"]

    # FTS search
    s = client.post("/search", json={"query": "Velvet", "limit": 10})
    assert s.status_code == 200, s.text
    body = s.json()
    assert body["count"] >= 1
    ids = [row["id"] for row in body["results"]]
    assert item_id in ids

    # Filter by media_type
    s2 = client.post("/search", json={"query": "", "media_type": "audio"})
    assert s2.status_code == 200
    assert any(row["id"] == item_id for row in s2.json()["results"])

    # GET item
    g = client.get(f"/item/{item_id}")
    assert g.status_code == 200
    assert g.json()["title"] == "Velvet Night Audio"

    # health
    h = client.get("/health")
    assert h.status_code == 200
    assert h.json()["status"] == "ok"
