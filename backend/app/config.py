"""
Application configuration using Pydantic Settings.
Loads from environment variables and .env file.
"""
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the project root directory (parent of backend/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "AI-Avangard"
    app_version: str = "1.0.0"
    debug: bool = False
    api_prefix: str = "/api/v1"

    # Database - PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "ai_avangard"
    postgres_user: str = "ai_avangard_admin"
    postgres_password: str = Field(..., description="PostgreSQL password")
    postgres_pool_size: int = 20
    postgres_max_overflow: int = 0

    @property
    def database_url(self) -> str:
        """Build PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        """Build sync PostgreSQL connection URL for Alembic."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0
    redis_max_connections: int = 50

    @property
    def redis_url(self) -> str:
        """Build Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "ai_avangard_main"
    qdrant_api_key: str = ""

    # Security
    jwt_secret_key: str = Field(..., description="JWT secret key")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 480  # 8 hours
    secret_key: str = Field(..., description="Additional secret key")

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # OpenAI
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_embedding_model: str = "text-embedding-3-large"
    openai_embedding_dimensions: int = 3072
    openai_llm_model: str = "gpt-4o"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.3
    openai_timeout: int = 30

    # Together AI (Qwen)
    together_api_key: str = Field(default="", description="Together AI API key")
    together_model: str = "Qwen/Qwen3-235B-A22B-Instruct-2507-FP8"
    together_base_url: str = "https://api.together.xyz/v1"
    use_together: bool = True  # Use Together AI as primary LLM


    # User Quotas
    free_user_max_documents: int = 10
    free_user_max_queries_daily: int = 100
    max_file_size_mb: int = 10
    allowed_extensions: list[str] = [".pdf", ".txt", ".md"]

    # System Capacity
    max_total_users: int = 100
    max_total_documents: int = 500

    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: str = "logs/backend.log"

    # File Storage
    upload_dir: str = "/home/temrjan/znai-cloud/uploads"

    # Admin
    admin_email: str = "admin@znai.cloud"
    admin_password: str = "changeme"
    admin_full_name: str = "System Administrator"

    # Telegram Notifications
    telegram_bot_token: str = ""
    telegram_owner_chat_id: str = ""


# Global settings instance
settings = Settings()
