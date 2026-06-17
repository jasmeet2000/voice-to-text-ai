"""Validation utilities for uploaded audio files.

Provides simple, testable checks for file existence, size, extension, and optional integrity check.
"""
from __future__ import annotations

from pathlib import Path
from typing import Union
import re

from core.config import get_settings
from core.constants import SUPPORTED_AUDIO_EXTENSIONS
from core.logger import get_logger
from core.exceptions import ValidationError

settings = get_settings()
logger = get_logger()


def sanitize_filename(filename: str) -> str:
    """Return a safe filename by stripping path components and replacing invalid chars.

    Keeps ASCII letters, digits, dot, underscore, and hyphen. Removes leading dots.
    """
    name = Path(filename).name
    # normalize spaces
    name = name.replace(" ", "_")
    # allow only a-z, A-Z, 0-9, dot, underscore, hyphen
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    # strip leading dots to avoid hidden files
    name = name.lstrip(".")
    if not name:
        name = "file"
    # limit length to avoid filesystem issues
    if len(name) > 200:
        base, dot, ext = name.rpartition(".")
        if dot:
            base = base[:190]
            name = f"{base}.{ext}"
        else:
            name = name[:200]
    return name


def validate_file_path(file_path: Union[str, Path], check_integrity: bool = True) -> None:
    """Validate an uploaded file path.

    Raises ValidationError if the file is missing, empty, too large, has an unsupported
    extension, or (optionally) fails a lightweight integrity check.
    """
    p = Path(file_path)
    if not p.exists():
        raise ValidationError(f"File not found: {p}")
    if not p.is_file():
        raise ValidationError(f"Not a file: {p}")

    size = p.stat().st_size
    if size == 0:
        raise ValidationError("Empty file")
    if size > settings.max_file_size:
        raise ValidationError(f"File exceeds maximum size ({settings.max_file_size} bytes)")

    if p.suffix.lower() not in SUPPORTED_AUDIO_EXTENSIONS:
        raise ValidationError(f"Unsupported file extension: {p.suffix}")

    if check_integrity:
        # Do a lightweight attempt to open the file using pydub to detect obvious corruption.
        try:
            from pydub import AudioSegment  # optional dependency

            AudioSegment.from_file(p)
        except Exception as exc:  # pragma: no cover - runtime dependency
            logger.error("Audio integrity check failed for %s: %s", p, exc)
            raise ValidationError("Audio file appears corrupt or unsupported") from exc
