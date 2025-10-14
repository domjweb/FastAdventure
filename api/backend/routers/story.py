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
    import logging
    logging.info(f"[Job Creation] Creating job: {job_doc}")
    container.create_item(body=job_doc)
    logging.info(f"[Job Creation] Job created in Cosmos DB: id={job_id}, partition_key=anonymous")

    background_tasks.add_task(
        generate_story_task,
        job_id=job_id,
        theme=request.theme,
        session_id=session_id
    )

    # Map Cosmos DB job_doc to StoryJobResponse for consistent API response
    return StoryJobResponse(
        job_id=job_doc["id"],
        status=job_doc["status"],
        created_at=job_doc["created_at"],
        story_id=job_doc.get("story_id"),
        completed_at=job_doc.get("completed_at"),
        error=job_doc.get("error")
    )

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


# Cosmos DB: Retrieve story document by id and partition key
@router.get("/{story_id}/complete", response_model=CompleteStoryResponse)
def get_complete_story(story_id: str):
    container = get_stories_container()
    partition_key = "anonymous"  # Replace with actual user_id if needed
    import logging
    try:
        story = container.read_item(item=story_id, partition_key=partition_key)
    except Exception as e:
        logging.error(f"Story not found: id={story_id}, partition_key={partition_key}. Exception: {e}")
        raise HTTPException(status_code=404, detail="Story not found")

    # Map Cosmos DB document to CompleteStoryResponse
    return CompleteStoryResponse(
        id=story["id"],
        title=story["title"],
        session_id=story.get("session_id"),
        created_at=story.get("created_at"),
        root_node=story.get("rootNode"),
        all_nodes={}  # Optionally populate if you store all nodes separately
    )

