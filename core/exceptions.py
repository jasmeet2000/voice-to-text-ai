"""Application-specific exceptions used across the project."""


class ApplicationError(Exception):
    """Base class for application-specific errors."""


class ValidationError(ApplicationError):
    """Raised when input validation fails."""


class ModelError(ApplicationError):
    """Raised when model loading or runtime errors occur."""


class TranscriptionError(ApplicationError):
    """Raised when transcription fails."""


__all__ = ["ApplicationError", "ValidationError", "ModelError", "TranscriptionError"]
