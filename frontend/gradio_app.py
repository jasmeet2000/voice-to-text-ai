"""Gradio application for local transcription demo.

Features:
- Upload or record audio
- Select model
- Display transcription and allow download

Launch: python frontend/gradio_app.py
"""
from __future__ import annotations

import asyncio
import shutil
import uuid
from pathlib import Path
import gradio as gr
import sys

# Ensure project root is on sys.path so top-level packages import when running script directly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.validation_service import sanitize_filename
from core.config import get_settings
from core.logger import get_logger
from services.transcription_service import transcription_service
from models.model_registry import registry

settings = get_settings()
logger = get_logger()


def _transcribe_local(audio_path: str, model_name: str | None = None) -> str:
    if not audio_path:
        return "No audio provided"
    src = Path(audio_path)
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = sanitize_filename(src.name)
    dest = upload_dir / safe_name
    if dest.exists():
        dest = upload_dir / f"{dest.stem}_{uuid.uuid4().hex}{dest.suffix}"
    try:
        shutil.copy2(src, dest)
    except Exception as exc:
        logger.exception("Failed to copy audio to upload dir: %s", exc)
        return f"Error saving audio: {exc}"

    try:
        # transcription_service.transcribe_file is async
        result = asyncio.run(transcription_service.transcribe_file(dest, model_name=model_name))
        return result.get("text", "")
    except Exception as exc:
        logger.exception("Gradio transcription failed")
        return f"Error: {exc}"


def _get_models() -> list[str]:
    defaults = [settings.model_name, "openai/whisper-base", "distil-whisper/distil-small.en"]
    known = registry.list_models()
    seen: list[str] = []
    for m in (known + defaults):
        if m and m not in seen:
            seen.append(m)
    return seen


def main() -> None:
    with gr.Blocks() as demo:
        gr.Markdown("# Voice-to-Text (Gradio Demo)")
        with gr.Row():
            with gr.Column(scale=1):
                audio_input = gr.Audio(sources=["upload", "microphone"], type="filepath", label="Upload or record audio")
                model_dropdown = gr.Dropdown(choices=_get_models(), value=settings.model_name, label="Model")
                transcribe_btn = gr.Button("Transcribe")
            with gr.Column(scale=2):
                output_text = gr.Textbox(label="Transcription", lines=10)
                # gr.File triggers a gradio_client schema bug (bool not iterable).
                # Use a plain Textbox to surface the saved filepath instead.
                transcript_path = gr.Textbox(label="Saved transcript path", interactive=False)

        def _on_transcribe(audio, model):
            text = _transcribe_local(audio, model)
            # write transcript to temporary file for download
            temp = Path(settings.upload_dir) / f"transcript_{uuid.uuid4().hex}.txt"
            try:
                temp.write_text(text, encoding="utf-8")
                path_str = str(temp)
            except Exception:
                path_str = "(could not save transcript)"
            return text, path_str

        transcribe_btn.click(
            fn=_on_transcribe,
            inputs=[audio_input, model_dropdown],
            outputs=[output_text, transcript_path],
        )

    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)


if __name__ == "__main__":
    main()
