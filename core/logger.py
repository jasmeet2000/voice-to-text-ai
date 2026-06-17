"""Loguru configuration for application and error logs.

Creates rotating sinks under configured log_dir and exposes the logger.
"""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from .config import get_settings

settings = get_settings()

log_dir = Path(settings.log_dir)
log_dir.mkdir(parents=True, exist_ok=True)

# Remove default handler added by Loguru
logger.remove()

# Console (stderr) for development
logger.add(
    sys.stderr,
    level=settings.log_level,
    colorize=True,
    enqueue=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - {message}",
)

# Application log (info+)
logger.add(
    log_dir / "application.log",
    level=settings.log_level,
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    enqueue=True,
    backtrace=True,
    diagnose=False,
)

# Error-only log
logger.add(
    log_dir / "error.log",
    level="ERROR",
    rotation="10 MB",
    retention="90 days",
    compression="zip",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)


def get_logger() -> logger.__class__:
    """Return the configured Loguru logger."""
    return logger
