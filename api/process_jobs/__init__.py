import azure.functions as func
import logging
from db.database import get_stories_container
from core.story_generator import StoryGenerator
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("[HTTP Trigger] Processing pending jobs...")
    container = get_stories_container()
    query = "SELECT * FROM c WHERE c.status = 'pending'"
    processed = 0
    for job in container.query_items(query=query, enable_cross_partition_query=True):
        try:
            logging.info(f"[HTTP Trigger] Processing job: {job['id']}")
            story_doc = StoryGenerator.generate_story(container, job['session_id'], job.get('theme', 'fantasy'))
            job['status'] = 'completed'
            job['completed_at'] = datetime.now().isoformat()
            job['story_id'] = story_doc['id']
            container.upsert_item(job)
            container.upsert_item(story_doc)
            processed += 1
        except Exception as e:
            logging.error(f"[HTTP Trigger] Failed to process job {job['id']}: {e}")
            job['status'] = 'error'
            job['error'] = str(e)
            job['completed_at'] = datetime.now().isoformat()
            container.upsert_item(job)
    return func.HttpResponse(f"Processed {processed} jobs.", status_code=200)
