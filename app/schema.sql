-- lewka metadata schema (SQLite + FTS5)
-- METADATA ONLY: no media binaries stored.

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    media_type TEXT NOT NULL CHECK (media_type IN ('video', 'image', 'text', 'audio')),
    source TEXT NOT NULL,
    outbound_url TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '[]',  -- JSON array
    heat REAL NOT NULL DEFAULT 0.0,
    duration_or_length TEXT,          -- e.g. "12:34", "4500 words", "3:20"
    thumb_url TEXT,                   -- hotlink only; never downloaded
    sample_or_summary TEXT,
    age_proof TEXT NOT NULL,          -- required; reject if missing/unclear
    scores TEXT NOT NULL DEFAULT '{}', -- JSON object
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    connector TEXT NOT NULL,
    description TEXT,
    allowlisted INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS critique_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    payload TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE SET NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
    title,
    tags,
    sample_or_summary,
    source,
    content='items',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS items_ai AFTER INSERT ON items BEGIN
    INSERT INTO items_fts(rowid, title, tags, sample_or_summary, source)
    VALUES (new.id, new.title, new.tags, new.sample_or_summary, new.source);
END;

CREATE TRIGGER IF NOT EXISTS items_ad AFTER DELETE ON items BEGIN
    INSERT INTO items_fts(items_fts, rowid, title, tags, sample_or_summary, source)
    VALUES ('delete', old.id, old.title, old.tags, old.sample_or_summary, old.source);
END;

CREATE TRIGGER IF NOT EXISTS items_au AFTER UPDATE ON items BEGIN
    INSERT INTO items_fts(items_fts, rowid, title, tags, sample_or_summary, source)
    VALUES ('delete', old.id, old.title, old.tags, old.sample_or_summary, old.source);
    INSERT INTO items_fts(rowid, title, tags, sample_or_summary, source)
    VALUES (new.id, new.title, new.tags, new.sample_or_summary, new.source);
END;
