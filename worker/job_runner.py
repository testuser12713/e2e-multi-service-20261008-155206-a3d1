"""Job processing step.

Claims at most one pending job per call and turns it into a finished job. The
claim is a single atomic ``UPDATE ... RETURNING`` so a second worker pass (or a
second worker process) never picks up a job that is already ``in_progress``.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime

try:
    from worker.analyses import compute
except ImportError:  # pragma: no cover - allows running from inside worker/
    from analyses import compute  # type: ignore[no-redef]

CLAIM_SQL = """
UPDATE jobs
SET status = 'in_progress', updated_at = ?
WHERE id = (
    SELECT id FROM jobs WHERE status = 'pending' ORDER BY id ASC LIMIT 1
)
  AND status = 'pending'
RETURNING id, text, analysis
"""


def _utcnow() -> str:
    """Current UTC time as an ISO-8601 string."""
    return datetime.now(UTC).isoformat()


def process_one(conn: sqlite3.Connection) -> int | None:
    """Claim and process at most one pending job.

    Returns the id of the processed job, or ``None`` when there was nothing to
    do. The claimed job's status is committed as ``in_progress`` before the
    computation runs, so no later pass sees it as ``pending`` again. A failing
    computation is recorded as a ``failed`` job with the error message; the
    exception is swallowed so the poll loop keeps running.
    """
    now = _utcnow()
    row = conn.execute(CLAIM_SQL, (now,)).fetchone()
    if row is None:
        conn.commit()
        return None

    job_id = row[0]
    text = row[1]
    analysis = row[2]
    conn.commit()

    try:
        result = compute(analysis, text)
    except Exception as exc:
        message = str(exc) or exc.__class__.__name__
        conn.execute(
            "UPDATE jobs SET status = 'failed', error = ?, updated_at = ? WHERE id = ?",
            (message, _utcnow(), job_id),
        )
        conn.commit()
        return job_id

    conn.execute(
        "UPDATE jobs SET status = 'done', result = ?, error = NULL, updated_at = ? WHERE id = ?",
        (json.dumps(result), _utcnow(), job_id),
    )
    conn.commit()
    return job_id
