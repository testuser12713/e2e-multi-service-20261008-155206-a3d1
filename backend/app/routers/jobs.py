"""Job routes.

The final paths, verbs and signatures are fixed here; the behaviour itself is
owned by a later ticket. Until then each route answers 501 Not Implemented so a
caller can tell "not built yet" apart from a crash.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import Job, JobCreate

router = APIRouter(tags=["jobs"])

_NOT_IMPLEMENTED = "the jobs API is not implemented yet"


@router.post("/api/jobs", status_code=201)
async def create_job(payload: JobCreate) -> Job:
    """Create a job from ``payload``. Not implemented yet."""
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.get("/api/jobs")
async def list_jobs() -> list[Job]:
    """List all jobs, newest first. Not implemented yet."""
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.get("/api/jobs/{id}")
async def get_job(id: int) -> Job:
    """Return a single job by id. Not implemented yet."""
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)
