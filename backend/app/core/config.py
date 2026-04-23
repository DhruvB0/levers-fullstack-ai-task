from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    chroma_host: str = "chromadb"
    chroma_port: int = 8000
    chroma_collection_name: str = "debt_collection_docs"
    embedding_model: str = "text-embedding-3-small"
    seed_data_path: str = "/app/rag-reference-data"
    top_k_results: int = 5
    max_completion_tokens: int = 1000
    cors_origins: str = "http://localhost:3000"
    max_context_chars: int = 12000

    model_config = {"env_file": ".env"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
