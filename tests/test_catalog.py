"""Catalog weight math + GET /sources?niches=."""

from __future__ import annotations

from app.services.catalog import compute_weight, niche_fit, parse_niches_param, weighted_catalog


def test_niche_fit_neutral_and_overlap():
    assert niche_fit([], ["goth", "ffm"]) == 0.5
    assert niche_fit(["goth", "ffm"], ["goth", "egirl"]) == 0.5
    assert niche_fit(["goth", "ffm"], ["goth", "ffm", "cuckquean"]) == 1.0
    assert niche_fit(["goth"], ["romance"]) == 0.0


def test_compute_weight_formula():
    # All mid/neutral: niche_fit=0.5, others 0.5, spam_risk=0.5 →
    # 0.25*0.5 + 0.20*0.5 + 0.20*0.5 + 0.15*0.5 + 0.15*0.5 + 0.05*0.5 = 0.5 → 50
    w = compute_weight(
        niche_fit_value=0.5,
        signal_to_noise=0.5,
        age_gate_clarity=0.5,
        metadata_richness=0.5,
        indexability=0.5,
        spam_risk=0.5,
    )
    assert w == 50.0

    # Perfect niche + strong scores, zero spam
    w2 = compute_weight(
        niche_fit_value=1.0,
        signal_to_noise=1.0,
        age_gate_clarity=1.0,
        metadata_richness=1.0,
        indexability=1.0,
        spam_risk=0.0,
    )
    assert w2 == 100.0


def test_parse_niches_param():
    assert parse_niches_param(None) == []
    assert parse_niches_param("goth,ffm,cuckquean") == ["goth", "ffm", "cuckquean"]
    assert parse_niches_param(" Goth , FFM ") == ["goth", "ffm"]


def test_weighted_catalog_mina_seed():
    rows = weighted_catalog(["goth", "egirl", "ffm", "cuckquean"])
    ids = {r["id"] for r in rows}
    # mina top-20 seed must be present
    for expected in (
        "burningangel",
        "clips4sale",
        "manyvids",
        "pornhub",
        "xvideos",
        "adulttime",
        "spankbang",
        "xhamster",
        "perfectgirlfriend",
        "fansly",
        "onlyfans",
        "iwantclips",
        "evilangel",
        "missax",
        "audiodesires",
        "literotica",
        "reddit_nsfw",
        "iafd",
        "alterotic",
        "teamskeet",
    ):
        assert expected in ids, expected
    assert len(rows) >= 20
    # sorted by weight desc
    weights = [r["weight"] for r in rows]
    assert weights == sorted(weights, reverse=True)
    # niche leaders should outrank generic tubes on this query
    by_id = {r["id"]: r for r in rows}
    assert by_id["burningangel"]["niche_fit"] >= 0.5
    assert by_id["burningangel"]["weight"] > by_id["xvideos"]["weight"]
    # user-liked first-party + cautious aggregators
    for liked in ("beeg", "hqporner", "mygothgf", "pussyspace", "spankbang", "xhamster", "erome", "eporner", "xpaja"):
        assert liked in ids, liked
    for caution in ("sxyprn", "hqpornsearch", "xoxporn", "pornbaker"):
        assert caution in ids, caution
    assert "thepornlinks" not in ids  # disabled directory
    assert by_id["mygothgf"]["niche_fit"] >= 0.5
    assert by_id["mygothgf"]["weight"] > by_id["sxyprn"]["weight"]
    assert by_id["hqporner"]["weight"] > by_id["hqpornsearch"]["weight"]


def test_sources_endpoint_with_niches(client):
    r = client.get("/sources")
    assert r.status_code == 200, r.text
    body = r.json()
    assert "connectors" in body and "catalog" in body
    assert len(body["connectors"]) >= 1
    assert len(body["catalog"]) >= 20
    # neutral niche_fit when no niches param
    assert all(abs(c["niche_fit"] - 0.5) < 1e-6 for c in body["catalog"])

    r2 = client.get("/sources", params={"niches": "goth,ffm,cuckquean"})
    assert r2.status_code == 200, r2.text
    cat = r2.json()["catalog"]
    assert len(cat) >= 20
    assert all("weight" in c and "niche_fit" in c for c in cat)
    # burningangel / clips4sale should appear with positive niche_fit
    by_id = {c["id"]: c for c in cat}
    assert by_id["burningangel"]["niche_fit"] > 0.0
    assert by_id["clips4sale"]["niche_fit"] >= 0.5
    # still sorted by weight
    assert [c["weight"] for c in cat] == sorted((c["weight"] for c in cat), reverse=True)
