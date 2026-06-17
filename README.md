# Check the live link before you read this file

https://jasmeet2000-voice-to-text-ai-frontendstreamlit-app-8xfcrg.streamlit.app/


# Voice-to-Text App

Production-ready, offline voice-to-text using Hugging Face Whisper variants.

## Quickstart

### 1. Prerequisites

- Python 3.9+
- **FFmpeg** (required for audio conversion)
  - Windows: `winget install --id Gyan.FFmpeg -e`
  - macOS: `brew install ffmpeg`
  - Linux: `apt install ffmpeg`

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note on package versions:** Gradio 4.44.x requires `fastapi<0.115.0` and `pydantic>=2.0`.
> The `requirements.txt` does not pin these, so if you encounter issues run:
> ```bash
> pip install "fastapi<0.115.0"
> ```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env as needed (MODEL_NAME, DEVICE, etc.)
```

### 4. Start services

**FastAPI backend:**
```bash
uvicorn api.routes:app --reload --host 127.0.0.1 --port 8000
```

**Gradio demo** (http://127.0.0.1:7860):
```bash
python frontend/gradio_app.py
```
> First launch is slow (~5–7 min) because PyTorch + Transformers must load model weights from Hugging Face.

**Streamlit dashboard** (http://localhost:8501):
```bash
streamlit run frontend/streamlit_app.py
```

---

## Features

- Upload audio files (wav, mp3, m4a, webm, flac)
- Local offline model inference using Hugging Face Whisper variants
- Gradio demo and Streamlit dashboard frontends
- REST API: `/health`, `/upload`, `/transcribe`, `/models`
- Structured logging with Loguru
- Configurable via `.env`

---

## Architecture & Tech Stack

- **Clean Architecture**: Presentation → API → Service → Model → Domain
- **FastAPI + Pydantic v2** for the HTTP layer
- **Hugging Face Transformers** for model inference (`openai/whisper-small` default)
- **PyTorch** for inference runtime; ONNX export available for CPU optimization
- **FFmpeg** (via pydub) for audio format conversion
- **Gradio** and **Streamlit** for lightweight frontends

See `docs/architecture_design.md` and `docs/technology_selection.md` for details.

---

## API Examples

**Check health:**
```bash
curl http://127.0.0.1:8000/health
```

**Upload a file:**
```bash
curl -F "file=@path/to/audio.wav" http://127.0.0.1:8000/upload
```

**Transcribe:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"filename":"audio.wav"}' \
  http://127.0.0.1:8000/transcribe
```

**Python example:**
```python
import requests

r = requests.post('http://127.0.0.1:8000/upload', files={'file': open('audio.wav','rb')})
filename = r.json()['filename']

r2 = requests.post('http://127.0.0.1:8000/transcribe', json={'filename': filename})
print(r2.json()['text'])
```

---

## Model Options

| Model | Speed | Accuracy | Notes |
|---|---|---|---|
| `openai/whisper-base` | Fast | Moderate | Lowest RAM |
| `openai/whisper-small` | Moderate | Good | **Default** |
| `distil-whisper/distil-small.en` | Fastest | Good (EN only) | CPU-optimized |

Set via `MODEL_NAME=openai/whisper-small` in `.env`.

---

## Development

**Run tests:**
```bash
pip install -r requirements-test.txt
pytest -q
```

**Lint:**
```bash
ruff check . && black --check . && isort --check-only .
```

**Pre-commit:**
```bash
pre-commit install
pre-commit run --all-files
```

---

## Docker (local)

```bash
docker build -t voice-to-text-app .
docker run -p 8000:8000 --env-file .env voice-to-text-app
```

> Note: FFmpeg must be installed inside the Docker image. The Dockerfile includes a placeholder — update it to `RUN apt-get install -y ffmpeg` for production use.

---

## Known Issues & Compatibility

| Issue | Resolution |
|---|---|
| `gr.Audio(source=...)` TypeError | Fixed — uses `sources=[...]` list (Gradio 4.x API) |
| `gr.File` schema crash (gradio_client bool TypeError) | Fixed — patched `gradio_client/utils.py` |
| `st.experimental_rerun()` AttributeError | Fixed — removed (deprecated in Streamlit 1.35+) |
| `fastapi>0.115` incompatible with Gradio 4.44.1 | Fixed — pinned `fastapi<0.115.0` |
| Slow startup (~5–7 min) | Expected — torch/transformers model loading |
| FFmpeg not found → Transcription failed | Fixed — install FFmpeg system-wide (see Prerequisites) |

---

## Project Structure

```
voice-to-text-app/
├── api/          # FastAPI routes, schemas, dependencies
├── services/     # Validation, audio conversion, transcription orchestration
├── models/       # WhisperModel wrapper and ModelRegistry
├── core/         # Config, logging, exceptions
├── frontend/     # gradio_app.py, streamlit_app.py
├── tests/        # Unit and integration tests (pytest)
├── uploads/      # Uploaded audio files
├── logs/         # Application logs
├── docs/         # Architecture docs and cheat-sheets
└── .github/      # CI workflows
```

See `docs/repository_structure.md` for full details.

---

## Phases

| Phase | Status |
|---|---|
| 1 Architecture Design | ✅ Complete |
| 2 Project Scaffold | ✅ Complete |
| 3 Configuration | ✅ Complete |
| 4 Model Layer | ✅ Complete |
| 5 Service Layer | ✅ Complete |
| 6 FastAPI Layer | ✅ Complete |
| 7 Frontend | ✅ Complete |
| 8 Tests & CI | ✅ Complete |
| 9 CI & Quality | ✅ Complete |
| 10 Docker & Docs | ✅ Complete |
| 11 Bug Fixes & Compatibility | ✅ Complete |
| 12 Benchmarking & ONNX | 🔲 Pending |
