"""Environment-driven application settings for the scaffolded architecture."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "production"
    debug: bool = False

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 2
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    database_url: str = "******postgres:5432/eco_ia"
    redis_url: str = "redis://redis:6379/0"

    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""

    prometheus_port: int = 9090
    grafana_port: int = 3000

    backup_retention_days: int = 30
    max_brute_force_attempts: int = 10
    auto_block_intruders: bool = True

    @property
    def agents_config_path(self) -> Path:
        return BASE_DIR / "config" / "agents_config.yaml"


settings = Settings()
