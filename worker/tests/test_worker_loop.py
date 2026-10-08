"""Tests for the worker poll loop skeleton.

The skeleton processes nothing: with an empty database one tick is a no-op and
the loop can be stopped cleanly.
"""

from __future__ import annotations

import threading
import time

from worker import db, job_runner, main


def test_process_one_returns_none_on_empty_database() -> None:
    """A tick over an empty database processes no job."""
    conn = db.connect(":memory:")
    try:
        db.init_db(conn)
        assert job_runner.process_one(conn) is None
    finally:
        conn.close()


def test_init_db_creates_jobs_table() -> None:
    conn = db.connect(":memory:")
    try:
        db.init_db(conn)
        db.init_db(conn)
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'jobs'"
        ).fetchone()
        assert row is not None
    finally:
        conn.close()


def test_loop_runs_ticks_and_can_be_stopped(tmp_path) -> None:
    """The loop keeps ticking and returns once the stop event is set."""
    conn = db.connect(str(tmp_path / "jobs.db"))
    try:
        db.init_db(conn)
        stop_event = threading.Event()
        thread = threading.Thread(
            target=main.run,
            args=(stop_event,),
            kwargs={"conn": conn, "interval": 0.01},
        )
        thread.start()
        time.sleep(0.05)
        stop_event.set()
        thread.join(timeout=5)
        assert not thread.is_alive()
    finally:
        conn.close()


def test_run_resolves_job_db_path_from_environment(tmp_path, monkeypatch) -> None:
    """Without an injected connection the loop uses JOB_DB_PATH."""
    monkeypatch.setenv("JOB_DB_PATH", str(tmp_path / "jobs.db"))
    stop_event = threading.Event()
    stop_event.set()
    main.run(stop_event, interval=0.01)
    assert (tmp_path / "jobs.db").exists()
