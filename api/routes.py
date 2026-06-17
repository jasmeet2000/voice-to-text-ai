"""FastAPI routes for the voice-to-text service."""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import List, Any, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse

from api.schemas import (
    HealthResponse,
    UploadResponse,
    TranscriptionRequest,
    TranscriptionResponse,
    ModelInfo,
)
from api.dependencies import (
    get_settings_dep,
    get_registry_dep,
    get_logger_dep,
    get_transcription_service_dep,
)
from core.exceptions import ValidationError, TranscriptionError
from services.validation_service import validate_file_path, sanitize_filename

settings = get_settings_dep()
logger = get_logger_dep()

app = FastAPI(title="Voice-to-Text API", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse()


@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    # Save uploaded file to configured upload directory
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize filename and ensure we don't allow traversal via filename
    safe_name = sanitize_filename(file.filename or "upload")
    dest = upload_dir / safe_name

    # Ensure unique filename to avoid accidental overwrite
    if dest.exists():
        stem = dest.stem
        suffix = dest.suffix
        dest = upload_dir / f"{stem}_{uuid.uuid4().hex}{suffix}"

    try:
        with dest.open("wb") as f:
            shutil.copyfileobj(file.file, f)
    finally:
        file.file.close()

    # Ensure destination is inside upload_dir (defense-in-depth)
    try:
        if not dest.resolve().is_relative_to(upload_dir.resolve()):
            dest.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail="Invalid upload path")
    except AttributeError:
        # Older pathlib fallback
        if upload_dir.resolve() not in dest.resolve().parents and dest.resolve() != upload_dir.resolve():
            dest.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail="Invalid upload path")

    # Validate saved file
    try:
        validate_file_path(dest)
    except ValidationError as exc:
        try:
            dest.unlink(missing_ok=True)
        except Exception:
            pass
        raise HTTPException(status_code=400, detail=str(exc))

    logger.info("Uploaded file %s (%s bytes)", dest.name, dest.stat().st_size)
    return UploadResponse(filename=dest.name, size=dest.stat().st_size, message="Uploaded")


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(req: TranscriptionRequest, transcription_service: Any = Depends(get_transcription_service_dep)):
    if transcription_service is None:
        raise HTTPException(status_code=503, detail="Transcription service unavailable")

    upload_dir_path = Path(settings.upload_dir).resolve()
    # Build a safe path inside the upload dir
    try:
        file_path = (upload_dir_path / req.filename).resolve()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # Ensure file is within upload directory
    try:
        if not file_path.is_relative_to(upload_dir_path):
            raise HTTPException(status_code=400, detail="Invalid filename or path")
    except AttributeError:
        if upload_dir_path not in file_path.parents and file_path != upload_dir_path:
            raise HTTPException(status_code=400, detail="Invalid filename or path")

    # Delegate to service (transcription_service will validate file)
    try:
        result = await transcription_service.transcribe_file(file_path, model_name=req.model, timeout=req.timeout)
        return TranscriptionResponse(**result)
    except TranscriptionError as exc:
        logger.error("TranscriptionError: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except ValidationError as exc:
        logger.error("ValidationError: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/models", response_model=List[ModelInfo])
async def list_models(registry: Optional[Any] = Depends(get_registry_dep)):
    if registry is None:
        return []
    models = registry.list_models()
    infos = [ModelInfo(name=name, loaded=(getattr(registry.get(name), "_pipe", None) is not None)) for name in models]
    return infos


# Mount static pages for quick frontend demo
@app.get("/")
async def root():
    return JSONResponse({"message": "Voice-to-Text API. See /docs for API UI."})
