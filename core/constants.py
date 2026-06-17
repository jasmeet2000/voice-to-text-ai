"""Constants for audio handling and default parameters."""
from __future__ import annotations

from typing import Set

# Supported audio file extensions (lowercase, including leading dot)
SUPPORTED_AUDIO_EXTENSIONS: Set[str] = {".wav", ".mp3", ".m4a", ".webm", ".flac"}

# Default sample rate for model input (Hz)
DEFAULT_SAMPLE_RATE: int = 16_000
