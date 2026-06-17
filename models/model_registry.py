"""ModelRegistry: manage available models, lazy-loading, and device allocation.

Provides a thin registry and convenience helpers for synchronous and async transcription calls.
"""
from __future__ import annotations

import threading
from typing import Dict, List, Optional

from core.config import get_settings
from core.logger import get_logger

from .whisper_model import WhisperModel, TranscriptionResult

logger = get_logger()
settings = get_settings()


class ModelRegistry:
    """Registry of WhisperModel instances.

    Models are lazily created on first access. The registry is thread-safe.
    """

    def __init__(self, default_model: Optional[str] = None, device: Optional[str] = None):
        self.default_model = default_model or settings.model_name
        self.device = device or settings.device
        self._models: Dict[str, WhisperModel] = {}
        self._lock = threading.RLock()

    def register(self, model_name: str) -> WhisperModel:
        """Register a model name and return its WhisperModel wrapper (does not force load)."""
        with self._lock:
            if model_name in self._models:
                return self._models[model_name]
            model = WhisperModel(model_name=model_name, device=self.device)
            self._models[model_name] = model
            logger.info("Registered model %s", model_name)
            return model

    def get(self, model_name: Optional[str] = None) -> WhisperModel:
        """Get a registered model, registering default if necessary."""
        name = model_name or self.default_model
        if name not in self._models:
            return self.register(name)
        return self._models[name]

    def list_models(self) -> List[str]:
        return list(self._models.keys())

    def transcribe(self, audio, model_name: Optional[str] = None, **kwargs) -> TranscriptionResult:
        model = self.get(model_name)
        return model.transcribe(audio, **kwargs)

    async def atranscribe(self, audio, model_name: Optional[str] = None, **kwargs) -> TranscriptionResult:
        model = self.get(model_name)
        return await model.atranscribe(audio, **kwargs)


# Module-level default registry for convenience
registry = ModelRegistry()

__all__ = ["ModelRegistry", "registry"]
