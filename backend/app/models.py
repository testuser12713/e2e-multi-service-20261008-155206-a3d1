"""Shared data models for jobs.

The shapes here are the product's contract between the API, the worker and the
frontend and must not diverge from it.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class Analysis(StrEnum):
    """The three text analyses a job can request."""

    word_count = "word_count"
    top_words = "top_words"
    reading_time = "reading_time"


class JobStatus(StrEnum):
    """Lifecycle of a job."""

    pending = "pending"
    in_progress = "in_progress"
    done = "done"
    failed = "failed"


class JobCreate(BaseModel):
    """Payload accepted by POST /api/jobs."""

    text: str
    analysis: Analysis


class Job(BaseModel):
    """A stored job as returned by the API."""

    id: int
    text: str
    analysis: Analysis
    status: JobStatus
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: str
    updated_at: str
