"""Public-web image discovery and candidate similarity evaluation.

Only HTTP(S) image URLs are fetched. Redirects are disabled to avoid an
untrusted result redirecting the backend into private networks. Candidates are
not treated as proof of synthetic media; the service only returns similarity
candidates.
"""
from __future__ import annotations

import hashlib
import ipaddress
import logging
import socket
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests
from PIL import Image, UnidentifiedImageError
import io

from .face_engine import extract_face_vector_with_kind, compute_similarity, vector_kind

logger = logging.getLogger(__name__)
DEFAULT_THRESHOLD = 0.30
MAX_IMAGE_BYTES = 10 * 1024 * 1024
DEEPFAKE_KEYWORDS = ["deepfake", "AI generated face", "synthetic media", "face swap"]


def _is_public_http_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False
    if parsed.username or parsed.password:
        return False
    host = parsed.hostname.lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith((".local", ".internal")):
        return False
    try:
        addresses = [ipaddress.ip_address(host)]
    except ValueError:
        try:
            addresses = [
                ipaddress.ip_address(item[4][0])
                for item in socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
            ]
        except (OSError, ValueError):
            return False
    return bool(addresses) and all(address.is_global for address in addresses)


def search_deepfake_candidates(
    query_vector: List[float],
    query_text: Optional[str] = None,
    threshold: float = DEFAULT_THRESHOLD,
    max_results: int = 20,
) -> List[Dict[str, object]]:
    if not query_vector or len(query_vector) != 512:
        return []
    query_kind = vector_kind(query_vector)
    image_urls = _gather_image_urls(query_text, max_results)
    if not image_urls:
        logger.info("Image provider returned no candidates.")
        return []

    candidates: List[Dict[str, object]] = []

    def evaluate(url: str) -> Optional[Dict[str, object]]:
        vector, kind, content_sha256 = _download_and_extract(url)
        if not vector or kind != query_kind:
            return None
        similarity = compute_similarity(query_vector, vector)
        if similarity < threshold:
            return None
        return {
            "url": url,
            "domain": _extract_domain(url),
            "similarity": round(max(-1.0, min(1.0, similarity)), 4),
            "thumbnail": url,
            "hash_signature": f"sha256:{content_sha256}",
        }

    # Bounded thread pool and request timeouts keep a single search manageable.
    with ThreadPoolExecutor(max_workers=4) as executor:
        for result in executor.map(evaluate, image_urls[: max_results * 2]):
            if result is not None:
                candidates.append(result)
    candidates.sort(key=lambda item: float(item["similarity"]), reverse=True)
    return candidates[:max_results]


def _gather_image_urls(query_text: Optional[str], max_results: int) -> List[str]:
    urls: list[str] = []
    seen: set[str] = set()

    def add(items: List[str]) -> None:
        for url in items:
            if url and url not in seen and _is_public_http_url(url):
                seen.add(url)
                urls.append(url)

    if query_text and query_text.strip():
        add(_ddgs_image_search(query_text.strip()[:200], max_results))
        if len(urls) < 5:
            for keyword in DEEPFAKE_KEYWORDS:
                add(_ddgs_image_search(keyword, max(2, (max_results - len(urls)) // len(DEEPFAKE_KEYWORDS))))
    else:
        per_term = max(3, max_results // len(DEEPFAKE_KEYWORDS))
        for keyword in DEEPFAKE_KEYWORDS:
            add(_ddgs_image_search(keyword, per_term))
    return urls


def _ddgs_image_search(term: str, limit: int) -> List[str]:
    if limit <= 0:
        return []
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.images(term, max_results=limit))
        return [
            str(item.get("image") or item.get("url") or item.get("image_url") or "")
            for item in results
        ]
    except Exception as exc:
        logger.warning("Image search failed for term=%r: %s", term, exc)
        return []


def _download_and_extract(url: str) -> tuple[List[float], str, str]:
    if not _is_public_http_url(url):
        return [], "", ""
    try:
        with requests.get(
            url,
            timeout=(3, 6),
            stream=True,
            allow_redirects=False,
            headers={"User-Agent": "DeepShield/1.0 (public image analysis)"},
        ) as response:
            response.raise_for_status()
            content_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
            if not content_type.startswith("image/"):
                return [], "", ""
            chunks = bytearray()
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                chunks.extend(chunk)
                if len(chunks) > MAX_IMAGE_BYTES:
                    logger.debug("Skipping oversized candidate image.")
                    return [], "", ""
            content = bytes(chunks)
    except Exception as exc:
        logger.debug("Could not download image candidate: %s", exc)
        return [], "", ""

    try:
        with Image.open(io.BytesIO(content)) as image:
            image.verify()
        vector, kind = extract_face_vector_with_kind(content)
        return vector, kind, hashlib.sha256(content).hexdigest()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        logger.debug("Candidate was not a valid supported image: %s", exc)
        return [], "", ""
    except Exception as exc:
        logger.debug("Candidate analysis failed: %s", exc)
        return [], "", ""


def _extract_domain(url: str) -> str:
    return urlparse(url).hostname or ""
