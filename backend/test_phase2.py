"""Deterministic integration tests for the DeepShield FastAPI backend."""
import io
import os
import uuid

# Avoid downloading large face models in automated tests. Tests exercise the
# explicit pHash fallback; real ArcFace should be validated with local models.
os.environ["DEEPSHIELD_DISABLE_FACE_MODEL"] = "1"

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

import main
from main import app, auth_service

client = TestClient(app)


def image_bytes(color=(200, 80, 80), size=(100, 100)):
    image = Image.new("RGB", size, color=color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def auth_headers():
    _, token = auth_service.register(
        "Test Operator", f"operator-{uuid.uuid4().hex}@example.test", "safe-test-password-123"
    )
    return {"Authorization": f"Bearer {token}"}


def test_root_and_health_endpoints():
    assert client.get("/").json() == {"status": "ok"}
    assert client.get("/api/health").status_code == 200


def test_analyze_image_returns_typed_vector_and_real_perceptual_hash():
    response = client.post(
        "/api/analyze",
        files={"file": ("test.png", image_bytes(), "image/png")},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "success"
    assert len(body["vector"]) == 512
    assert body["vector_kind"] == "phash"
    assert body["hash_kind"] in {"pdq", "phash"}
    assert body["hash"].startswith(body["hash_kind"] + ":")
    assert np.isclose(np.linalg.norm(np.asarray(body["vector"], dtype=float)), 1.0, atol=0.05)


def test_analyze_rejects_empty_and_invalid_files():
    empty = client.post("/api/analyze", files={"file": ("empty.png", b"", "image/png")})
    invalid = client.post("/api/analyze", files={"file": ("notes.txt", b"not an image", "text/plain")})
    assert empty.status_code == 400
    assert invalid.status_code == 400


def test_analyze_rejects_oversized_upload():
    body = b"0" * (main.MAX_UPLOAD_BYTES + 1)
    response = client.post("/api/analyze", files={"file": ("oversized.jpg", body, "image/jpeg")})
    assert response.status_code == 413


def test_search_rejects_wrong_vector_dimension():
    response = client.post("/api/search", json={"vector": [0.1] * 10})
    assert response.status_code == 422


def test_search_returns_candidates_from_pipeline(monkeypatch):
    expected = [{
        "url": "https://example.com/candidate.jpg",
        "domain": "example.com",
        "similarity": 0.88,
        "thumbnail": "https://example.com/candidate.jpg",
        "hash_signature": "sha256:" + "a" * 64,
    }]
    monkeypatch.setattr(main, "search_deepfake_candidates", lambda **kwargs: expected)
    response = client.post("/api/search", json={"vector": [1.0 / np.sqrt(512)] * 512, "threshold": 0.3})
    assert response.status_code == 200, response.text
    assert response.json()[0]["hash_signature"] == expected[0]["hash_signature"]


def test_dossier_requires_operator_and_returns_pdf():
    payload = {
        "victim_name": "Test & Operator",
        "matches": [{
            "url": "https://example.com/a?x=1&y=2",
            "domain": "example.com",
            "similarity": 0.88,
            "thumbnail": "https://example.com/a.jpg",
            "hash_signature": "sha256:" + "a" * 64,
        }],
    }
    denied = client.post("/api/dossier", json=payload)
    assert denied.status_code == 401
    response = client.post("/api/dossier", headers=auth_headers(), json=payload)
    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("application/pdf")
    assert response.content.startswith(b"%PDF-")


def test_dossier_requires_at_least_one_candidate():
    response = client.post(
        "/api/dossier",
        headers=auth_headers(),
        json={"victim_name": "Test", "matches": []},
    )
    assert response.status_code == 422


def test_cors_preflight_for_local_frontend():
    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
