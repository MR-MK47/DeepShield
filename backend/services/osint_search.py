"""
OSINT Search — DuckDuckGo image search + face-similarity candidate filtering.
Downloads all candidate images in RAM; never persists them to disk.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

import requests

from .face_engine import (
    extract_face_vector_with_kind,
    compute_similarity,
    vector_kind,
)

logger = logging.getLogger(__name__)

# Minimum cosine similarity to consider a candidate a "match".
# ArcFace embeddings of different photos of the same person typically score
# ~0.4–0.9; unrelated faces score near 0.  We therefore use a moderate default
# and let the caller tune it from the UI.
DEFAULT_THRESHOLD = 0.30

# Keywords used ONLY as a fallback when the user supplies no text query.
DEEPFAKE_KEYWORDS = [
    "deepfake",
    "AI generated face",
    "synthetic media",
    "face swap",
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
      1. Build the query terms — the user's own text query takes priority;
         generic deepfake keywords are used only when no query is given, or
         as a small supplement when the query returns too few images.
      2. Download each candidate image into RAM (BytesIO).
      3. Extract a face vector from each candidate (ArcFace, or pHash
         fallback when no face is present).
      4. Compute cosine similarity against ``query_vector`` — but ONLY
         against candidates of the same vector kind (ArcFace vs pHash are
         different spaces and cannot be meaningfully compared).
      5. Return candidates with similarity >= ``threshold``, best first.

    Returns an empty list on any network or parsing error — the caller
    should surface this to the user as a retry suggestion.
    """
    if not query_vector:
        logger.warning("search_deepfake_candidates called with empty query vector")
        return []

    query_kind = vector_kind(query_vector)
    logger.info("Query vector kind: %s", query_kind)

    # ── Step 1: Gather candidate image URLs ──────────────────────────────────
    image_urls = _gather_image_urls(query_text, max_results)
    if not image_urls:
        logger.info("No image URLs found — returning empty candidate list")
        return []

    logger.info("Evaluating %d candidate image URLs", len(image_urls))

    # ── Steps 2–4: Download + embed (parallel) + similarity ──────────────────
    candidates: List[Dict[str, object]] = []

    def _evaluate(url: str) -> Optional[Dict[str, object]]:
        vec, kind = _download_and_extract(url)
        if not vec:
            return None
        # Skip cross-space comparisons (ArcFace vs pHash = noise).
        if kind != query_kind:
            logger.debug("Skipping %s — kind %s != query kind %s", url[:60], kind, query_kind)
            return None
        sim = compute_similarity(query_vector, vec)
        logger.info("SIMILARITY %.4f (threshold %.2f) %s", sim, threshold, url[:60])
        if sim >= threshold:
            return {
                "url": url,
                "domain": _extract_domain(url),
                "similarity": round(sim, 4),
                "thumbnail": url,
            }
        return None

    with ThreadPoolExecutor(max_workers=6) as executor:
        for result in executor.map(_evaluate, image_urls[: max_results * 2]):
            if result is not None:
                candidates.append(result)

    # Sort descending by similarity
    candidates.sort(key=lambda c: c["similarity"], reverse=True)
    logger.info("Returning %d candidates above threshold %.2f", len(candidates), threshold)
    return candidates[:max_results]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _gather_image_urls(query_text: Optional[str], max_results: int) -> List[str]:
    """
    Collect image URLs for the search.

    The user's own query is the PRIMARY source.  Generic deepfake keywords are
    only used when there is no query, or as a small supplement when the query
    returns very few images — this keeps the results relevant instead of
    drowning the user's subject in generic "deepfake" stock imagery.
    """
    urls: List[str] = []
    seen: set[str] = set()

    def _add(batch: List[str]) -> None:
        for u in batch:
            if u and u not in seen:
                seen.add(u)
                urls.append(u)

    if query_text and query_text.strip():
        _add(_ddgs_image_search(query_text.strip(), max_results))
        logger.info("User-query search returned %d URLs", len(urls))
        # Supplement only if the user query was unproductive.
        if len(urls) < 5:
            per_term = max(2, (max_results - len(urls)) // len(DEEPFAKE_KEYWORDS))
            for kw in DEEPFAKE_KEYWORDS:
                _add(_ddgs_image_search(kw, per_term))
    else:
        per_term = max(3, max_results // len(DEEPFAKE_KEYWORDS))
        for kw in DEEPFAKE_KEYWORDS:
            _add(_ddgs_image_search(kw, per_term))

    return urls


def _ddgs_image_search(term: str, limit: int) -> List[str]:
    """Run a single DDGS image search and return image URLs (best-effort)."""
    if limit <= 0:
        return []
    try:
        from ddgs import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.images(term, max_results=limit))
        out: List[str] = []
        for r in results:
            url = r.get("image") or r.get("url") or r.get("image_url")
            if url:
                out.append(url)
        return out
    except Exception as exc:
        logger.warning("DDGS image search failed for term=%r: %s", term, exc)
        return []


def _download_and_extract(url: str) -> tuple[List[float], str]:
    """
    Download an image from ``url`` into RAM, then extract a face vector.

    Returns ``(vector, kind)`` where ``kind`` is ``"arcface"``, ``"phash"``,
    or ``""`` on failure.
    """
    try:
        resp = requests.get(url, timeout=6, stream=True)
        resp.raise_for_status()
        content = resp.content  # read into RAM, never write to disk
        if len(content) > 10 * 1024 * 1024:  # 10 MB safety limit
            logger.debug("Image too large: %s", url)
            return [], ""
    except Exception as exc:
        logger.debug("Failed to download %s: %s", url, exc)
        return [], ""

    try:
        return extract_face_vector_with_kind(content)
    except Exception as exc:
        logger.debug("Failed to extract vector from %s: %s", url, exc)
        return [], ""


def _extract_domain(url: str) -> str:
    """Best-effort domain extraction from a URL string."""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc or url
    except Exception:
        return url
