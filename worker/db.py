"""SQLite access for the worker service.

The worker and the API share a single SQLite file, chosen through the
``JOB_DB_PATH`` environment variable. A relative value is resolved against the
repository root (never the process working directory) so both services always
reach the same file.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parent.parent
DEFAULT_DB_FILENAME = "jobs.db"

BUSY_TIMEOUT_MS = 5000

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    analysis TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    result TEXT,
    error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def resolve_db_path() -> str:
    """Return the absolute database path.

    ``JOB_DB_PATH`` may be absolute or relative; a relative value is anchored
    at the repository root. The in-memory sentinel ``:memory:`` is returned
    untouched.
    """
    raw = (os.environ.get("JOB_DB_PATH") or "").strip() or DEFAULT_DB_FILENAME
    if raw == ":memory:":
        return raw
    path = Path(raw)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return str(path)


def connect(db_path: str | None = None) -> sqlite3.Connection:
    """Open a connection to the shared jobs database.

    When ``db_path`` is omitted the ``JOB_DB_PATH`` environment variable is
    resolved. The schema's parent directory is created if needed and the
    SQLite busy timeout is set so the API and the worker can share the file.
    """
    path = db_path or resolve_db_path()
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Create the jobs table if it does not exist yet (idempotent)."""
    conn.execute(SCHEMA)
    conn.commit()
