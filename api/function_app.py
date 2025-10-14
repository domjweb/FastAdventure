import azure.functions as func
from mangum import Mangum
from main import app  # Import your FastAPI app

handler = Mangum(app)

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
	return func.AsgiMiddleware(handler).handle(req, context)