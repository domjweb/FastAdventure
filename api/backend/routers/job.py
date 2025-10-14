import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Cookie
from backend.db.database import get_stories_container
from backend.schemas.job import StoryJobResponse

router = APIRouter (
    prefix="/jobs",
    tags=["jobs"]
)

@router.get("/{job_id}", response_model=StoryJobResponse)
def get_job_status(job_id: str):
    container = get_stories_container()
    try:
        job = container.read_item(item=job_id, partition_key="anonymous")  # Replace with actual user_id if available
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
