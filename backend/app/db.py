"""SQLite helpers for the jobs store.

Both the API and the worker open the SAME database file, named by the
``JOB_DB_PATH`` environment variable. A relative value resolves against the
repository root, never the process working directory, so the two processes find
the same file regardless of where they were started from.
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from app.models import Job

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


def _utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(UTC).isoformat()


def _row_to_job(row: sqlite3.Row) -> Job:
    """Map a ``jobs`` row to a :class:`Job`, decoding the JSON ``result`` text."""
    raw_result = row["result"]
    result = json.loads(raw_result) if raw_result is not None else None
    return Job(
        id=row["id"],
        text=row["text"],
        analysis=row["analysis"],
        status=row["status"],
        result=result,
        error=row["error"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def insert_job(text: str, analysis: str) -> Job:
    """Insert a pending job and return the stored record."""
    now = _utc_now_iso()
    conn = connect()
    try:
        cursor = conn.execute(
            "INSERT INTO jobs (text, analysis, status, created_at, updated_at) "
            "VALUES (?, ?, 'pending', ?, ?)",
            (text, analysis, now, now),
        )
        conn.commit()
        job_id = cursor.lastrowid
    finally:
        conn.close()
    job = get_job(int(job_id))
    if job is None:  # pragma: no cover - the row was just written
        raise RuntimeError(f"job {job_id} disappeared right after insert")
    return job


def list_jobs() -> list[Job]:
    """Return every job, newest first (id DESC)."""
    conn = connect()
    try:
        rows = conn.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
    finally:
        conn.close()
    return [_row_to_job(row) for row in rows]


def get_job(job_id: int) -> Job | None:
    """Return the job with ``job_id`` or ``None`` when it does not exist."""
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    finally:
        conn.close()
    return _row_to_job(row) if row is not None else None
