# context.md

Short cheat sheet

API routes
- GET  /health
- POST /upload (multipart form) — returns {filename, size}
- POST /transcribe (JSON) — {"filename": "uploaded.wav", "model": "optional", "timeout": 30}
- GET  /models — lists registered models

Folder structure
- api/, services/, models/, core/, frontend/, tests/, uploads/, logs/, docs/, .github/

Model names (candidates)
- openai/whisper-base          (lighter, faster)
- openai/whisper-small         (default — best accuracy/speed balance)
- distil-whisper/distil-small.en  (English-only, fastest on CPU)

Environment variables
- MODEL_NAME, DEVICE (cpu|cuda), MAX_FILE_SIZE, UPLOAD_DIR, LOG_DIR, LOG_LEVEL, HOST, PORT, SAMPLE_RATE

Common commands
- Start API server:      uvicorn api.routes:app --reload --host 127.0.0.1 --port 8000
- Gradio demo:           python frontend/gradio_app.py         → http://127.0.0.1:7860
- Streamlit dashboard:   streamlit run frontend/streamlit_app.py
- Run tests:             pytest -q
- Linting:               ruff check . && black --check . && isort --check-only .

Known compatibility constraints (IMPORTANT)
- Python runtime: 3.9 (not 3.11 as originally planned)
- FastAPI must be <0.115.0 (pinned to 0.114.x) — required by Gradio 4.44.1
- Pydantic must be >=2.0 — do NOT downgrade; Gradio 4.44.1 requires it
- FFmpeg must be installed system-wide — pydub won't work without it
- Gradio must bind to 127.0.0.1 (not 0.0.0.0) in this environment
- gradio_client/utils.py has been patched to fix a boolean-schema TypeError with Pydantic v2

Coding conventions
- Python typing everywhere
- Single Responsibility per module
- No files >200 LOC where practical

Quick habits to save tokens
- Read docs/memory.md first
- Read docs/context.md second
- Load only relevant files for a change
- Update docs/memory.md after phase completion

Phase
- Current: Phase 11 (Bug Fixes & Runtime Compatibility) — all services running
- Next: Phase 12 (Benchmarking, ONNX optimization, Docker hardening)
