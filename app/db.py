"""SQLite + FTS5 database setup for lewka (metadata only)."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Iterable, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "lewka.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

_DEFAULT_SOURCES = [
    ("manual", "manual_url", "Manual URL / paste ingest"),
    ("ao3", "ao3_class", "AO3 class stub normalizer (no live scrape)"),
    ("private_library", "private_library", "Private library connector"),
    ("reddit_nsfw", "reddit_nsfw", "Reddit NSFW stub (allowlisted only)"),
]


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    path = db_path or DB_PATH
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_connection(path) as conn:
        conn.executescript(schema)
        for name, connector, description in _DEFAULT_SOURCES:
            conn.execute(
                """
                INSERT OR IGNORE INTO sources (name, connector, description, allowlisted)
                VALUES (?, ?, ?, 1)
                """,
                (name, connector, description),
            )
        conn.commit()


@contextmanager
def session(db_path: Optional[Path] = None) -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def row_to_item(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    d["tags"] = json.loads(d.get("tags") or "[]")
    d["scores"] = json.loads(d.get("scores") or "{}")
    return d


def insert_item(conn: sqlite3.Connection, data: dict[str, Any]) -> int:
    cur = conn.execute(
        """
        INSERT INTO items (
            title, media_type, source, outbound_url, tags, heat,
            duration_or_length, thumb_url, sample_or_summary, age_proof, scores
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["title"],
            data["media_type"],
            data["source"],
            data["outbound_url"],
            json.dumps(data.get("tags") or []),
            float(data.get("heat") or 0.0),
            data.get("duration_or_length"),
            data.get("thumb_url"),
            data.get("sample_or_summary"),
            data["age_proof"],
            json.dumps(data.get("scores") or {}),
        ),
    )
    return int(cur.lastrowid)


def get_item(conn: sqlite3.Connection, item_id: int) -> Optional[dict[str, Any]]:
    row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    return row_to_item(row) if row else None


def delete_item(conn: sqlite3.Connection, item_id: int) -> bool:
    cur = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    return cur.rowcount > 0


def list_sources(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT id, name, connector, description, allowlisted, created_at FROM sources ORDER BY name"
    ).fetchall()
    return [dict(r) for r in rows]


def search_items(
    conn: sqlite3.Connection,
    query: str,
    media_type: Optional[str] = None,
    source: Optional[str] = None,
    tags: Optional[Iterable[str]] = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    if query and query.strip():
        # FTS5 MATCH; escape double quotes in query for safety
        safe_q = query.strip().replace('"', '""')
        sql = """
            SELECT i.* FROM items i
            JOIN items_fts f ON i.id = f.rowid
            WHERE items_fts MATCH ?
        """
        params: list[Any] = [safe_q]
    else:
        sql = "SELECT i.* FROM items i WHERE 1=1"
        params = []

    if media_type:
        sql += " AND i.media_type = ?"
        params.append(media_type)
    if source:
        sql += " AND i.source = ?"
        params.append(source)
    if tags:
        for tag in tags:
            sql += " AND i.tags LIKE ?"
            params.append(f'%"{tag}"%')

    sql += " ORDER BY i.heat DESC, i.id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(sql, params).fetchall()
    return [row_to_item(r) for r in rows]


def update_item_scores(conn: sqlite3.Connection, item_id: int, scores: dict[str, Any]) -> bool:
    cur = conn.execute(
        """
        UPDATE items SET scores = ?, updated_at = datetime('now')
        WHERE id = ?
        """,
        (json.dumps(scores), item_id),
    )
    return cur.rowcount > 0


def insert_critique(conn: sqlite3.Connection, item_id: Optional[int], payload: dict[str, Any]) -> int:
    cur = conn.execute(
        """
        INSERT INTO critique_requests (item_id, payload, status)
        VALUES (?, ?, 'pending')
        """,
        (item_id, json.dumps(payload)),
    )
    return int(cur.lastrowid)
