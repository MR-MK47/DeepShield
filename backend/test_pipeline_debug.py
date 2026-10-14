"""Deterministic end-to-end API pipeline test (no public search calls)."""
import io
import os

os.environ["DEEPSHIELD_DISABLE_FACE_MODEL"] = "1"

from fastapi.testclient import TestClient
from PIL import Image

import main

client = TestClient(main.app)


def make_image():
    image = Image.new("RGB", (100, 100), color=(10, 60, 160))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_analyze_then_search_pipeline(monkeypatch):
    response = client.post(
        "/api/analyze",
        files={"file": ("reference.png", make_image(), "image/png")},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["vector"]) == 512
    assert body["vector_kind"] == "phash"

    monkeypatch.setattr(main, "search_deepfake_candidates", lambda **kwargs: [])
    result = client.post(
        "/api/search",
        json={"vector": body["vector"], "query_text": "example test", "threshold": 0.3},
    )
    assert result.status_code == 200, result.text
    assert result.json() == []
