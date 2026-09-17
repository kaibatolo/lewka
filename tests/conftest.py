"""Pytest fixtures — isolated temp SQLite DB per test session/function."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import db as db_mod  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_lewka.db"
    monkeypatch.setattr(db_mod, "DB_PATH", test_db)
    db_mod.init_db(test_db)
    with TestClient(app) as c:
        yield c
