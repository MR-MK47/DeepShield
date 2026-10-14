"""
Face Engine — Real face embedding & cosine similarity
DPDP Act 2023 compliant: all vectors processed in RAM, never persisted to disk.
"""

from __future__ import annotations

import io
import logging
from typing import List

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# Initialize the optional face model only when the first image is analysed.
# This keeps API startup and unit tests fast and works offline using pHash fallback.
import os
import threading
from pathlib import Path

_face_app = None
_FACE_ENGINE_AVAILABLE: bool | None = None
_face_lock = threading.Lock()


def _get_face_app():
    global _face_app, _FACE_ENGINE_AVAILABLE
    if _FACE_ENGINE_AVAILABLE is False:
        return None
    if _face_app is not None:
        return _face_app
    with _face_lock:
        if _face_app is not None:
            return _face_app
        if _FACE_ENGINE_AVAILABLE is False:
            return None
        if os.getenv("DEEPSHIELD_DISABLE_FACE_MODEL", "").lower() in {"1", "true", "yes"}:
            _FACE_ENGINE_AVAILABLE = False
            logger.info("Face model disabled by DEEPSHIELD_DISABLE_FACE_MODEL; using pHash fallback")
            return None
        try:
            from insightface.app import FaceAnalysis
            model_root = os.getenv(
                "INSIGHTFACE_ROOT", str(Path(__file__).resolve().parents[1] / ".insightface")
            )
            app = FaceAnalysis(
                name=os.getenv("INSIGHTFACE_MODEL", "buffalo_l"),
                root=model_root,
                providers=["CPUExecutionProvider"],
            )
            app.prepare(ctx_id=-1, det_size=(640, 640))
            _face_app = app
            _FACE_ENGINE_AVAILABLE = True
            logger.info("InsightFace model loaded")
        except Exception as exc:  # missing model or optional dependency: fall back explicitly
            _FACE_ENGINE_AVAILABLE = False
            logger.warning("InsightFace unavailable (%s); using pHash fallback until restart", exc)
    return _face_app

def extract_face_vector_with_kind(image_bytes: bytes) -> tuple[List[float], str]:
    """
    Like :func:`extract_face_vector` but also returns the vector *kind*:

    * ``"arcface"`` — a real 512-D ArcFace biometric embedding (face found).
    * ``"phash"``   — a perceptual-hash fallback (no face detected).
    * ``""``        — decoding failed (empty vector).

    Callers MUST only compare vectors of the same kind; an ArcFace embedding
    and a pHash vector are not in the same space and their cosine similarity
    is meaningless noise.
    """
    try:
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        logger.warning("Could not decode image: %s", exc)
        return [], ""

    arr = np.array(pil_img)

    face_app = _get_face_app()
    if face_app is not None:
        try:
            faces = face_app.get(arr)
            if faces:
                # Take the face with the largest actual bounding-box area.
                largest = max(
                    faces,
                    key=lambda face: max(0.0, face.bbox[2] - face.bbox[0])
                    * max(0.0, face.bbox[3] - face.bbox[1]),
                )
                embedding = largest.embedding  # 512-D float32, already L2-normalised
                logger.info("Used ArcFace embedding")
                return embedding.tolist(), "arcface"
            else:
                logger.info("No face detected by InsightFace")
        except Exception as exc:  # pragma: no cover
            logger.warning("insightface embedding failed: %s — falling back", exc)

    # Fallback: pHash → 512-D normalised vector (perceptual, not biometric)
    logger.info("Used pHash fallback")
    return _phash_vector(pil_img), "phash"


def extract_face_vector(image_bytes: bytes) -> List[float]:
    """
    Decode ``image_bytes`` in memory, detect faces, and return a 512-D
    face-embedding vector (normalized ArcFace) for the largest face.

    If no face is detected, falls back to a perceptual-hash vector so the
    pipeline still returns a 512-D result that can be compared downstream.

    Returns an empty list when the image cannot be decoded at all.
    """
    vec, _kind = extract_face_vector_with_kind(image_bytes)
    return vec


def vector_kind(vec: List[float]) -> str:
    """
    Best-effort classification of a bare 512-D vector when its provenance is
    unknown (e.g. a query vector that travelled through JSON).

    pHash fallback vectors are produced by L2-normalising a ±1 bit vector, so
    every component has an identical magnitude (~1/sqrt(512)).  ArcFace
    embeddings have a continuous distribution of magnitudes.  We exploit that
    to tell them apart.
    """
    if not vec:
        return ""
    a = np.abs(np.asarray(vec, dtype=np.float64))
    if a.size and a.max() > 0 and (a.max() - a.min()) < 1e-6:
        return "phash"
    return "arcface"


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

def _phash_vector(img: Image.Image, hash_size: int = 8) -> List[float]:
    """Represent a standard 64-bit pHash as a 512-D normalized fallback.

    Each of the 64 bits is repeated eight times only to retain the historical
    vector transport shape. It is not a face embedding; vector_kind() marks
    this equal-magnitude vector as "phash".
    """
    try:
        import imagehash
        bit_string = bin(int(str(imagehash.phash(img.convert("RGB"), hash_size=8)), 16))[2:].zfill(64)
    except Exception as exc:
        logger.warning("pHash computation failed: %s", exc)
        return []
    bits = np.fromiter((1.0 if bit == "1" else -1.0 for bit in bit_string), dtype=np.float64)
    vec = np.repeat(bits, 8)
    norm = float(np.linalg.norm(vec))
    if norm == 0:
        return []
    return (vec / norm).tolist()
