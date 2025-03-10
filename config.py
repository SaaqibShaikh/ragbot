from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"  # Changed model
    embedding_dimension: int = 384  # Updated dimension
    similarity_threshold: float = 0.5
    max_results: int = 5

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()