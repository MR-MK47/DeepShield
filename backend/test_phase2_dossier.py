"""
Unit & Integration Tests for Phase 2 — Cybercrime Dossier PDF Generation Endpoint
Run with: python -m pytest backend/test_phase2_dossier.py -v
"""

from fastapi.testclient import TestClient
from main import app
from services.pdf_dossier import PDFDossier

client = TestClient(app)


def test_pdf_dossier_service_bytes():
    service = PDFDossier()
    matches = [
        {
            "url": "https://example.com/deepfake1.jpg",
            "domain": "example.com",
            "similarity": 0.89,
            "hash_signature": "pdq:1234567890abcdef",
        }
    ]
    pdf_bytes = service.generate_dossier_bytes(
        victim_name="Jane Doe",
        matches=matches,
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF-")


def test_api_dossier_endpoint():
    response = client.post(
        "/api/dossier",
        json={
            "victim_name": "Jane Doe",
            "matches": [
                {
                    "url": "https://instagram.com/fake_profile",
                    "domain": "instagram.com",
                    "similarity": 0.92,
                    "thumbnail": "https://instagram.com/thumb.jpg",
                }
            ],
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    pdf_content = response.content
    assert pdf_content.startswith(b"%PDF-")
    assert len(pdf_content) > 500


def test_api_dossier_endpoint_empty_matches():
    response = client.post(
        "/api/dossier",
        json={
            "victim_name": "Test User",
            "matches": [],
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")
