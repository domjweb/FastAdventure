import logging
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
    partition_key = "anonymous"
    logging.info(f"Job lookup: id={job_id}, partition_key={partition_key}")
    try:
        job = container.read_item(item=job_id, partition_key=partition_key)
    except Exception as e:
        logging.error(f"Job not found: id={job_id}, partition_key={partition_key}. Exception: {e}")
        raise HTTPException(status_code=404, detail="Job not found")

    # Map Cosmos DB document to StoryJobResponse
    return StoryJobResponse(
        job_id=job["id"],
        status=job["status"],
        created_at=job["created_at"],
        story_id=job.get("story_id"),
        completed_at=job.get("completed_at"),
        error=job.get("error")
    )
