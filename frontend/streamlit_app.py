"""Streamlit dashboard for upload-based transcription demo.

Features:
- Upload audio, transcribe, and view/download transcripts
- Transcript history and basic system info

Launch: streamlit run frontend/streamlit_app.py
"""
from __future__ import annotations

import asyncio
import uuid
import platform
from pathlib import Path
import streamlit as st
import sys

# Ensure project root is on sys.path so top-level packages import when running script directly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.validation_service import sanitize_filename
from core.config import get_settings
from core.logger import get_logger
from services.transcription_service import transcription_service

settings = get_settings()
logger = get_logger()


def save_uploaded_file(uploaded_file) -> Path | None:
    if uploaded_file is None:
        return None
    fname = sanitize_filename(uploaded_file.name)
    dest = Path(settings.upload_dir) / fname
    if dest.exists():
        dest = Path(settings.upload_dir) / f"{dest.stem}_{uuid.uuid4().hex}{dest.suffix}"
    try:
        with dest.open("wb") as f:
            f.write(uploaded_file.getbuffer())
        return dest
    except Exception as exc:
        logger.exception("Failed to save uploaded file: %s", exc)
        return None


st.set_page_config(page_title="Voice-to-Text Dashboard")
st.title("Voice-to-Text Dashboard")

page = st.sidebar.selectbox("Page", ["Upload", "History", "System Info"])

if "history" not in st.session_state:
    st.session_state.history = []


if page == "Upload":
    st.header("Upload and Transcribe")
    uploaded = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a", "webm", "flac"]) 
    model = st.selectbox("Model", options=[settings.model_name, "openai/whisper-base", "distil-whisper/distil-small.en"])

    if uploaded is not None:
        st.audio(uploaded)
        if st.button("Transcribe"):
            dest = save_uploaded_file(uploaded)
            if dest is None:
                st.error("Failed to save uploaded file")
            else:
                with st.spinner("Transcribing..."):
                    try:
                        res = asyncio.run(transcription_service.transcribe_file(dest, model_name=model))
                        st.success("Transcription complete")
                        st.text_area("Transcript", value=res.get("text", ""), height=200)
                        st.download_button("Download transcript", data=res.get("text", ""), file_name=f"{dest.stem}.txt")
                        st.session_state.history.insert(0, {"file": dest.name, "text": res.get("text", ""), "model": res.get("model", "")})
                    except Exception as exc:
                        st.error(f"Transcription failed: {exc}")


if page == "History":
    st.header("Transcript History")
    for item in st.session_state.history:
        st.subheader(item["file"])
        st.write(item.get("model", ""))
        st.write(item.get("text", ""))
        st.markdown("---")


if page == "System Info":
    st.header("System Information")
    st.write({
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python": platform.python_version(),
        "default_model": settings.model_name,
        "device": settings.device,
    })


if __name__ == "__main__":
    pass
