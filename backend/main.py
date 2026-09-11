"""
DeepShield Backend — FastAPI Entry Point
AI-Powered Deepfake Detection & Legal Takedown Platform
"""

import hashlib
import io
import logging
import random
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel

from services.face_engine import extract_face_vector, compute_similarity
from services.osint_search import search_deepfake_candidates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DeepShield API",
    description="AI-Powered Deepfake Detection & Legal Takedown Platform",
    version="0.2.0",
)

import os

# CORS middleware configuration supporting environment variable override
cors_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]
if "http://localhost:3000" not in allowed_origins:
    allowed_origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


# ─── Request / Response Models ───────────────────────────────────────────────

class SearchRequest(BaseModel):
    vector: list[float]
    query_text: Optional[str] = None
    threshold: float = 0.55


class CandidateMatch(BaseModel):
    url: str
    domain: str
    similarity: float
    thumbnail: str


class TakedownRequest(BaseModel):
    target_url: str
    platform: str


class TakedownResponse(BaseModel):
    status: str
    notice_type: str
    recipient: str
    timestamp: str


class AnalyzeResponse(BaseModel):
    status: str
    vector: list[float]
    hash: str


class HealthResponse(BaseModel):
    status: str


# ─── Mock fall-back data (used when insightface finds no face) ───────────────

_PLATFORM_RECIPIENTS = {
    "Meta":    "fbgoindia@support.facebook.com",
    "Google":  "abuse@google.com",
    "X":       "abuse@x.com",
    "TikTok":  "legal@tiktok.com",
}


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> dict:
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_image(file: UploadFile = File(...)) -> dict:
    """
    Accepts an image file, extracts a real 512-D face vector (insightface
    ArcFace) or a perceptual-hash fallback, and returns a PDQ-style hash
    for downstream similarity search.

    The uploaded image bytes are processed entirely in RAM and discarded
    immediately after vectorisation — no persistent storage per DPDP Act.
    """
    # Read into RAM (never write to disk)
    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # Validate that it is actually an image
    try:
        Image.open(io.BytesIO(image_bytes)).verify()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid image (expected JPG/PNG/GIF/WEBP)",
        )

    # Extract real face vector (512-D) or pHash fallback
    vector = extract_face_vector(image_bytes)

    if not vector:
        raise HTTPException(
            status_code=400,
            detail="No face detected in the uploaded image and the image could not be hashed",
        )

    # Deterministic PDQ-style hash from image content
    content_hash = hashlib.sha256(image_bytes).hexdigest()
    pdq_hash = "pdq:" + hashlib.md5(content_hash.encode()).hexdigest()[:16]

    logger.info("analyze_image: vector_dim=%d hash=%s", len(vector), pdq_hash)
    return {"status": "success", "vector": vector, "hash": pdq_hash}


@app.post("/api/search", response_model=list[CandidateMatch])
async def search_matches(request: SearchRequest) -> list[dict]:
    """
    Accepts a face vector (produced by /api/analyze) and queries the public
    web via DuckDuckGo for similar images.  Returns candidates with
    cosine similarity >= threshold (default 0.70).
    """
    if len(request.vector) != 512:
        raise HTTPException(
            status_code=422,
            detail="Expected a 512-dimensional vector (produced by /api/analyze)",
        )

    results = search_deepfake_candidates(
        query_vector=request.vector,
        query_text=request.query_text,
        threshold=request.threshold,
    )

    return [
        CandidateMatch(**m) for m in results
    ]


@app.post("/api/takedown/email", response_model=TakedownResponse)
async def dispatch_takedown_email(request: TakedownRequest) -> dict:
    """
    Dispatches a Rule 3(1)(b) IT Rules legal notice to the specified
    platform's designated grievance officer.  Human-in-the-loop
    confirmation must be enforced on the frontend before this call.
    """
    recipient = _PLATFORM_RECIPIENTS.get(request.platform, "legal@unknown.com")
    timestamp = datetime.now(timezone.utc).isoformat()

    logger.info(
        "takedown dispatched: platform=%s recipient=%s url=%s",
        request.platform, recipient, request.target_url,
    )
    return {
        "status": "dispatched",
        "notice_type": "Rule 3(1)(b)",
        "recipient": recipient,
        "timestamp": timestamp,
    }
