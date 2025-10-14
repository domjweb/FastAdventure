import azure.functions as func
import logging
from db.database import get_stories_container
from schemas.job import StoryJobResponse

def main(req: func.HttpRequest) -> func.HttpResponse:
    job_id = req.route_params.get('job_id')
    container = get_stories_container()
    partition_key = "anonymous"
    logging.info(f"[Job Lookup] Attempting to read job: id={job_id}, partition_key={partition_key}")
    try:
        job = container.read_item(item=job_id, partition_key=partition_key)
        logging.info(f"[Job Lookup] Found job: {job}")
    except Exception as e:
        logging.error(f"[Job Lookup] Job not found: id={job_id}, partition_key={partition_key}. Exception: {e}")
        return func.HttpResponse(
            '{"detail": "Job not found"}',
            status_code=404,
            mimetype="application/json"
        )
    # Map Cosmos DB document to response
    return func.HttpResponse(
        f'{{"job_id": "{job["id"]}", "status": "{job["status"]}", "created_at": "{job["created_at"]}", "story_id": {repr(job.get("story_id"))}, "completed_at": {repr(job.get("completed_at"))}, "error": {repr(job.get("error"))}}}',
        mimetype="application/json"
    )
