"""Job routes: create a job and query the stored jobs."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.db import get_job as db_get_job
from app.db import insert_job as db_insert_job
from app.db import list_jobs as db_list_jobs
from app.models import Job, JobCreate

router = APIRouter(tags=["jobs"])

_EMPTY_TEXT_DETAIL = "text must not be empty"


@router.post("/api/jobs", status_code=201)
async def create_job(payload: JobCreate) -> Job:
    """Store a new pending job and return the full stored record."""
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail=_EMPTY_TEXT_DETAIL)
    return db_insert_job(text, payload.analysis.value)


@router.get("/api/jobs")
async def list_jobs() -> list[Job]:
    """List all jobs, newest first (id DESC)."""
    return db_list_jobs()


@router.get("/api/jobs/{id}")
async def get_job(id: int) -> Job:
    """Return a single job by id, or 404 when it does not exist."""
    job = db_get_job(id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"job {id} not found")
    return job
