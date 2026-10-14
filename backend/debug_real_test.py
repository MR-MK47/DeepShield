"""Manual public-web smoke test.

This script makes external network requests only when executed directly:
    python debug_real_test.py

It is intentionally not an automated pytest test because results depend on
third-party websites, search provider availability and network connectivity.
"""
import logging
import sys

import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

REFERENCE_URL = "https://universaljacket.com/wp-content/uploads/2023/04/3.jpg"


def main() -> int:
    try:
        from services.face_engine import extract_face_vector
        from services.osint_search import search_deepfake_candidates
    except ImportError as exc:
        print(f"Backend dependencies are missing: {exc}")
        return 1

    print("=" * 70)
    print("MANUAL PUBLIC-WEB IMAGE SEARCH SMOKE TEST")
    print("=" * 70)
    print(f"Downloading reference image: {REFERENCE_URL}")
    try:
        response = requests.get(REFERENCE_URL, timeout=(3, 10))
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Could not download the reference image: {exc}")
        print("Check network access or use a local test image instead.")
        return 2

    vector, kind = __import__(
        "services.face_engine", fromlist=["extract_face_vector_with_kind"]
    ).extract_face_vector_with_kind(response.content)
    if not vector:
        print("The reference image could not be analysed.")
        return 3

    print(f"Representation kind: {kind}; vector dimensions: {len(vector)}")
    print("Searching public image candidates (this requires network access)...")
    try:
        matches = search_deepfake_candidates(
            query_vector=vector,
            query_text="Puffer Jacket Pope",
            threshold=0.30,
            max_results=20,
        )
    except Exception as exc:
        print(f"Search failed: {exc}")
        return 4

    print(f"Candidates returned: {len(matches)}")
    for index, match in enumerate(matches, 1):
        print(
            f"{index}. {match['domain']} — "
            f"{float(match['similarity']) * 100:.1f}% similarity — {match['url']}"
        )
    print("Note: similarity candidates are not proof of synthetic or unlawful media.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
