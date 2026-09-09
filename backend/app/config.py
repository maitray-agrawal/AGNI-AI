from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "AGNI-AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000

    # Local Inference
    MODEL_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    DEFAULT_TIMEOUT_SECONDS: int = 180

    # Configured Models
    REASONING_MODEL: str = "llama3.1:8b"
    CODING_MODEL: str = "qwen2.5-coder:7b"
    VISION_MODEL: str = "moondream"
    GENERAL_MODEL: str = "mistral:latest"

    # Storage Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    OUTPUT_DIR: Path = BASE_DIR / "outputs"
    QDRANT_PATH: Path = BASE_DIR / "data" / "qdrant_storage"
    AUDIT_DB_PATH: Path = BASE_DIR / "outputs" / "audit.db"


settings = Settings()

# Ensure mandatory directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
settings.QDRANT_PATH.mkdir(parents=True, exist_ok=True)
