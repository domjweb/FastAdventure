import azure.functions as func
import logging
import json
import uuid
from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from backend.db.database import SessionLocal
from backend.models.job import StoryJob
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
    db = SessionLocal()
    try:
        job = StoryJob(
            job_id=job_id,
            session_id=session_id,
            theme=theme,
            status="processing"
        )
        db.add(job)
        db.commit()

        try:
            story = StoryGenerator.generate_story(db, session_id, theme)
            job.story_id = story.id
            job.status = "completed"
            job.completed_at = datetime.now()
            db.commit()
            result = {
                "job_id": job.job_id,
                "session_id": job.session_id,
                "theme": job.theme,
                "status": job.status,
                "story_id": job.story_id,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None
            }
            return func.HttpResponse(
                json.dumps(result),
                status_code=200,
                mimetype="application/json"
            )
        except Exception as e:
            job.status = "failed"
            job.completed_at = datetime.now()
            job.error = str(e)
            db.commit()
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                status_code=500,
                mimetype="application/json"
            )
    finally:
        db.close()
