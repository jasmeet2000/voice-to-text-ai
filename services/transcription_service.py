"""TranscriptionService: orchestrates validation, preprocessing, model inference, and formatting.

This layer keeps business logic separate from FastAPI routes and the model implementation.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, Optional, Union

from core.config import get_settings
from core.exceptions import TranscriptionError
from core.logger import get_logger
from services.audio_service import convert_to_wav
from services.validation_service import validate_file_path

settings = get_settings()
logger = get_logger()


class TranscriptionService:
    """Orchestrates the full transcription pipeline for a single file.

    The model registry is imported lazily to avoid pulling heavy ML dependencies at module import.
    """

    def __init__(self, registry: Optional[Any] = None):
        self._registry = registry

    def _get_registry(self) -> Optional[Any]:
        if self._registry is None:
            try:
                from models.model_registry import registry as model_registry

                self._registry = model_registry
            except Exception as exc:  # pragma: no cover - runtime dependency
                logger.debug(
                    "Model registry not available in TranscriptionService: %s", exc
                )
                self._registry = None
        return self._registry

    async def transcribe_file(
        self,
        file_path: Union[str, Path],
        model_name: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Validate, preprocess, run inference, and format the transcription result.

        - file_path: path to uploaded file
        - model_name: optional model override
        - timeout: optional per-request timeout in seconds
        """
        p = Path(file_path)

        # Validation
        validate_file_path(p)

        # Preprocessing (blocking) — run in threadpool
        wav_path: Optional[Path] = None
        try:
            wav_path = await asyncio.to_thread(convert_to_wav, p)
        except Exception as exc:
            logger.exception("Audio preprocessing failed for %s", p)
            raise TranscriptionError("Audio preprocessing failed") from exc

        # Resolve registry lazily
        registry = self._get_registry()
        if registry is None:
            logger.error("No model registry available for transcription")
            raise TranscriptionError("Model registry unavailable")

        # Inference (async) with optional timeout
        try:
            start = perf_counter()
            coro = registry.atranscribe(str(wav_path), model_name)
            if timeout is not None:
                result = await asyncio.wait_for(coro, timeout=timeout)
            else:
                result = await coro
            duration = perf_counter() - start

            # Normalize result (supports TranscriptionResult dataclass from model layer)
            text = getattr(result, "text", None) or (
                result.raw.get("text") if getattr(result, "raw", None) else ""
            )
            segments = getattr(result, "segments", None)
            language = getattr(result, "language", None)

            logger.info(
                "Transcription completed in %.2fs for %s using model %s",
                duration,
                p.name,
                model_name or settings.model_name,
            )

            return {
                "text": text,
                "segments": segments,
                "language": language,
                "model": model_name or settings.model_name,
                "duration": duration,
            }
        except asyncio.TimeoutError as exc:
            logger.error("Transcription timed out for %s after %s seconds", p, timeout)
            raise TranscriptionError("Transcription timed out") from exc
        except Exception as exc:
            logger.exception("Transcription failed for %s", p)
            raise TranscriptionError("Transcription failed") from exc
        finally:
            # Attempt to remove temporary converted WAV if it was created under upload_dir
            try:
                if wav_path and wav_path.exists():
                    try:
                        upload_dir_resolved = Path(settings.upload_dir).resolve()
                        if (
                            wav_path.resolve().parent == upload_dir_resolved
                            and wav_path.resolve() != Path(p).resolve()
                        ):
                            wav_path.unlink(missing_ok=True)
                            logger.debug("Removed temporary wav %s", wav_path)
                    except Exception:
                        logger.debug("Unable to remove temporary wav %s", wav_path)
            except UnboundLocalError:
                pass


# Convenience singleton
transcription_service = TranscriptionService()

__all__ = ["TranscriptionService", "transcription_service"]
