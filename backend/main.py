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
from services.legal_email import LegalEmail
from services.pdf_dossier import PDFDossier
from fastapi.responses import Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

legal_email_service = LegalEmail()
pdf_dossier_service = PDFDossier()

app = FastAPI(
    title="DeepShield API",
    description="AI-Powered Deepfake Detection & Legal Takedown Platform",
    version="0.2.0",
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


# ─── Request / Response Models ───────────────────────────────────────────────

class CandidateMatch(BaseModel):
    url: str
    domain: str
    similarity: float
    thumbnail: str


class SearchRequest(BaseModel):
    vector: list[float]
    query_text: Optional[str] = None
    threshold: float = 0.55


class DossierRequest(BaseModel):
    victim_name: Optional[str] = "Aggrieved Individual"
    matches: list[CandidateMatch]


class TakedownRequest(BaseModel):
    target_url: str
    platform: str
    victim_name: Optional[str] = "Aggrieved Individual"
    hash_signature: Optional[str] = None


class TakedownResponse(BaseModel):
    status: str
    notice_type: str
    recipient: str
    timestamp: str
    dispatch_id: Optional[str] = None


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


@app.post("/api/dossier")
async def generate_cybercrime_dossier(request: DossierRequest):
    """
    Generates an official Cybercrime Complaint Dossier PDF in RAM
    for law enforcement submission (DPDP Act 2023 compliant).
    """
    try:
        matches_dict = [m.model_dump() for m in request.matches]
        pdf_bytes = pdf_dossier_service.generate_dossier_bytes(
            victim_name=request.victim_name or "Aggrieved Individual",
            matches=matches_dict,
        )
        logger.info("Generated cybercrime dossier PDF (%d bytes) for victim=%s", len(pdf_bytes), request.victim_name)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=DeepShield_Cybercrime_Dossier.pdf"
            },
        )
    except Exception as exc:
        logger.error("Failed to generate PDF dossier: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"PDF dossier generation failed: {str(exc)}",
        )


@app.post("/api/takedown/email", response_model=TakedownResponse)
async def dispatch_takedown_email(request: TakedownRequest) -> dict:
    """
    Dispatches a Rule 3(1)(b) IT Rules legal notice to the specified
    platform's designated grievance officer. Human-in-the-loop
    confirmation must be enforced on the frontend before this call.
    """
    recipient = _PLATFORM_RECIPIENTS.get(request.platform, "legal@unknown.com")
    hash_sig = request.hash_signature or ("pdq:" + hashlib.md5(request.target_url.encode()).hexdigest()[:16])

    try:
        dispatch_result = legal_email_service.send_notice(
            to_email=recipient,
            victim_name=request.victim_name or "Aggrieved Individual",
            platform_name=request.platform,
            content_url=request.target_url,
            hash_signature=hash_sig,
        )
    except Exception as exc:
        logger.error(
            "takedown dispatch failed: platform=%s recipient=%s url=%s error=%s",
            request.platform, recipient, request.target_url, exc,
        )
        raise HTTPException(
            status_code=502,
            detail=f"Legal notice email dispatch failed: {str(exc)}",
        )

    logger.info(
        "takedown dispatched: platform=%s recipient=%s url=%s id=%s",
        request.platform, recipient, request.target_url, dispatch_result.get("id"),
    )
    return {
        "status": dispatch_result.get("status", "dispatched"),
        "notice_type": "Rule 3(1)(b)",
        "recipient": recipient,
        "timestamp": dispatch_result.get("timestamp", datetime.now(timezone.utc).isoformat()),
        "dispatch_id": dispatch_result.get("id"),
    }
