from sqlalchemy import create_engine
from core.config import settings

engine = create_engine(settings.DATABASE_URL)

try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print("Connection failed:", e)