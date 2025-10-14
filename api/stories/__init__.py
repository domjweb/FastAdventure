import azure.functions as func
import uuid
from datetime import datetime
from db.database import get_stories_container
from schemas.story import CreateStoryRequest
from schemas.job import StoryJobResponse
from core.story_generator import StoryGenerator
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "POST":
        try:
            data = req.get_json()
            theme = data.get("theme", "fantasy")
        except Exception:
            return func.HttpResponse(
                '{"detail": "Invalid request body"}',
                status_code=400,
                mimetype="application/json"
            )
        session_id = str(uuid.uuid4())
        job_id = str(uuid.uuid4())
        container = get_stories_container()
        job_doc = {
            "id": job_id,
            "session_id": session_id,
            "theme": theme,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "user_id": "anonymous"
        }
        container.create_item(body=job_doc)
        return func.HttpResponse(
            json.dumps({
                "job_id": job_doc["id"],
                "status": job_doc["status"],
                "created_at": job_doc["created_at"],
                "story_id": job_doc.get("story_id"),
                "completed_at": job_doc.get("completed_at"),
                "error": job_doc.get("error")
            }),
            mimetype="application/json"
        )
    return func.HttpResponse(
        '{"detail": "Method not allowed"}',
        status_code=405,
        mimetype="application/json"
    )
