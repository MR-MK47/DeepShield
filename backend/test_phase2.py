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


def test_combined_scan_endpoint_analyzes_and_searches(monkeypatch):
    expected = [{
        "url": "https://example.com/combined.jpg",
        "domain": "example.com",
        "similarity": 0.81,
        "thumbnail": "https://example.com/combined.jpg",
        "hash_signature": "sha256:" + "a" * 64,
    }]
    monkeypatch.setattr(main, "search_deepfake_candidates", lambda **kwargs: expected)
    response = client.post(
        "/api/scan",
        files={"file": ("reference.png", image_bytes(), "image/png")},
        data={"query_text": "demo subject", "threshold": "0.3"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "success"
    assert body["analysis"]["hash_kind"] in {"pdq", "phash"}
    assert body["matches"][0]["url"] == expected[0]["url"]
    assert body["history_saved"] is False


def test_match_history_is_opt_in_private_and_deletable(monkeypatch):
    expected = [{
        "url": "https://example.com/history.jpg",
        "domain": "example.com",
        "similarity": 0.81,
        "thumbnail": "https://example.com/history.jpg",
        "hash_signature": "sha256:" + "b" * 64,
    }]
    monkeypatch.setattr(main, "search_deepfake_candidates", lambda **kwargs: expected)
    body = {"vector": [1.0 / np.sqrt(512)] * 512, "query_text": "history test", "threshold": 0.3, "save_history": True}
    denied = client.post("/api/search", json=body)
    assert denied.status_code == 401

    headers = auth_headers()
    response = client.post("/api/search", headers=headers, json=body)
    assert response.status_code == 200, response.text
    history_response = client.get("/api/matches", headers=headers)
    assert history_response.status_code == 200, history_response.text
    history = history_response.json()
    assert len(history) == 1
    assert history[0]["query_text"] == "history test"
    assert history[0]["matches"][0]["hash_signature"] == expected[0]["hash_signature"]
    assert "vector" not in history[0]
    assert "image_bytes" not in history[0]

    other_headers = auth_headers()
    denied_delete = client.delete(f"/api/matches/{history[0]['scan_id']}", headers=other_headers)
    assert denied_delete.status_code == 404

    deleted = client.delete(f"/api/matches/{history[0]['scan_id']}", headers=headers)
    assert deleted.status_code == 200
    assert client.get("/api/matches", headers=headers).json() == []
