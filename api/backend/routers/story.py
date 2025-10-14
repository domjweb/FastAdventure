import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks
from backend.db.database import get_stories_container
from backend.schemas.story import (
    CompleteStoryResponse, CompleteStoryNodeResponse, CreateStoryRequest
)
from backend.schemas.job import StoryJobResponse
from backend.core.story_generator import StoryGenerator


router = APIRouter(
    prefix="/stories",
    tags=["stories"]
)

def get_session_id(session_id: Optional[str] = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

@router.post("/create", response_model=StoryJobResponse)
def create_story(
    request: CreateStoryRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    session_id: str = Depends(get_session_id)
):
    response.set_cookie(key="session_id", value=session_id)
    job_id = str(uuid.uuid4())
    container = get_stories_container()
    job_doc = {
        "id": job_id,
        "session_id": session_id,
        "theme": request.theme,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "user_id": "anonymous"  # Replace with actual user/account id if available
    }
    container.create_item(body=job_doc)

    background_tasks.add_task(
        generate_story_task,
        job_id=job_id,
        theme=request.theme,
        session_id=session_id
    )

    return job_doc

def generate_story_task(job_id: str, theme: str, session_id: str):
    import logging
    logging.basicConfig(level=logging.INFO)
    container = get_stories_container()
    try:
        job = container.read_item(item=job_id, partition_key="anonymous")  # Replace with actual user_id if available
        job["status"] = "processing"
        container.upsert_item(body=job)

        story = StoryGenerator.generate_story(None, session_id, theme)
        job["story_id"] = story.get("id")
        job["status"] = "completed"
        job["completed_at"] = datetime.now().isoformat()
        container.upsert_item(body=job)
        print(f"[generate_story_task] Job completed. story_id={job.get('story_id')}")
        logging.info(f"[generate_story_task] Job completed. story_id={job.get('story_id')}")
    except Exception as e:
        job = container.read_item(item=job_id, partition_key="anonymous")
        job["status"] = "failed"
        job["completed_at"] = datetime.now().isoformat()
        job["error"] = str(e)
        container.upsert_item(body=job)
        print(f"[generate_story_task] Exception occurred: {e}")
        logging.error(f"[generate_story_task] Exception occurred: {e}")

# Cosmos DB: Implement story retrieval logic as needed

