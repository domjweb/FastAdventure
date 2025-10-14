from typing import List, ClassVar
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    # Example: postgresql+psycopg2://username:password@host:5432/dbname
    DATABASE_URL: str = "postgresql+psycopg2://user:password@localhost:5432/fastadventure"
    ALLOWED_ORIGINS: str = ""
    OPENAI_API_KEY: str

    @field_validator("ALLOWED_ORIGINS")
    def parse_allowed_origins(cls, v: str) -> List[str]:
        return v.split(",") if v else []
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()
