"""Tests for the API service skeleton: the app imports and /health answers."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_app_imports() -> None:
    assert app is not None


def test_health_returns_ok(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("JOB_DB_PATH", str(tmp_path / "test_jobs.db"))
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
