"""
OSINT Search — DuckDuckGo image search + face-similarity candidate filtering.
Downloads all candidate images in RAM; never persists them to disk.
"""

from __future__ import annotations

import asyncio
import io
import logging
from typing import Dict, List, Optional

import requests
from PIL import Image

from .face_engine import extract_face_vector, compute_similarity

logger = logging.getLogger(__name__)

# Minimum cosine similarity to consider a candidate a "match"
DEFAULT_THRESHOLD = 0.55

# Keywords that commonly appear on deepfake-hosting pages
DEEPFAKE_KEYWORDS = [
    "deepfake",
    "AI generated face",
    "synthetic media",
    "face swap",
    "digital disguise",
]


def search_deepfake_candidates(
    query_vector: List[float],
    query_text: Optional[str] = None,
    threshold: float = DEFAULT_THRESHOLD,
    max_results: int = 20,
) -> List[Dict[str, object]]:
    """
    Search the public web for images similar to ``query_vector``.

    Flow:
      1. Query DuckDuckGo Images for relevant URLs.
      2. Download each candidate thumbnail into RAM (BytesIO).
      3. Extract a face vector from each candidate.
      4. Compute cosine similarity against ``query_vector``.
      5. Return candidates with similarity >= ``threshold``.

    Returns an empty list on any network or parsing error — the caller
    should surface this to the user as a retry suggestion.
    """
    candidates: List[Dict[str, object]] = []
    query_vector_np = query_vector  # keep reference for logging

    # ── Step 1: DDGS image search ────────────────────────────────────────────
    search_terms = _build_search_terms(query_text)
    image_urls: List[str] = []
    for term in search_terms:
        try:
            from ddgs import DDGS  # renamed package
            with DDGS() as ddgs:
                results = list(ddgs.images(term, max_results=max_results // len(search_terms)))
                for r in results:
                    url = r.get("image") or r.get("url") or r.get("image_url")
                    if url and url not in image_urls:
                        image_urls.append(url)
        except Exception as exc:
            logger.warning("DDGS image search failed for term=%r: %s", term, exc)

    if not image_urls:
        logger.info("No image URLs from DDGS — returning empty candidate list")
        return []

    logger.info("Found %d candidate image URLs from DDGS", len(image_urls))

    # ── Step 2 & 3: Download + extract vector (in RAM) ───────────────────────
    for url in image_urls[:max_results]:
        vec, success = _download_and_extract(url)
        if not success:
            continue

        # ── Step 4: Similarity check ─────────────────────────────────────────
        sim = compute_similarity(query_vector, vec)
        if sim >= threshold:
            domain = _extract_domain(url)
            candidates.append({
                "url": url,
                "domain": domain,
                "similarity": round(sim, 4),
                "thumbnail": url,
            })

    # Sort descending by similarity
    candidates.sort(key=lambda c: c["similarity"], reverse=True)
    return candidates


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _build_search_terms(query_text: Optional[str]) -> List[str]:
    """Return a mix of the user query and standard deepfake keywords."""
    terms: List[str] = []
    if query_text:
        terms.append(query_text)
    terms.extend(DEEPFAKE_KEYWORDS)
    return terms


def _download_and_extract(url: str) -> tuple[List[float], bool]:
    """
    Download an image from ``url`` into a BytesIO buffer, then extract a
    512-D face vector.  Returns ``(vector, True)`` on success or
    ``(empty_list, False)`` on any failure.
    """
    try:
        resp = requests.get(url, timeout=10, stream=True)
        resp.raise_for_status()
    except Exception as exc:
        logger.debug("Failed to download %s: %s", url, exc)
        return [], False

    try:
        content = resp.content  # read into RAM, never write to disk
        vec = extract_face_vector(content)
        if vec:
            return vec, True
    except Exception as exc:
        logger.debug("Failed to extract vector from %s: %s", url, exc)

    return [], False


def _extract_domain(url: str) -> str:
    """Best-effort domain extraction from a URL string."""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc or url
    except Exception:
        return url
