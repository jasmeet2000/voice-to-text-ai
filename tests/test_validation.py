import pytest

import services.validation_service as vs
from core.exceptions import ValidationError


def test_sanitize_filename_basic():
    assert vs.sanitize_filename("my file.wav") == "my_file.wav"
    assert vs.sanitize_filename("../etc/passwd") == "passwd"
    assert vs.sanitize_filename(".hidden.mp3").startswith("hidden") and vs.sanitize_filename(".hidden.mp3").endswith(".mp3")
    longfn = "a" * 250 + ".wav"
    s = vs.sanitize_filename(longfn)
    assert len(s) <= 200
    assert s.endswith(".wav")


def test_validate_file_path_success(tmp_path):
    p = tmp_path / "ok.wav"
    p.write_bytes(b"\x00\x01")
    # skip integrity check to avoid ffmpeg/pydub in CI
    vs.validate_file_path(p, check_integrity=False)


def test_validate_file_path_unsupported_extension(tmp_path):
    p = tmp_path / "bad.txt"
    p.write_bytes(b"ok")
    with pytest.raises(ValidationError):
        vs.validate_file_path(p, check_integrity=False)


def test_validate_file_path_oversize(tmp_path, monkeypatch):
    p = tmp_path / "big.wav"
    p.write_bytes(b"ab")
    # reduce configured max_file_size to trigger oversize
    monkeypatch.setattr(vs.settings, "max_file_size", 1)
    with pytest.raises(ValidationError):
        vs.validate_file_path(p, check_integrity=False)
