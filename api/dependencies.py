"""FastAPI dependency providers (settings, registry, logger).

Note: model and service imports are lazy to avoid heavy ML deps at import time.
"""
from __future__ import annotations

from importlib import import_module
from typing import Optional, Any

from core.config import get_settings
from core.logger import get_logger


def get_settings_dep():
    return get_settings()


def get_logger_dep():
    return get_logger()


def get_registry_dep() -> Optional[Any]:
    """Lazily import and return the model registry, or None if unavailable."""
    try:
        mod = import_module("models.model_registry")
        return getattr(mod, "registry", None)
    except Exception as exc:  # pragma: no cover - defensive
        logger = get_logger()
        logger.debug("Model registry not available: %s", exc)
        return None


def get_transcription_service_dep() -> Optional[Any]:
    """Lazily import and return the transcription_service singleton, or None."""
    try:
        mod = import_module("services.transcription_service")
        return getattr(mod, "transcription_service", None)
    except Exception as exc:  # pragma: no cover - defensive
        logger = get_logger()
        logger.debug("Transcription service not available: %s", exc)
        return None
