

import logging
logging.basicConfig(level=logging.INFO)
logging.info("[main.py] FastAPI app starting up...")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from routers import story, job
from db.database import create_tables

logging.info("[main.py] Creating database tables...")
create_tables()

app = FastAPI(
    title="Choose Your Own Adventure Game API",
    description="api to generate cool stories",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.info("[main.py] Registering routers...")
app.include_router(story.router, prefix=settings.API_PREFIX)
app.include_router(job.router, prefix=settings.API_PREFIX)
logging.info("[main.py] Routers registered. App startup complete.")

@app.get("/api/health")
def health():
    return {"status": "ok"}
