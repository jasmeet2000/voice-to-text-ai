"""WhisperModel: typed wrapper around Hugging Face automatic-speech-recognition pipeline.

Provides lazy-loading, device selection, and sync/async transcription helpers.
"""

from __future__ import annotations

import asyncio
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from transformers import Pipeline, pipeline
except Exception as exc:  # pragma: no cover - runtime dependency
    raise RuntimeError("transformers is required for model inference") from exc

from core.config import get_settings
from core.exceptions import ModelError, TranscriptionError
from core.logger import get_logger

logger = get_logger()
settings = get_settings()


@dataclass
class TranscriptionResult:
    text: str
    segments: Optional[List[Dict[str, Any]]] = None
    language: Optional[str] = None
    raw: Any = None


class WhisperModel:
    """Lightweight wrapper around a Hugging Face ASR pipeline.

    - Lazy-loads the model on first inference.
    - Respects DEVICE from config (cpu or cuda[:N]).
    - Exposes sync (transcribe) and async (atranscribe) APIs.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        chunk_length_s: int = 30,
    ):
        self.model_name = model_name or settings.model_name
        self.device = device or settings.device
        self.chunk_length_s = chunk_length_s
        self._pipe: Optional[Pipeline] = None
        self._lock = threading.Lock()

    def _device_id(self) -> int:
        dev = (self.device or "cpu").lower()
        if dev in ("cpu", "-1"):
            return -1
        if dev.startswith("cuda"):
            parts = dev.split(":")
            if len(parts) == 1:
                return 0
            try:
                return int(parts[1])
            except Exception:
                return 0
        return -1

    def _load(self) -> Pipeline:
        if self._pipe is None:
            with self._lock:
                if self._pipe is None:
                    try:
                        device_id = self._device_id()
                        logger.info(
                            "Loading model %s on device %s (device_id=%s)",
                            self.model_name,
                            self.device,
                            device_id,
                        )
                        self._pipe = pipeline(
                            "automatic-speech-recognition",
                            model=self.model_name,
                            device=device_id,
                            chunk_length_s=self.chunk_length_s,
                        )
                        logger.info("Model %s loaded", self.model_name)
                    except Exception as exc:
                        logger.exception("Failed to load model %s", self.model_name)
                        raise ModelError(
                            f"Failed to load model {self.model_name}"
                        ) from exc
        return self._pipe

    def transcribe(
        self, audio: Union[str, Path, bytes], **kwargs
    ) -> TranscriptionResult:
        """Synchronous (blocking) transcription.

        The pipe accepts a file path or raw audio if supported by the pipeline/backend.
        """
        pipe = self._load()
        try:
            # If it's a file path, load it natively to avoid HF pipeline ffmpeg subprocess crashing
            if isinstance(audio, (str, Path)) and Path(audio).is_file():
                import soundfile as sf

                audio_array, sr = sf.read(str(audio))
                # Convert to mono if stereo
                if len(audio_array.shape) > 1:
                    audio_array = audio_array.mean(axis=1)

                # HF pipeline accepts dict for raw arrays
                inference_input = {"array": audio_array, "sampling_rate": sr}
            else:
                inference_input = str(audio) if isinstance(audio, Path) else audio

            result = pipe(inference_input, **kwargs)

            # pipeline returns a dict with at least 'text'
            text = result.get("text", "") if isinstance(result, dict) else str(result)
            segments = result.get("chunks") if isinstance(result, dict) else None
            language = result.get("language") if isinstance(result, dict) else None
            return TranscriptionResult(
                text=text, segments=segments, language=language, raw=result
            )
        except Exception as exc:
            logger.exception("Transcription failed for %s", audio)
            raise TranscriptionError("Transcription failed") from exc

    async def atranscribe(
        self, audio: Union[str, Path, bytes], **kwargs
    ) -> TranscriptionResult:
        """Async wrapper that runs transcription in a threadpool."""
        return await asyncio.to_thread(self.transcribe, audio, **kwargs)


__all__ = ["WhisperModel", "TranscriptionResult"]
