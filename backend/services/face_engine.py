"""
Face Engine — Real face embedding & cosine similarity
DPDP Act 2023 compliant: all vectors processed in RAM, never persisted to disk.
"""

from __future__ import annotations

import io
import logging
import os
from typing import List

# Limit OpenMP threads to 1 to prevent memory spikes in resource-constrained environments (e.g., 512MB RAM)
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# InsightFace singleton — loaded once per process.
# We use buffalo_sc (16MB lightweight model) to fit within 512MB RAM limits.
try:
    from insightface.app import FaceAnalysis
    _face_app = FaceAnalysis(name="buffalo_sc", root=".insightface")
    _face_app.prepare(ctx_id=0, det_size=(640, 640))
    _FACE_ENGINE_AVAILABLE = True
    logger.info("insightface buffalo_sc model loaded (512-D ArcFace embeddings)")
except Exception as exc:  # pragma: no cover — graceful degrade
    logger.warning("insightface unavailable: %s — falling back to pHash vectors", exc)
    _face_app = None
    _FACE_ENGINE_AVAILABLE = False


def extract_face_vector(image_bytes: bytes) -> List[float]:
    """
    Decode ``image_bytes`` in memory, detect faces, and return a 512-D
    face-embedding vector (normalized ArcFace) for the largest face.

    If no face is detected, falls back to a perceptual-hash vector so the
    pipeline still returns a 512-D result that can be compared downstream.

    Returns an empty list when the image cannot be decoded at all.
    """
    try:
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        logger.warning("Could not decode image: %s", exc)
        return []

    arr = np.array(pil_img)

    if _FACE_ENGINE_AVAILABLE and _face_app is not None:
        try:
            faces = _face_app.get(arr)
            if faces:
                # Take the largest face (by bounding-box area).
                largest = max(faces, key=lambda f: f.bbox[2] * f.bbox[3])
                embedding = largest.embedding  # 512-D float32, already L2-normalised
                return embedding.tolist()
        except Exception as exc:  # pragma: no cover
            logger.warning("insightface embedding failed: %s — falling back", exc)

    # Fallback: pHash → 512-D normalised vector (perceptual, not biometric)
    return _phash_vector(pil_img)


def compute_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Cosine similarity between two vectors.
    Returns a float in ``[0.0, 1.0]`` for normalised embeddings.
    """
    a = np.asarray(vec1, dtype=np.float64)
    b = np.asarray(vec2, dtype=np.float64)
    dot = float(np.dot(a, b))
    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(dot / (norm_a * norm_b))


# ─── Perceptual-hash fallback ────────────────────────────────────────────────

def _phash_vector(img: Image.Image, hash_size: int = 32) -> List[float]:
    """
    Compute a perceptual hash (pHash) of an image and return it as a
    512-D normalised float vector.  Not a biometric embedding — used as a
    graceful fallback when no face is present.
    """
    # Resize to hash_size+1 × hash_size to compute DCT
    size = hash_size + 1
    img_small = img.resize((size, size), Image.LANCZOS).convert("L")
    pixels = np.array(img_small, dtype=np.float64)

    # Compute 1-D DCT along rows, then columns
    # (simple DCT-II approximation via numpy)
    N = pixels.shape[1]
    dct_row = np.zeros_like(pixels)
    for x in range(N):
        for u in range(hash_size):
            s = 0.0
            for v in range(N):
                s += pixels[u, v] * np.cos(np.pi * (2 * v + 1) * u / (2 * N))
            dct_row[u, x] = s

    dct_result = np.zeros_like(dct_row)
    for y in range(dct_row.shape[0]):
        for v in range(hash_size):
            s = 0.0
            for u in range(dct_row.shape[1]):
                s += dct_row[y, u] * np.cos(np.pi * (2 * u + 1) * v / (2 * N))
            dct_result[y, v] = s

    # Take top-left hash_size × hash_size block = 1024 coefficients
    block = dct_result[:hash_size, :hash_size]
    median = np.median(block)
    bits = (block > median).astype(np.uint8).flatten()
    # Pad or trim to 512
    bits = bits[:512] if len(bits) > 512 else np.pad(bits, (0, 512 - len(bits)))
    # Normalise to [-1, 1] range for similarity comparison
    vec = (bits.astype(np.float64) * 2.0 - 1.0).tolist()
    # L2-normalise
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec
