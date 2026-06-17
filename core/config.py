"""Configuration management without pydantic BaseSettings.

Loads environment from a .env file (python-dotenv) and returns a cached Settings instance.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Load .env early
load_dotenv()


@dataclass
class Settings:
    model_name: str = "openai/whisper-small"
    device: str = "cpu"
    max_file_size: int = 104_857_600  # 100 MB
    upload_dir: str = "uploads"
    log_dir: str = "logs"
    log_level: str = "INFO"
    host: str = "127.0.0.1"
    port: int = 8000
    sample_rate: int = 16_000


def _int_env(name: str, default: int) -> int:
    v = os.getenv(name)
    if v is None or v == "":
        return default
    try:
        return int(v)
    except ValueError:
        return default


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance and ensure required folders exist."""
    s = Settings(
        model_name=os.getenv("MODEL_NAME", Settings.model_name),
        device=os.getenv("DEVICE", Settings.device),
        max_file_size=_int_env("MAX_FILE_SIZE", Settings.max_file_size),
        upload_dir=os.getenv("UPLOAD_DIR", Settings.upload_dir),
        log_dir=os.getenv("LOG_DIR", Settings.log_dir),
        log_level=os.getenv("LOG_LEVEL", Settings.log_level),
        host=os.getenv("HOST", Settings.host),
        port=_int_env("PORT", Settings.port),
        sample_rate=_int_env("SAMPLE_RATE", Settings.sample_rate),
    )

    # Ensure directories exist
    Path(s.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(s.log_dir).mkdir(parents=True, exist_ok=True)

    return s


# Convenience alias
settings: Settings = get_settings()
