"""Lifecycle tests for the worker job runner.

These run against a temporary SQLite file so the atomic claim is exercised on
the same kind of connection the real worker uses.
"""

from __future__ import annotations

import json
import sqlite3

from worker import db, job_runner

NOW = "2026-01-01T00:00:00+00:00"


def _insert_job(
    conn: sqlite3.Connection,
    text: str,
    analysis: str,
    status: str = "pending",
) -> int:
    cur = conn.execute(
        "INSERT INTO jobs (text, analysis, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (text, analysis, status, NOW, NOW),
    )
    conn.commit()
    assert cur.lastrowid is not None
    return int(cur.lastrowid)


def _connect(tmp_path) -> sqlite3.Connection:
    conn = db.connect(str(tmp_path / "jobs.db"))
    db.init_db(conn)
    return conn


def test_process_one_returns_none_on_empty_database(tmp_path) -> None:
    conn = _connect(tmp_path)
    try:
        assert job_runner.process_one(conn) is None
    finally:
        conn.close()


def test_word_count_job_lifecycle_pending_to_done(tmp_path) -> None:
    conn = _connect(tmp_path)
    try:
        job_id = _insert_job(conn, "one two three", "word_count")
        assert job_runner.process_one(conn) == job_id
        row = conn.execute(
            "SELECT status, result, error FROM jobs WHERE id = ?", (job_id,)
        ).fetchone()
        assert row["status"] == "done"
        assert json.loads(row["result"]) == {"word_count": 3}
        assert row["error"] is None
    finally:
        conn.close()


def test_marks_in_progress_before_computing(tmp_path, monkeypatch) -> None:
    conn = _connect(tmp_path)
    try:
        job_id = _insert_job(conn, "a b c", "word_count")
        seen: dict = {}
        real_compute = job_runner.compute

        def spy(analysis: str, text: str) -> dict:
            seen["status"] = conn.execute(
                "SELECT status FROM jobs WHERE id = ?", (job_id,)
            ).fetchone()["status"]
            return real_compute(analysis, text)

        monkeypatch.setattr(job_runner, "compute", spy)
        assert job_runner.process_one(conn) == job_id
        assert seen["status"] == "in_progress"
    finally:
        conn.close()


def test_second_pass_does_not_pick_up_claimed_job(tmp_path, monkeypatch) -> None:
    path = str(tmp_path / "jobs.db")
    conn = db.connect(path)
    db.init_db(conn)
    other = db.connect(path)
    try:
        job_id = _insert_job(conn, "a b c", "word_count")
        seen: dict = {}
        real_compute = job_runner.compute

        def spy(analysis: str, text: str) -> dict:
            seen["second"] = job_runner.process_one(other)
            return real_compute(analysis, text)

        monkeypatch.setattr(job_runner, "compute", spy)
        assert job_runner.process_one(conn) == job_id
        assert seen["second"] is None
    finally:
        conn.close()
        other.close()


def test_top_words_job_writes_contract_shape(tmp_path) -> None:
    conn = _connect(tmp_path)
    try:
        job_id = _insert_job(conn, "the cat the dog the cat", "top_words")
        assert job_runner.process_one(conn) == job_id
        row = conn.execute("SELECT status, result FROM jobs WHERE id = ?", (job_id,)).fetchone()
        assert row["status"] == "done"
        assert json.loads(row["result"]) == {
            "top_words": [
                {"word": "the", "count": 3},
                {"word": "cat", "count": 2},
                {"word": "dog", "count": 1},
            ]
        }
    finally:
        conn.close()


def test_reading_time_job_writes_contract_shape(tmp_path) -> None:
    conn = _connect(tmp_path)
    try:
        job_id = _insert_job(conn, " ".join(["word"] * 100), "reading_time")
        assert job_runner.process_one(conn) == job_id
        row = conn.execute("SELECT status, result FROM jobs WHERE id = ?", (job_id,)).fetchone()
        assert row["status"] == "done"
        assert json.loads(row["result"]) == {"reading_time_minutes": 0.5, "word_count": 100}
    finally:
        conn.close()


def test_failed_computation_marks_job_failed_and_loop_continues(tmp_path) -> None:
    conn = _connect(tmp_path)
    try:
        bad_id = _insert_job(conn, "some text", "not_a_real_analysis")
        assert job_runner.process_one(conn) == bad_id
        bad = conn.execute("SELECT status, error FROM jobs WHERE id = ?", (bad_id,)).fetchone()
        assert bad["status"] == "failed"
        assert bad["error"]

        good_id = _insert_job(conn, "one two", "word_count")
        assert job_runner.process_one(conn) == good_id
        good = conn.execute("SELECT status, result FROM jobs WHERE id = ?", (good_id,)).fetchone()
        assert good["status"] == "done"
        assert json.loads(good["result"]) == {"word_count": 2}
    finally:
        conn.close()
