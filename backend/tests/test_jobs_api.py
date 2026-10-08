"""Tests for the jobs API: creation, validation, listing and lookup."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def _db_path(tmp_path: Path) -> str:
    return str(tmp_path / "jobs.db")


def test_create_job_returns_201_pending_and_persists(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("JOB_DB_PATH", _db_path(tmp_path))

    with TestClient(app) as client:
        response = client.post(
            "/api/jobs",
            json={"text": "  hello brave world  ", "analysis": "word_count"},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["text"] == "hello brave world"
    assert body["analysis"] == "word_count"
    assert body["status"] == "pending"
    assert body["result"] is None
    assert body["error"] is None
    assert body["created_at"]
    assert body["updated_at"]
    job_id = body["id"]

    with TestClient(app) as client:
        listed = client.get("/api/jobs")

    assert listed.status_code == 200
    assert [job["id"] for job in listed.json()] == [job_id]


def test_get_job_by_id_returns_the_job(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("JOB_DB_PATH", _db_path(tmp_path))

    with TestClient(app) as client:
        created = client.post(
            "/api/jobs",
            json={"text": "some text", "analysis": "top_words"},
        ).json()
        fetched = client.get(f"/api/jobs/{created['id']}")

    assert fetched.status_code == 200
    assert fetched.json() == created


def test_list_jobs_is_newest_first(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("JOB_DB_PATH", _db_path(tmp_path))

    with TestClient(app) as client:
        for index in range(3):
            client.post(
                "/api/jobs",
                json={"text": f"text {index}", "analysis": "reading_time"},
            )
        listed = client.get("/api/jobs")

    assert listed.status_code == 200
    ids = [job["id"] for job in listed.json()]
    assert ids == sorted(ids, reverse=True)
    assert len(ids) == 3


def test_get_unknown_job_returns_404_with_string_detail(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("JOB_DB_PATH", _db_path(tmp_path))

    with TestClient(app) as client:
        response = client.get("/api/jobs/9999")

    assert response.status_code == 404
    assert isinstance(response.json()["detail"], str)


def test_empty_text_returns_422_and_stores_nothing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("JOB_DB_PATH", _db_path(tmp_path))

    with TestClient(app) as client:
        response = client.post("/api/jobs", json={"text": "", "analysis": "word_count"})
        listed = client.get("/api/jobs")

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)
    assert listed.json() == []


def test_whitespace_only_text_returns_422_and_stores_nothing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("JOB_DB_PATH", _db_path(tmp_path))

    with TestClient(app) as client:
        response = client.post("/api/jobs", json={"text": "   \n\t ", "analysis": "word_count"})
        listed = client.get("/api/jobs")

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)
    assert listed.json() == []


def test_unknown_analysis_returns_422_and_stores_nothing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("JOB_DB_PATH", _db_path(tmp_path))

    with TestClient(app) as client:
        response = client.post("/api/jobs", json={"text": "some text", "analysis": "bogus"})
        listed = client.get("/api/jobs")

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)
    assert listed.json() == []
