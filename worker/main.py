"""Worker entry point.

Connects to the shared jobs database, ensures the schema exists and then polls
forever: every ``POLL_INTERVAL_SECONDS`` seconds it runs one processing step
and logs a single line per tick. SIGINT and SIGTERM stop the loop cleanly.
"""

from __future__ import annotations

import logging
import os
import signal
import sqlite3
import threading

try:
    from worker import db, job_runner
except ImportError:  # pragma: no cover - allows running from inside worker/
    import db  # type: ignore[no-redef]
    import job_runner  # type: ignore[no-redef]

logger = logging.getLogger("worker")

DEFAULT_POLL_INTERVAL_SECONDS = 2.0


def poll_interval_seconds() -> float:
    """Read ``POLL_INTERVAL_SECONDS`` defensively, falling back to the default."""
    raw = (os.environ.get("POLL_INTERVAL_SECONDS") or "").strip()
    if not raw:
        return DEFAULT_POLL_INTERVAL_SECONDS
    try:
        value = float(raw)
    except ValueError:
        logger.warning(
            "invalid POLL_INTERVAL_SECONDS=%r, using %s", raw, DEFAULT_POLL_INTERVAL_SECONDS
        )
        return DEFAULT_POLL_INTERVAL_SECONDS
    if value <= 0:
        logger.warning(
            "non-positive POLL_INTERVAL_SECONDS=%r, using %s", raw, DEFAULT_POLL_INTERVAL_SECONDS
        )
        return DEFAULT_POLL_INTERVAL_SECONDS
    return value


def run(
    stop_event: threading.Event,
    conn: sqlite3.Connection | None = None,
    interval: float | None = None,
) -> None:
    """Poll the jobs database until ``stop_event`` is set.

    ``conn`` and ``interval`` are injectable so the loop can be exercised
    without reading the environment. When no connection is given one is opened
    from ``JOB_DB_PATH`` and closed on stop.
    """
    owns_conn = conn is None
    if conn is None:
        conn = db.connect()
    db.init_db(conn)
    tick_interval = poll_interval_seconds() if interval is None else interval
    logger.info("worker started (interval=%ss)", tick_interval)
    try:
        while not stop_event.is_set():
            processed = job_runner.process_one(conn)
            logger.info("poll tick: processed=%s", processed)
            stop_event.wait(tick_interval)
    finally:
        if owns_conn:
            conn.close()
    logger.info("worker stopped")


def main() -> int:
    """Configure logging and signals, then run the poll loop."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    stop_event = threading.Event()

    def request_stop(signum: int, _frame: object) -> None:
        logger.info("received signal %s, shutting down", signum)
        stop_event.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)

    try:
        run(stop_event)
    except KeyboardInterrupt:  # pragma: no cover - signal handler normally wins
        stop_event.set()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
