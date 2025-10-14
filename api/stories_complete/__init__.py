import azure.functions as func
from db.database import get_stories_container
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    story_id = req.route_params.get('story_id')
    if req.method == "GET" and story_id:
        container = get_stories_container()
        try:
            story = container.read_item(item=story_id, partition_key="anonymous")
            return func.HttpResponse(
                json.dumps(story, default=str),
                mimetype="application/json"
            )
        except Exception:
            return func.HttpResponse(
                '{"detail": "Story not found"}',
                status_code=404,
                mimetype="application/json"
            )
    return func.HttpResponse(
        '{"detail": "Method not allowed"}',
        status_code=405,
        mimetype="application/json"
    )
