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
        # Always use 'anonymous' as the partition key for now
        job = container.read_item(item=job_id, partition_key="anonymous")
    except Exception as e:
        import logging
        logging.error(f"Job not found: {job_id} with partition key 'anonymous'. Exception: {e}")
        raise HTTPException(status_code=404, detail="Job not found")
    return job
