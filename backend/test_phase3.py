"""
Phase 3 - AI Vision & Search Systems QA
Tests: extract_face_vector (in-memory, no disk artefacts),
       compute_similarity (identity vs dissimilar),
       full /api/analyze pipeline integration.
Run with:  python backend/test_phase3.py
"""

from __future__ import annotations

import io
import os
import sys
import tempfile

import numpy as np
from PIL import Image

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from services.face_engine import extract_face_vector, compute_similarity  # noqa: E402

SEED_A = 42
SEED_B = 42   # same as A -> identical images
SEED_C = 9999  # different -> noise image


def _make_image(seed, size=100):
    """Return PNG bytes of a synthetic image.  No file is written to disk."""
    rng = np.random.default_rng(seed)
    arr = rng.integers(0, 256, size=(size, size, 3), dtype=np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def _dir_snapshot(path):
    try:
        return set(os.listdir(path))
    except FileNotFoundError:
        return set()


passed = 0
failed = 0
results = []


def check(condition, label, detail=""):
    global passed, failed
    if condition:
        passed += 1
        results.append("  PASS  " + label)
    else:
        failed += 1
        results.append("  FAIL  " + label + ("" if not detail else "  -- " + detail))


# ─── 1. extract_face_vector ───────────────────────────────────────────────────

def test_extract_face_vector():
    print()
    print("=" * 60)
    print("  1. extract_face_vector")
    print("=" * 60)

    img_bytes = _make_image(SEED_A)
    dir_before = _dir_snapshot(_BACKEND_DIR)
    tmp_before = _dir_snapshot(tempfile.gettempdir())

    vec = extract_face_vector(img_bytes)

    dir_after = _dir_snapshot(_BACKEND_DIR)
    tmp_after = _dir_snapshot(tempfile.gettempdir())

    check(isinstance(vec, list),              "returns a Python list")
    check(len(vec) == 512,                    "vector length is 512",
          "got %d" % len(vec))
    check(all(isinstance(v, (int, float)) for v in vec),
          "all elements are numeric")
    check(len(dir_after - dir_before) == 0,   "no new files in backend/ dir",
          "unexpected: %s" % (dir_after - dir_before))
    check(len(tmp_after - tmp_before) == 0,   "no temp files written to /tmp",
          "unexpected: %s" % (tmp_after - tmp_before))

    # Idempotent
    vec2 = extract_face_vector(img_bytes)
    check(len(vec2) == 512,                   "second call also 512-D")
    check(np.allclose(vec, vec2, atol=1e-6),  "deterministic: same bytes -> same vec")


# ─── 2. compute_similarity ────────────────────────────────────────────────────

def test_compute_similarity():
    print()
    print("=" * 60)
    print("  2. compute_similarity")
    print("=" * 60)

    vec_a = extract_face_vector(_make_image(SEED_A))
    vec_c = extract_face_vector(_make_image(SEED_C))

    sim_aa = compute_similarity(vec_a, vec_a)
    check(sim_aa > 0.95, "similarity A vs A > 0.95", "got %.6f" % sim_aa)

    sim_ac = compute_similarity(vec_a, vec_c)
    check(sim_ac < 0.40, "similarity A vs C < 0.40", "got %.6f" % sim_ac)

    sim_ca = compute_similarity(vec_c, vec_a)
    check(abs(sim_ca - sim_ac) < 1e-9, "similarity is symmetric",
          "A->C=%.6f  C->A=%.6f" % (sim_ac, sim_ca))

    vec_a2 = extract_face_vector(_make_image(SEED_A))
    sim_aa2 = compute_similarity(vec_a, vec_a2)
    check(sim_aa2 > 0.99, "same-image second call similarity > 0.99",
          "got %.6f" % sim_aa2)


# ─── 3. API integration ───────────────────────────────────────────────────────

def test_api_analyze():
    print()
    print("=" * 60)
    print("  3. API integration - POST /api/analyze")
    print("=" * 60)

    from fastapi.testclient import TestClient  # noqa: E402
    from main import app                        # noqa: E402

    client = TestClient(app)
    img_bytes = _make_image(SEED_A)

    r = client.post("/api/analyze",
                    files={"file": ("synthetic.png", img_bytes, "image/png")})
    check(r.status_code == 200, "HTTP 200 on valid image",
          "got %d: %s" % (r.status_code, r.text[:200]))

    body = r.json()
    check(body.get("status") == "success",           "response status is 'success'")
    check(isinstance(body.get("vector"), list),      "vector is a list")
    check(len(body["vector"]) == 512,                "vector length is 512",
          "got %d" % len(body["vector"]))
    check(isinstance(body.get("hash"), str),         "hash is a string")
    check(body["hash"].startswith("pdq:"),           "hash starts with 'pdq:'")

    vec = np.asarray(body["vector"], dtype=np.float64)
    norm = float(np.linalg.norm(vec))
    check(0.9 <= norm <= 1.1, "vector is L2-normalised (norm ~1.0)",
          "norm = %.6f" % norm)


# ─── 4. Edge cases ────────────────────────────────────────────────────────────

def test_edge_cases():
    print()
    print("=" * 60)
    print("  4. Edge cases")
    print("=" * 60)

    from fastapi.testclient import TestClient  # noqa: E402
    from main import app                        # noqa: E402

    client = TestClient(app)

    r = client.post("/api/analyze",
                    files={"file": ("empty.png", b"", "image/png")})
    check(r.status_code == 400, "empty file returns 400",
          "got %d" % r.status_code)

    r = client.post("/api/analyze",
                    files={"file": ("notes.txt", b"just text", "text/plain")})
    check(r.status_code == 400, "non-image file returns 400",
          "got %d" % r.status_code)

    r = client.post("/api/search", json={"vector": [0.1] * 10})
    check(r.status_code == 422, "wrong-dim vector returns 422",
          "got %d" % r.status_code)

    zero = [0.0] * 512
    sim = compute_similarity(zero, zero)
    check(sim == 0.0, "zero-vector similarity is 0.0", "got %.6f" % sim)


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  DeepShield Phase 3 - AI Vision & Search QA")
    print("=" * 60)

    test_extract_face_vector()
    test_compute_similarity()
    test_api_analyze()
    test_edge_cases()

    print()
    print("=" * 60)
    print("  RESULTS: %d passed, %d failed" % (passed, failed))
    print("=" * 60)
    for line in results:
        print(line)

    sys.exit(1 if failed else 0)
