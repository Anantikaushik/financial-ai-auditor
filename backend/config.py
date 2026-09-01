from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application configuration."""

    APP_NAME: str = "Financial AI Auditor"

    DATABASE_PATH: str = str(
        BASE_DIR / "data" / "financial_auditor.duckdb"
    )

    RAW_DATA_DIR: str = str(
        BASE_DIR / "data" / "raw"
    )

    PROCESSED_DATA_DIR: str = str(
        BASE_DIR / "data" / "processed"
    )

    SAMPLE_DATA_DIR: str = str(
        BASE_DIR / "data" / "sample"
    )

    VLM_PROVIDER: str = "groq"

    VLM_API_KEY: str = ""

    VLM_MODEL: str = "qwen/qwen3.6-27b"

    MAX_FILE_SIZE_MB: int = 25

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()