"""SQLite helpers for the jobs store.

Both the API and the worker open the SAME database file, named by the
``JOB_DB_PATH`` environment variable. A relative value resolves against the
repository root, never the process working directory, so the two processes find
the same file regardless of where they were started from.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = "jobs.db"
BUSY_TIMEOUT_MS = 5000

_CREATE_JOBS_TABLE = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    analysis TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    result TEXT,
    error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""


def _resolve_db_path() -> str:
    """Return the SQLite path for ``JOB_DB_PATH``, resolved against the repo root."""
    raw = os.environ.get("JOB_DB_PATH", DEFAULT_DB_PATH)
    if raw == ":memory:" or raw.startswith("file:"):
        return raw
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    return str(path)


def connect() -> sqlite3.Connection:
    """Open (creating if needed) the jobs database with a busy timeout set."""
    db_path = _resolve_db_path()
    if db_path != ":memory:" and not db_path.startswith("file:"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
    return conn


def init_db() -> None:
    """Create the jobs table if it does not exist yet. Safe to call repeatedly."""
    conn = connect()
    try:
        conn.execute(_CREATE_JOBS_TABLE)
        conn.commit()
    finally:
        conn.close()
