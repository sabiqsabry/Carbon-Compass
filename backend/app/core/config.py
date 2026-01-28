from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore")

  # Database Configuration
  DATABASE_URL: str | None = None
  REDIS_URL: str | None = None

  # Supabase Configuration
  SUPABASE_URL: str | None = None
  SUPABASE_KEY: str | None = None

  # Application Settings
  ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
  DEBUG: bool = Field(default=True, description="Debug mode")

  # File Storage
  REPORTS_DIR: Path = Field(default=PROJECT_ROOT / "reports", description="Directory where PDF reports are stored")
  MAX_FILE_SIZE: int = Field(default=50 * 1024 * 1024, description="Maximum upload size in bytes (default 50MB)")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
  return Settings()

