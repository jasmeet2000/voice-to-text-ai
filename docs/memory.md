# memory.md

Project Vision
- Build a production-ready, offline voice-to-text app using Hugging Face Whisper variants and Clean Architecture.

Architecture Decisions
- Clean Architecture (Presentation, Application, Domain, Infrastructure)
- Layered inference pipeline (API → Service → Model → Response)
- Dependency injection and small modules (~<=200 LOC) for testability and low token load

Tech Stack
- Python 3.9 (installed runtime; note: docs previously said 3.11+ — actual env is 3.9)
- FastAPI 0.114.x + Starlette 0.38.x (pinned to be compatible with Gradio 4.44.1)
- Uvicorn, Loguru, python-dotenv
- Hugging Face Transformers + PyTorch; optional ONNX for CPU optimization
- Audio: ffmpeg (via pydub), torchaudio fallback
- Frontend: Gradio 4.44.1 (demo) & Streamlit (dashboard)
- Pydantic v2 (2.13.x) — NOTE: do NOT downgrade below v2; Gradio 4.44.1 requires it

Current Progress
- Phase 1: Architecture Design — complete
- Phase 2: Project Scaffold — complete (repo skeleton, docs, stubs)
- Phase 3: Configuration — complete (core/config, core/logger)
- Phase 4: Model Layer — implemented (models/whisper_model.py, models/model_registry.py, lazy loading, sync/async API)
- Phase 5: Service Layer — implemented (validation, audio conversion, transcription orchestration)
- Phase 6: FastAPI Layer — implemented (/health, /upload, /transcribe, /models) with DI and path safety
- Phase 7: Frontend — Gradio and Streamlit apps running under frontend/
- Phase 8: Tests — unit tests for validation and API; CI workflow added; 7 passing, 2 skipped (placeholders)
- Phase 9: CI & Quality — pre-commit, ruff, black, isort, GitHub Actions CI
- Phase 10: Docker & Docs — Dockerfile and docker-compose placeholders; README and docs updated
- Phase 11: Bug Fixes & Compatibility — all runtime bugs resolved; all services confirmed running

Pending Tasks
- Model benchmarking and ONNX export/quantization for CPU inference
- GPU support and optimized Docker images (CUDA)
- Full inference integration tests (heavy; optional CI job)
- Frontend refinements: in-browser recording, UI polish, history persistence
- Documentation: screenshots, architecture diagram, API examples expansion
- Upgrade runtime to Python 3.11+ for better performance

Known Issues / Constraints
- Offline constraint: trade-offs between model size and latency
- Requires ffmpeg for many audio formats (pydub dependency)
- torch + transformers imports are slow (~5-7 min on dev machine); use lazy loading wherever possible
- Gradio 4.44.1 has a gradio_client schema-parsing bug with Pydantic v2 boolean schemas:
    PATCHED in: gradio_client/utils.py — get_type() guards isinstance(schema, dict);
                additionalProperties bool check added before recursion
- gr.Audio(source=...) kwarg is deprecated in Gradio 4.x — use sources=[...] instead
- st.experimental_rerun() removed in Streamlit 1.35+ — replaced with pass
- Gradio must bind to 127.0.0.1 (not 0.0.0.0) in this environment
- FastAPI must be <0.115.0 for Gradio 4.44.1 compatibility (pinned to 0.114.x)

Lessons Learned
- Small, focused files improve reviewability and reduce token usage.
- Capture project state in memory.md to avoid repeating decisions.
- Always test frontend dependencies together — Gradio, FastAPI, and Pydantic versions interact.
- torch/transformers import time is significant; account for it in startup latency expectations.
