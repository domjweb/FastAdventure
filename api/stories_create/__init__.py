import azure.functions as func
import logging
import json
import uuid
from datetime import datetime

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from backend.db.database import get_stories_container
from backend.core.story_generator import StoryGenerator

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Azure Function: stories_create called')
    try:
        data = req.get_json()
        theme = data.get('theme')
        if not theme:
            raise ValueError('Missing theme')
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": f"Invalid request: {str(e)}"}),
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
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "user_id": "anonymous"  # Replace with actual user/account id if available
    }
    container.create_item(body=job_doc)

    try:
        # Generate story and update job document
        story = StoryGenerator.generate_story(None, session_id, theme)  # Update StoryGenerator to not require db
        job_doc["story_id"] = story.get("id")
        job_doc["status"] = "completed"
        job_doc["completed_at"] = datetime.now().isoformat()
        container.upsert_item(body=job_doc)
        result = {
            "job_id": job_doc["id"],
            "session_id": job_doc["session_id"],
            "theme": job_doc["theme"],
            "status": job_doc["status"],
            "story_id": job_doc.get("story_id"),
            "completed_at": job_doc.get("completed_at")
        }
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        job_doc["status"] = "failed"
        job_doc["completed_at"] = datetime.now().isoformat()
        job_doc["error"] = str(e)
        container.upsert_item(body=job_doc)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
