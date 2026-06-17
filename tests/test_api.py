import sys
import types
import io
from pathlib import Path

from fastapi.testclient import TestClient


def _make_fake_registry_module():
    m = types.ModuleType("models.model_registry")

    class DummyReg:
        def list_models(self):
            return []

        def get(self, name=None):
            class DummyModel:
                _pipe = None

                async def atranscribe(self, audio, model_name=None, **kwargs):
                    class R:
                        def __init__(self):
                            self.text = "hello world"
                            self.segments = None
                            self.language = "en"
                            self.raw = {"text": "hello world"}

                    return R()

                def transcribe(self, audio, model_name=None, **kwargs):
                    class R:
                        def __init__(self):
                            self.text = "hello world"
                            self.segments = None
                            self.language = "en"
                            self.raw = {"text": "hello world"}

                    return R()

            return DummyModel()

        async def atranscribe(self, audio, model_name=None, **kwargs):
            class R:
                def __init__(self):
                    self.text = "hello world"
                    self.segments = None
                    self.language = "en"
                    self.raw = {"text": "hello world"}

            return R()

    m.registry = DummyReg()
    return m


def test_health(monkeypatch):
    fake = _make_fake_registry_module()
    monkeypatch.setitem(sys.modules, "models.model_registry", fake)

    # import after stubbing heavy model modules
    from api.routes import app

    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_upload_file(monkeypatch, tmp_path):
    fake = _make_fake_registry_module()
    monkeypatch.setitem(sys.modules, "models.model_registry", fake)

    from api import routes

    # stub validation to avoid pydub/ffmpeg in test environment
    monkeypatch.setattr(routes, "validate_file_path", lambda p: None)

    client = TestClient(routes.app)
    file_content = b"FAKEAUDIOBYTES"
    files = {"file": ("test.wav", io.BytesIO(file_content), "audio/wav")}
    r = client.post("/upload", files=files)
    assert r.status_code == 200
    data = r.json()
    # Filename should be sanitized and end with the original extension
    assert data["filename"].endswith(".wav")

    # cleanup and ensure file exists
    upload_path = Path(routes.settings.upload_dir) / data["filename"]
    assert upload_path.exists()
    if upload_path.exists():
        upload_path.unlink()


def test_transcribe_endpoint(monkeypatch):
    fake = _make_fake_registry_module()
    monkeypatch.setitem(sys.modules, "models.model_registry", fake)

    from api import routes
    from api.dependencies import get_transcription_service_dep
    from types import SimpleNamespace

    async def fake_transcribe_file(filename, model_name=None, timeout=None):
        return {"text": "hello", "segments": None, "language": "en", "model": model_name or "default", "duration": 0.1}

    # Override dependency to provide a fake transcription service
    routes.app.dependency_overrides[get_transcription_service_dep] = lambda: SimpleNamespace(transcribe_file=fake_transcribe_file, atranscribe=fake_transcribe_file)

    client = TestClient(routes.app)
    r = client.post("/transcribe", json={"filename": "test.wav"})
    assert r.status_code == 200
    data = r.json()
    assert data["text"] == "hello"
    assert data["model"] == "default"

    # cleanup override
    routes.app.dependency_overrides.pop(get_transcription_service_dep, None)
