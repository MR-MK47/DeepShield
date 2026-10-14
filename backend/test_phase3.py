"""Offline-safe face-vector and similarity tests."""
import io
import os

os.environ["DEEPSHIELD_DISABLE_FACE_MODEL"] = "1"

import numpy as np
from PIL import Image

from services.face_engine import extract_face_vector, extract_face_vector_with_kind, compute_similarity


def make_image(color):
    image = Image.new("RGB", (100, 100), color=color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_fallback_vector_is_normalized_and_typed():
    vector, kind = extract_face_vector_with_kind(make_image((10, 60, 160)))
    assert len(vector) == 512
    assert kind == "phash"
    assert np.isclose(np.linalg.norm(np.asarray(vector)), 1.0, atol=1e-6)


def test_similarity_is_stable_symmetric_and_bounded():
    first = extract_face_vector(make_image((10, 60, 160)))
    same = extract_face_vector(make_image((10, 60, 160)))
    other = extract_face_vector(make_image((240, 10, 20)))
    assert compute_similarity(first, same) > 0.99
    assert -1.0 <= compute_similarity(first, other) <= 1.0
    assert np.isclose(compute_similarity(first, other), compute_similarity(other, first))


def test_invalid_image_returns_empty_vector():
    assert extract_face_vector(b"not an image") == []
