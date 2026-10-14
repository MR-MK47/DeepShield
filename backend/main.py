"""DeepShield API: image candidate search and operator-reviewed actions.

The application never writes reference uploads or face vectors to its own database.
Operators/accounts and opaque session-token hashes are persisted in SQLite.
"""
from __future__ import annotations

import io
import logging
import os
import re

from dotenv import load_dotenv

load_dotenv()
from datetime import datetime, timezone
from typing import Literal, Optional
from urllib.parse import urlparse

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field

from services.auth import AuthError, AuthService
from services.face_engine import extract_face_vector_with_kind
from services.hash_engine import HashEngine
from services.legal_email import LegalEmail
from services.osint_search import search_deepfake_candidates
from services.pdf_dossier import PDFDossier

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
MAX_IMAGE_PIXELS = int(os.getenv("MAX_IMAGE_PIXELS", "20000000"))
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS

auth_service = AuthService()
hash_engine = HashEngine()
legal_email_service = LegalEmail()
pdf_dossier_service = PDFDossier()

app = FastAPI(
    title="DeepShield API",
    description="Candidate image search and operator-reviewed reporting tools.",
    version="1.0.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

Platform = Literal["Meta", "Google", "X", "TikTok"]
_PLATFORM_RECIPIENTS = {
    "Meta": os.getenv("META_GRIEVANCE_EMAIL", "").strip(),
    "Google": os.getenv("GOOGLE_ABUSE_EMAIL", "").strip(),
    "X": os.getenv("X_ABUSE_EMAIL", "").strip(),
    "TikTok": os.getenv("TIKTOK_LEGAL_EMAIL", "").strip(),
}


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=256)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=256)


class AuthResponse(BaseModel):
    status: str
    token: str
    user: dict


class CandidateMatch(BaseModel):
    url: str = Field(min_length=8, max_length=2048)
    domain: str = Field(min_length=1, max_length=255)
    similarity: float = Field(ge=-1.0, le=1.0)
    thumbnail: str = Field(min_length=1, max_length=2048)
    hash_signature: Optional[str] = Field(default=None, max_length=200)


class SearchRequest(BaseModel):
    vector: list[float] = Field(min_length=512, max_length=512)
    query_text: Optional[str] = Field(default=None, max_length=200)
    threshold: float = Field(default=0.30, ge=0.0, le=1.0)


class DossierRequest(BaseModel):
    victim_name: str = Field(default="Aggrieved Individual", min_length=1, max_length=120)
    matches: list[CandidateMatch] = Field(min_length=1, max_length=100)


class TakedownRequest(BaseModel):
    target_url: str = Field(min_length=8, max_length=2048)
    platform: Platform
    victim_name: str = Field(default="Aggrieved Individual", min_length=1, max_length=120)
    hash_signature: str = Field(min_length=1, max_length=200)


class HealthResponse(BaseModel):
    status: str


def _current_user(authorization: str | None = Header(default=None)) -> dict:
    """Require a valid operator bearer token for legal/evidence actions."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Sign in to perform this action.")
    token = authorization.removeprefix("Bearer ").strip()
    user = auth_service.get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Session expired or invalid. Please sign in again.")
    return user


def _validate_evidence_signature(value: str) -> None:
    if not re.fullmatch(r"sha256:[0-9a-fA-F]{64}", value):
        raise HTTPException(
            status_code=422,
            detail="A candidate SHA-256 content signature is required; run a fresh search before reporting this item.",
        )


def _validate_http_url(value: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise HTTPException(status_code=422, detail="Target must be a valid public HTTP or HTTPS URL.")
    if parsed.username or parsed.password:
        raise HTTPException(status_code=422, detail="URLs containing embedded credentials are not accepted.")
    host = parsed.hostname.lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise HTTPException(status_code=422, detail="Local network URLs are not accepted.")
    import ipaddress
    try:
        address = ipaddress.ip_address(host)
        if not address.is_global:
            raise HTTPException(status_code=422, detail="Private or reserved IP addresses are not accepted.")
    except ValueError:
        pass


@app.get("/", response_model=HealthResponse)
@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> dict:
    return {"status": "ok"}


@app.post("/api/auth/register", response_model=AuthResponse)
async def register_operator(request: RegisterRequest) -> dict:
    try:
        user, token = auth_service.register(request.name, request.email, request.password)
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "created", "token": token, "user": user}


@app.post("/api/auth/login", response_model=AuthResponse)
async def login_operator(request: LoginRequest) -> dict:
    try:
        user, token = auth_service.login(request.email, request.password)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return {"status": "authenticated", "token": token, "user": user}


@app.get("/api/auth/me")
async def get_current_operator(user: dict = Depends(_current_user)) -> dict:
    return {"user": user}


@app.post("/api/auth/logout")
async def logout_operator(authorization: str | None = Header(default=None)) -> dict:
    token = authorization.removeprefix("Bearer ").strip() if authorization and authorization.startswith("Bearer ") else None
    auth_service.logout(token)
    return {"status": "signed_out"}


@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...)) -> dict:
    """Validate an image and compute a face embedding or clearly typed fallback."""
    try:
        image_bytes = await file.read(MAX_UPLOAD_BYTES + 1)
        if not image_bytes:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")
        if len(image_bytes) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail=f"Image exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB upload limit.")
        try:
            with Image.open(io.BytesIO(image_bytes)) as image:
                width, height = image.size
                if width * height > MAX_IMAGE_PIXELS:
                    raise HTTPException(status_code=413, detail="Image dimensions are too large to process safely.")
                image.verify()
        except HTTPException:
            raise
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Upload a valid JPG, PNG, WEBP or GIF image.") from exc

        try:
            vector, vector_kind = extract_face_vector_with_kind(image_bytes)
            with Image.open(io.BytesIO(image_bytes)) as image:
                signature = hash_engine.compute_best_hash(image.convert("RGB"))
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Image analysis failed")
            raise HTTPException(status_code=422, detail="The image could not be analysed. Try a clearer, smaller image.") from exc
        if len(vector) != 512:
            raise HTTPException(status_code=422, detail="No usable face or perceptual representation could be extracted.")
        return {
            "status": "success",
            "vector": vector,
            "vector_kind": vector_kind,
            "hash": signature,
            "hash_kind": signature.split(":", 1)[0],
        }
    finally:
        await file.close()


@app.post("/api/search", response_model=list[CandidateMatch])
async def search_matches(request: SearchRequest) -> list[dict]:
    if not all(__import__("math").isfinite(value) for value in request.vector):
        raise HTTPException(status_code=422, detail="Vector contains invalid numeric values.")
    results = search_deepfake_candidates(
        query_vector=request.vector,
        query_text=request.query_text,
        threshold=request.threshold,
    )
    return [CandidateMatch(**match).model_dump() for match in results]


@app.post("/api/dossier")
async def generate_cybercrime_dossier(
    request: DossierRequest,
    user: dict = Depends(_current_user),
):
    """Generate a PDF only for a signed-in operator's explicit UI request."""
    try:
        matches = [match.model_dump() for match in request.matches]
        pdf_bytes = pdf_dossier_service.generate_dossier_bytes(
            victim_name=request.victim_name,
            matches=matches,
        )
        logger.info("Generated dossier (%d bytes) for operator_id=%s", len(pdf_bytes), user["id"])
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="DeepShield_Cybercrime_Dossier.pdf"'},
        )
    except Exception as exc:
        logger.exception("PDF dossier generation failed")
        raise HTTPException(status_code=500, detail="PDF dossier generation failed. Check server logs.") from exc


@app.post("/api/takedown/preview")
async def preview_takedown_email(
    request: TakedownRequest,
    user: dict = Depends(_current_user),
) -> dict:
    """Return the exact recipient and notice text for operator review; sends nothing."""
    _validate_http_url(request.target_url)
    _validate_evidence_signature(request.hash_signature)
    recipient = _PLATFORM_RECIPIENTS[request.platform]
    if not recipient:
        raise HTTPException(
            status_code=503,
            detail=f"No verified recipient is configured for {request.platform}. Set the platform contact in backend/.env after checking the official contact details.",
        )
    notice = legal_email_service.generate_legal_notice(
        victim_name=request.victim_name,
        platform_name=request.platform,
        content_url=request.target_url,
        hash_signature=request.hash_signature,
    )
    return {
        "recipient": recipient,
        "notice_type": "Operator-reviewed takedown request",
        "notice_text": notice,
        "prepared_for_operator_id": user["id"],
    }


@app.post("/api/takedown/email")
async def dispatch_takedown_email(
    request: TakedownRequest,
    user: dict = Depends(_current_user),
) -> dict:
    """Dispatch a notice after a separate operator review/confirmation step in the UI."""
    _validate_http_url(request.target_url)
    recipient = _PLATFORM_RECIPIENTS[request.platform]
    if not recipient:
        raise HTTPException(
            status_code=503,
            detail=f"No verified recipient is configured for {request.platform}. Set the platform contact in backend/.env after checking the official contact details.",
        )
    try:
        dispatch_result = legal_email_service.send_notice(
            to_email=recipient,
            victim_name=request.victim_name,
            platform_name=request.platform,
            content_url=request.target_url,
            hash_signature=request.hash_signature,
        )
    except RuntimeError as exc:
        logger.warning("Notice delivery failed for operator_id=%s platform=%s", user["id"], request.platform)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected notice dispatch failure")
        raise HTTPException(status_code=502, detail="Email provider failed to dispatch the notice.") from exc

    return {
        "status": dispatch_result["status"],
        "notice_type": "Operator-reviewed takedown request",
        "recipient": recipient,
        "timestamp": dispatch_result["timestamp"],
        "dispatch_id": dispatch_result.get("id"),
    }
