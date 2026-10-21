from pathlib import Path

from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Supabase (Auth + hosted Postgres) — required in real mode ---
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None

    # --- Postgres (Alembic + direct DB access) ---
    database_url: str = "postgresql://doccopilot:doccopilot@localhost:5432/document_copilot"

    # --- OpenAI (LLM + embeddings) — required in real mode ---
    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dimensions: int = 1536
    openai_chat_model: str = "gpt-4.1"
    openai_grounding_model: str = "gpt-4.1-mini"
    openai_agent_request_limit: int = 20
    openai_agent_temperature: float = 0.0

    # --- Retrieval (hybrid search defaults) ---
    retrieval_candidate_k: int = 50
    retrieval_top_k: int = 10
    retrieval_rrf_k: int = 60
    retrieval_neighbor_radius: int = 1
    retrieval_fts_config: str = "english"
    retrieval_fts_keyword_model: str = "gpt-4.1-mini"
    retrieval_fts_keyword_min: int = 3
    retrieval_fts_keyword_max: int = 5
    retrieval_fts_keyword_fast_path_tokens: int = 5

    # --- Server ---
    allowed_origins: str = "http://localhost:5173"

    # --- Demo mode ---
    # None (unset) = auto-detect: demo when Supabase or OpenAI keys are missing.
    demo_mode: bool | None = None
    demo_jwt_secret: str = "document-copilot-demo-secret-change-me"

    @field_validator(
        "supabase_url",
        "supabase_anon_key",
        "supabase_service_role_key",
        "openai_api_key",
        mode="before",
    )
    @classmethod
    def _empty_str_to_none(cls, value: object) -> object:
        """Treat empty env values as unset so demo-mode auto-detection works."""
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @computed_field
    @property
    def is_demo(self) -> bool:
        if self.demo_mode is not None:
            return self.demo_mode
        return self.openai_api_key is None or self.supabase_url is None

    @computed_field
    @property
    def sqlalchemy_database_url(self) -> str:
        """Normalize postgres URLs for SQLAlchemy + psycopg v3."""
        url = self.database_url
        if url.startswith("postgresql+psycopg://"):
            return url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+psycopg://", 1)
        return url

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
