import os
import json
import logging
from io import BytesIO
import urllib.error
import socket
import pytest
from server.ai.gemini_provider import GeminiProvider

# Ensure API key is set for tests
os.environ["GEMINI_API_KEY"] = "test_key"

@pytest.fixture
def provider():
    return GeminiProvider()

def make_response(status=200, body=b"{}", reason="OK"):
    class MockResponse:
        def __init__(self, status, body, reason):
            self.status = status
            self.body = body
            self.reason = reason
        def read(self):
            return self.body
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            pass
    return MockResponse(status, body, reason)

def test_http_error_logging(provider, caplog, monkeypatch):
    # Simulate HTTPError with body containing JSON error message
    error_body = json.dumps({"error": {"code": 400, "message": "Invalid request"}}).encode("utf-8")
    http_err = urllib.error.HTTPError(
        url="https://example.com",
        code=400,
        msg="Bad Request",
        hdrs=None,
        fp=BytesIO(error_body),
    )
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(http_err))
    with caplog.at_level(logging.WARNING):
        result = provider.generate_copilot_explanation(trusted_context={}, language="English")
    assert result is None
    # Verify safe log format without URL or API key
    logged = any("Gemini API HTTPError 400 | Bad Request | Invalid request" in rec.message for rec in caplog.records)
    assert logged

def test_url_error_logging(provider, caplog, monkeypatch):
    url_err = urllib.error.URLError("Network unreachable")
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(url_err))
    with caplog.at_level(logging.WARNING):
        result = provider.generate_copilot_explanation(trusted_context={}, language="English")
    assert result is None
    assert any("Gemini API URLError: Network unreachable" in rec.message for rec in caplog.records)

def test_timeout_logging(provider, caplog, monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(socket.timeout()))
    with caplog.at_level(logging.WARNING):
        result = provider.generate_copilot_explanation(trusted_context={}, language="English")
    assert result is None
    assert any("Gemini API request timed out after" in rec.message for rec in caplog.records)

def test_envelope_json_decode_error(provider, caplog, monkeypatch):
    # Return malformed JSON for envelope
    resp = make_response(body=b"{ not json")
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: resp)
    with caplog.at_level(logging.WARNING):
        result = provider.generate_copilot_explanation(trusted_context={}, language="English")
    assert result is None
    assert any("Gemini API envelope JSON decode error" in rec.message for rec in caplog.records)

def test_no_candidates(provider, caplog, monkeypatch):
    resp = make_response(body=json.dumps({"candidates": []}).encode())
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: resp)
    with caplog.at_level(logging.WARNING):
        result = provider.generate_copilot_explanation(trusted_context={}, language="English")
    assert result is None
    assert any("Gemini API returned no candidates" in rec.message for rec in caplog.records)

def test_candidate_no_parts(provider, caplog, monkeypatch):
    resp_body = {"candidates": [{"content": {"parts": []}}]}
    resp = make_response(body=json.dumps(resp_body).encode())
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: resp)
    with caplog.at_level(logging.WARNING):
        result = provider.generate_copilot_explanation(trusted_context={}, language="English")
    assert result is None
    assert any("Gemini API candidate has no content parts" in rec.message for rec in caplog.records)

def test_candidate_empty_text(provider, caplog, monkeypatch):
    resp_body = {"candidates": [{"content": {"parts": [{"text": ""}]}}]}
    resp = make_response(body=json.dumps(resp_body).encode())
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: resp)
    with caplog.at_level(logging.WARNING):
        result = provider.generate_copilot_explanation(trusted_context={}, language="English")
    assert result is None
    assert any("Gemini API returned empty candidate text" in rec.message for rec in caplog.records)

def test_model_output_json_decode_error(provider, caplog, monkeypatch):
    # Valid envelope but malformed model output JSON
    bad_json = "{invalid json}"
    resp_body = {"candidates": [{"content": {"parts": [{"text": bad_json}]}}]}
    resp = make_response(body=json.dumps(resp_body).encode())
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: resp)
    with caplog.at_level(logging.WARNING):
        result = provider.generate_copilot_explanation(trusted_context={}, language="English")
    assert result is None
    assert any("Gemini model output JSON decode error" in rec.message for rec in caplog.records)
