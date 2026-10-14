"""PDF dossier tests. TestClient calls remain offline and do not store reports."""
import uuid

from fastapi.testclient import TestClient

from main import app, auth_service
from services.pdf_dossier import PDFDossier

client = TestClient(app)


def auth_headers():
    _, token = auth_service.register(
        "PDF Test", f"pdf-{uuid.uuid4().hex}@example.test", "safe-test-password-123"
    )
    return {"Authorization": f"Bearer {token}"}


def test_pdf_dossier_service_bytes():
    service = PDFDossier()
    pdf_bytes = service.generate_dossier_bytes(
        victim_name="Jane & Doe",
        matches=[{
            "url": "https://example.com/a?x=1&y=2",
            "domain": "example.com",
            "similarity": 0.89,
            "hash_signature": "sha256:" + "1" * 64,
        }],
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF-")


def test_api_dossier_endpoint():
    response = client.post(
        "/api/dossier",
        headers=auth_headers(),
        json={
            "victim_name": "Jane Doe",
            "matches": [{
                "url": "https://example.com/candidate",
                "domain": "example.com",
                "similarity": 0.92,
                "thumbnail": "https://example.com/thumb.jpg",
                "hash_signature": "sha256:" + "2" * 64,
            }],
        },
    )
    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("application/pdf")
    assert "attachment" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF-")


def test_api_dossier_requires_authentication():
    response = client.post("/api/dossier", json={"victim_name": "Test", "matches": [{
        "url": "https://example.com/candidate",
        "domain": "example.com",
        "similarity": 0.5,
        "thumbnail": "https://example.com/candidate",
    }]})
    assert response.status_code == 401
