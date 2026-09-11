"""
Phase 2 Integration Tests — DeepShield Backend
Uses FastAPI TestClient (httpx) for synchronous HTTP assertions.
Run with:  python -m pytest backend/test_phase2.py -v
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import List

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from main import app

client = TestClient(app)

# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def sample_image_bytes() -> bytes:
    """Generate a valid 100×100 red PNG in memory (no disk I/O)."""
    img = Image.new("RGB", (100, 100), color=(200, 80, 80))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


@pytest.fixture(scope="module")
def sample_text_bytes() -> bytes:
    """Arbitrary plain-text bytes (not a valid image)."""
    return b"this is not an image, just a text file"


@pytest.fixture(scope="module")
def analyze_response(sample_image_bytes: bytes) -> dict:
    """Call POST /api/analyze once and cache the result for other tests."""
    resp = client.post(
        "/api/analyze",
        files={"file": ("test.png", sample_image_bytes, "image/png")},
    )
    assert resp.status_code == 200, f"analyze failed: {resp.text}"
    return resp.json()


# ─── 1. Health Check ─────────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_200(self):
        r = client.get("/api/health")
        assert r.status_code == 200

    def test_health_body(self):
        r = client.get("/api/health")
        assert r.json() == {"status": "ok"}


# ─── 2. Analyze — valid image ────────────────────────────────────────────────

class TestAnalyzeValid:
    def test_status_200(self, sample_image_bytes):
        r = client.post(
            "/api/analyze",
            files={"file": ("test.png", sample_image_bytes, "image/png")},
        )
        assert r.status_code == 200

    def test_response_schema(self, analyze_response: dict):
        body = analyze_response
        assert body["status"] == "success"
        assert isinstance(body["vector"], list)
        assert isinstance(body["hash"], str)

    def test_vector_is_512_floats(self, analyze_response: dict):
        vec = analyze_response["vector"]
        assert len(vec) == 512, f"Expected 512 dims, got {len(vec)}"
        assert all(isinstance(v, (int, float)) for v in vec)

    def test_hash_non_empty_pdq(self, analyze_response: dict):
        h = analyze_response["hash"]
        assert len(h) > 0
        assert h.startswith("pdq:")

    def test_vector_l2_norm_reasonable(self, analyze_response: dict):
        """Real ArcFace embeddings are L2-normalised → norm ≈ 1.0."""
        vec = np.asarray(analyze_response["vector"], dtype=np.float64)
        norm = float(np.linalg.norm(vec))
        # pHash-fallback vectors are also L2-normalised
        assert 0.9 <= norm <= 1.1, f"Unexpected vector norm: {norm}"


# ─── 3. Analyze — invalid file ───────────────────────────────────────────────

class TestAnalyzeInvalid:
    def test_empty_file_returns_400(self):
        r = client.post("/api/analyze", files={"file": ("empty.txt", b"", "text/plain")})
        assert r.status_code == 400

    def test_non_image_file_returns_400(self, sample_text_bytes):
        r = client.post(
            "/api/analyze",
            files={"file": ("notes.txt", sample_text_bytes, "text/plain")},
        )
        assert r.status_code == 400


# ─── 4. Search ───────────────────────────────────────────────────────────────

class TestSearch:
    def test_valid_vector_returns_200(self, analyze_response: dict):
        vec = analyze_response["vector"]
        r = client.post("/api/search", json={"vector": vec})
        assert r.status_code == 200, f"search failed: {r.text}"

    def test_response_is_list(self, analyze_response: dict):
        vec = analyze_response["vector"]
        r = client.post("/api/search", json={"vector": vec})
        body = r.json()
        assert isinstance(body, list)

    def test_similarity_scores_in_range(self, analyze_response: dict):
        vec = analyze_response["vector"]
        r = client.post("/api/search", json={"vector": vec})
        matches = r.json()
        for m in matches:
            sim = m.get("similarity")
            assert isinstance(sim, (int, float)), f"similarity not a number: {sim}"
            assert 0.0 <= sim <= 1.0, f"similarity out of range: {sim}"

    def test_match_has_required_fields(self, analyze_response: dict):
        vec = analyze_response["vector"]
        r = client.post("/api/search", json={"vector": vec})
        matches = r.json()
        required = {"url", "domain", "similarity", "thumbnail"}
        for m in matches:
            assert required.issubset(m.keys()), f"Missing keys in match: {required - m.keys()}"

    def test_bad_vector_returns_422(self):
        r = client.post("/api/search", json={"vector": [0.1] * 10})
        assert r.status_code == 422


# ─── 5. Takedown Email ───────────────────────────────────────────────────────

class TestTakedown:
    def test_meta_platform(self):
        r = client.post(
            "/api/takedown/email",
            json={"target_url": "https://facebook.com/fake123", "platform": "Meta"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "dispatched"
        assert body["notice_type"] == "Rule 3(1)(b)"
        assert body["recipient"] == "fbgoindia@support.facebook.com"
        # ISO-8601 timestamp contains 'T'
        assert "T" in body["timestamp"]

    def test_google_platform(self):
        r = client.post(
            "/api/takedown/email",
            json={"target_url": "https://youtube.com/v/fake", "platform": "Google"},
        )
        assert r.status_code == 200
        assert r.json()["recipient"] == "abuse@google.com"

    def test_unknown_platform_fallback(self):
        r = client.post(
            "/api/takedown/email",
            json={"target_url": "https://x.com/fake", "platform": "UnknownNet"},
        )
        assert r.status_code == 200
        assert r.json()["status"] == "dispatched"

    def test_missing_fields_returns_422(self):
        r = client.post("/api/takedown/email", json={})
        assert r.status_code == 422


# ─── 6. CORS ─────────────────────────────────────────────────────────────────

class TestCORS:
    def test_preflight_health(self):
        r = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert r.status_code == 200
        assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_cors_header_on_post_analyze(self, sample_image_bytes):
        r = client.post(
            "/api/analyze",
            files={"file": ("test.png", sample_image_bytes, "image/png")},
            headers={"Origin": "http://localhost:3000"},
        )
        assert r.status_code == 200
        assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"


# ─── 7. End-to-end: analyze → search pipeline ───────────────────────────────

class TestPipeline:
    def test_analyze_then_search(self, sample_image_bytes):
        """Full pipeline: upload image → get vector → search candidates."""
        # Step 1: Analyze
        r1 = client.post(
            "/api/analyze",
            files={"file": ("subject.jpg", sample_image_bytes, "image/jpeg")},
        )
        assert r1.status_code == 200
        vec = r1.json()["vector"]
        assert len(vec) == 512

        # Step 2: Search with that vector
        r2 = client.post("/api/search", json={"vector": vec})
        assert r2.status_code == 200
        matches = r2.json()
        # At minimum the endpoint returns a list (may be empty if DDGS has no results)
        assert isinstance(matches, list)
        for m in matches:
            assert 0.0 <= m["similarity"] <= 1.0
