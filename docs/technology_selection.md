# Technology Selection

Core choices
- Python 3.9 (runtime; 3.11+ recommended for production)
- FastAPI <0.115.0: async-first API with robust validation; pinned for Gradio 4.44.x compatibility
- Uvicorn (ASGI): production server for FastAPI
- Loguru: structured logging
- python-dotenv: environment-driven config (lightweight)
- Pydantic v2 (>=2.0): required by Gradio 4.44.x; do NOT downgrade
- transformers (Hugging Face) + tokenizers
- PyTorch for model runtime; ONNX for CPU-optimized inference when necessary
- FFmpeg (system dependency, required) for format handling via pydub wrapper

Audio libs
- pydub (ffmpeg-backed) for broad format support — requires ffmpeg system binary
- torchaudio for fallback loading and resampling when pydub is unavailable

Model candidates (summary)
- openai/whisper-base
  - Accuracy: moderate
  - Speed: faster than small
  - RAM: lower footprint
  - Use when: tight RAM/CPU constraints and accuracy can be relaxed

- openai/whisper-small  ← DEFAULT
  - Accuracy: better than base
  - Speed: moderate
  - RAM: higher than base (recommended for demos)
  - Use when: balanced accuracy vs latency

- distil-whisper/distil-small.en
  - Accuracy: slightly lower (English-only)
  - Speed: fastest on CPU
  - RAM: smaller footprint
  - Use when: English-only, CPU-constrained environments

Default model recommendation
- Default: openai/whisper-small — best balance of accuracy and usability.
  Use distil-whisper for English-only CPU-limited setups; whisper-base for minimal-resource use.

Dependency compatibility matrix (as of 2026-06-16)
- Gradio 4.44.1 requires: pydantic>=2.0, fastapi<0.115.0, starlette<0.39.0
- gradio_client 0.6.x has a bug with Pydantic v2 boolean JSON schemas — patched in site-packages
- Python 3.9 works; Python 3.11+ recommended for production for better performance

Notes on config
- Configuration uses python-dotenv and a small Settings dataclass (not pydantic BaseSettings).
  Consider adopting pydantic-settings in a future phase.

Performance tuning
- For CPU-only deployments, export model to ONNX and apply int8 quantization.
- Benchmark on representative hardware: peak memory, latency per minute of audio, throughput.
- torch + transformers import adds ~5–7 min startup on constrained hardware; lazy-load everything.

Security & license
- Verify model license before redistribution; document licenses in README and LICENSE.
- Never commit .env or model weights to version control.
