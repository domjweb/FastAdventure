from azure.cosmos import CosmosClient
from backend.core.config import settings

def get_cosmos_client():
    return CosmosClient(settings.COSMOS_ENDPOINT, credential=settings.COSMOS_KEY)

def get_stories_container():
    client = get_cosmos_client()
    database = client.get_database_client(settings.COSMOS_DATABASE)
    container = database.get_container_client(settings.COSMOS_CONTAINER)
    return container
    


