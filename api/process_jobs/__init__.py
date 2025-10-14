import azure.functions as func
import logging
from db.database import get_stories_container
from core.story_generator import StoryGenerator
from datetime import datetime

def main(mytimer: func.TimerRequest) -> None:
    logging.info("[Timer Trigger] Checking for pending jobs...")
    container = get_stories_container()
    query = "SELECT * FROM c WHERE c.status = 'pending'"
    for job in container.query_items(query=query, enable_cross_partition_query=True):
        try:
            logging.info(f"[Timer Trigger] Processing job: {job['id']}")
            # Generate story
            story_doc = StoryGenerator.generate_story(container, job['session_id'], job.get('theme', 'fantasy'))
            # Update job with story info
            job['status'] = 'completed'
            job['completed_at'] = datetime.now().isoformat()
            job['story_id'] = story_doc['id']
            container.upsert_item(job)
            # Save story to container
            container.upsert_item(story_doc)
            logging.info(f"[Timer Trigger] Job {job['id']} completed.")
        except Exception as e:
            logging.error(f"[Timer Trigger] Failed to process job {job['id']}: {e}")
            job['status'] = 'error'
            job['error'] = str(e)
            job['completed_at'] = datetime.now().isoformat()
            container.upsert_item(job)
