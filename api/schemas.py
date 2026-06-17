"""Pydantic request/response schemas for API endpoints."""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class HealthResponse(BaseModel):
    status: str = Field("ok")


class UploadResponse(BaseModel):
    filename: str
    size: int
    message: Optional[str] = None


class TranscriptionRequest(BaseModel):
    filename: str
    model: Optional[str] = None
    timeout: Optional[float] = Field(None, description="Per-request timeout in seconds")


class TranscriptionResponse(BaseModel):
    text: str
    segments: Optional[List[Dict[str, Any]]]
    language: Optional[str]
    model: str
    duration: float


class ModelInfo(BaseModel):
    name: str
    loaded: bool


__all__ = [
    "HealthResponse",
    "UploadResponse",
    "TranscriptionRequest",
    "TranscriptionResponse",
    "ModelInfo",
]
