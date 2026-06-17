"""Audio helpers: conversion and preprocessing utilities.

Functions are intentionally small and blocking; callers should run them in a threadpool
when used from async code (e.g., asyncio.to_thread).
"""

from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, Union

from core.config import get_settings
from core.exceptions import ValidationError
from core.logger import get_logger

settings = get_settings()
logger = get_logger()


def _configure_ffmpeg() -> None:
    """Ensure pydub can find the ffmpeg binary.

    Injects the winget FFmpeg bin dir into os.environ['PATH'] before pydub is
    first imported, so the pydub module-level check sees ffmpeg correctly.
    No-ops when ffmpeg is already on PATH.
    """
    try:
        # If ffmpeg is already on PATH, nothing to do.
        if shutil.which("ffmpeg"):
            return

        # Winget default install path on Windows.
        winget_base = Path(os.environ.get("LOCALAPPDATA", "")) / (
            "Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
        )
        candidates = sorted(winget_base.glob("*/bin"), reverse=True)
        if candidates:
            bin_dir = str(candidates[0])
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
            logger.debug("Injected ffmpeg bin into PATH: %s", bin_dir)
    except Exception as exc:
        logger.debug("Could not auto-configure ffmpeg path: %s", exc)


_configure_ffmpeg()


def convert_to_wav(
    input_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    sample_rate: Optional[int] = None,
) -> Path:
    """Convert arbitrary input audio to a mono WAV file at the target sample rate.

    Returns the path to the created WAV file. If output_path is not provided a temporary
    file will be created under settings.upload_dir with a unique name.

    Raises ValidationError on failure.
    """
    p = Path(input_path)
    sample_rate = sample_rate or settings.sample_rate

    if output_path:
        out = Path(output_path)
    else:
        out = Path(settings.upload_dir) / f"conv_{uuid.uuid4().hex}.wav"

    # Primary strategy: pydub (ffmpeg-backed) which supports many formats
    try:
        from pydub import AudioSegment  # optional dependency

        seg = AudioSegment.from_file(p)
        seg = seg.set_channels(1).set_frame_rate(int(sample_rate))
        seg.export(out, format="wav")
        logger.debug("Converted %s -> %s (sr=%s)", p, out, sample_rate)
        return out
    except Exception as exc:  # pragma: no cover - runtime dependency
        logger.debug("pydub conversion failed for %s: %s", p, exc)

    # Fallback: torchaudio if available
    try:
        import torchaudio

        waveform, sr = torchaudio.load(str(p))
        sr = int(sr)
        if sr != int(sample_rate):
            resampler = torchaudio.transforms.Resample(
                orig_freq=sr, new_freq=int(sample_rate)
            )
            waveform = resampler(waveform)
        torchaudio.save(str(out), waveform, int(sample_rate))
        logger.debug("Converted via torchaudio %s -> %s (sr=%s)", p, out, sample_rate)
        return out
    except Exception as exc:  # pragma: no cover - runtime dependency
        logger.exception("Audio conversion failed for %s", p)
        raise ValidationError("Failed to convert audio to WAV") from exc
