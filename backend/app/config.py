from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application settings.

    Values are loaded from environment variables or from a local .env file.
    """

    app_name: str = "NyayaSetu"
    app_env: str = "development"
    app_debug: bool = True

    # Groq LLM settings
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"
    groq_api_url: str = "https://api.groq.com/openai/v1/chat/completions"

    # Vector DB settings
    chroma_db_path: str = "app/data/vector_db"
    chroma_collection_name: str = "nyayasetu_legal_docs"

    # Embedding settings
    embedding_model_name: str = "intfloat/multilingual-e5-base"

    # RAG settings
    rag_top_k: int = 5
    rag_min_score: float = 0.20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()