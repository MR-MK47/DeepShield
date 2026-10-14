"""Tests for operator-reviewed email delivery. No test sends a real email."""
import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import main
from main import app, auth_service
from services.legal_email import LegalEmail

client = TestClient(app)


def auth_headers():
    _, token = auth_service.register(
        "Test Operator", f"operator-{uuid.uuid4().hex}@example.test", "safe-test-password-123"
    )
    return {"Authorization": f"Bearer {token}"}


def create_preview(headers, recipient="legal@example.test"):
    return client.post(
        "/api/takedown/preview",
        headers=headers,
        json={
            "target_url": "https://example.com/candidate.jpg",
            "recipient": recipient,
            "victim_name": "Test User",
            "hash_signature": "sha256:" + "d" * 64,
        },
    )


def test_generate_legal_notice_is_a_reviewable_request():
    notice = LegalEmail(api_key="").generate_legal_notice(
        victim_name="Jane Doe",
        platform_name="example.com",
        content_url="https://example.com/candidate.jpg",
        hash_signature="sha256:" + "a" * 64,
    )
    assert "REQUEST FOR REVIEW AND REMOVAL" in notice
    assert "Jane Doe" in notice
    assert "https://example.com/candidate.jpg" in notice
    assert "sha256:" in notice
    assert "does not itself establish" in notice
    assert "within 36 hours as mandated" not in notice
    assert "Section 66A" not in notice


def test_send_notice_refuses_missing_or_placeholder_api_key():
    service = LegalEmail(api_key="", mode="resend")
    with pytest.raises(RuntimeError, match="missing or a placeholder"):
        service.send_notice(
            to_email="grievance@example.test",
            victim_name="Jane Doe",
            platform_name="Meta",
            content_url="https://example.com/candidate.jpg",
            hash_signature="sha256:" + "a" * 64,
        )


def test_send_notice_with_mocked_resend():
    service = LegalEmail(api_key="re_test_key_for_mocking_only", mode="resend")
    with patch("resend.Emails.send", return_value={"id": "resend_email_id_999"}) as mock_send:
        result = service.send_notice(
            to_email="abuse@example.test",
            victim_name="John Doe",
            platform_name="example.com",
            content_url="https://example.com/candidate.jpg",
            hash_signature="sha256:" + "b" * 64,
            from_email="DeepShield Test <sender@example.test>",
        )
    assert result["status"] == "accepted_by_provider"
    assert result["id"] == "resend_email_id_999"
    mock_send.assert_called_once()
    params = mock_send.call_args[0][0]
    assert params["to"] == ["abuse@example.test"]
    assert "John Doe" in params["text"]


def test_dispatch_endpoint_requires_operator_authentication():
    response = client.post("/api/takedown/email", json={"preview_id": "x" * 43})
    assert response.status_code == 401


def test_dispatch_endpoint_requires_a_live_preview():
    response = client.post(
        "/api/takedown/email",
        headers=auth_headers(),
        json={"preview_id": "x" * 43},
    )
    assert response.status_code == 409
    assert "preview" in response.json()["detail"].lower()


def test_notice_preview_returns_recipient_and_never_sends(monkeypatch):
    monkeypatch.setattr(main.legal_email_service, "mode", "resend")
    headers = auth_headers()
    with patch("main.legal_email_service.send_notice") as send:
        denied = client.post(
            "/api/takedown/preview",
            json={
                "target_url": "https://example.com/candidate.jpg",
                "recipient": "legal@example.test",
                "hash_signature": "sha256:" + "9" * 64,
            },
        )
        assert denied.status_code == 401
        response = create_preview(headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["preview_id"]) >= 40
    assert body["recipient"] == "legal@example.test"
    assert "Test User" in body["notice_text"]
    assert "https://example.com/candidate.jpg" in body["notice_text"]
    assert body["expires_in_seconds"] > 0
    send.assert_not_called()


def test_notice_preview_requires_a_valid_custom_recipient():
    response = client.post(
        "/api/takedown/preview",
        headers=auth_headers(),
        json={
            "target_url": "https://example.com/candidate.jpg",
            "victim_name": "Test User",
            "hash_signature": "sha256:" + "d" * 64,
        },
    )
    assert response.status_code == 422


def test_takedown_endpoint_uses_only_reviewed_preview(monkeypatch):
    monkeypatch.setattr(main.legal_email_service, "mode", "resend")
    headers = auth_headers()
    preview = create_preview(headers)
    assert preview.status_code == 200, preview.text
    preview_id = preview.json()["preview_id"]
    mocked_result = {
        "status": "accepted_by_provider",
        "id": "mock-id-123",
        "recipient": "legal@example.test",
        "timestamp": "2026-01-01T00:00:00+00:00",
    }
    with patch("main.legal_email_service.send_notice", return_value=mocked_result) as send:
        response = client.post(
            "/api/takedown/email",
            headers=headers,
            json={"preview_id": preview_id},
        )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "accepted_by_provider"
    assert body["recipient"] == "legal@example.test"
    send.assert_called_once_with(
        to_email="legal@example.test",
        victim_name="Test User",
        platform_name="example.com",
        content_url="https://example.com/candidate.jpg",
        hash_signature="sha256:" + "d" * 64,
    )
    replay = client.post("/api/takedown/email", headers=headers, json={"preview_id": preview_id})
    assert replay.status_code == 409


def test_preview_cannot_be_used_by_a_different_operator(monkeypatch):
    monkeypatch.setattr(main.legal_email_service, "mode", "resend")
    preview = create_preview(auth_headers())
    assert preview.status_code == 200
    with patch("main.legal_email_service.send_notice") as send:
        response = client.post(
            "/api/takedown/email",
            headers=auth_headers(),
            json={"preview_id": preview.json()["preview_id"]},
        )
    assert response.status_code == 403
    send.assert_not_called()


def test_preview_accepts_a_website_not_in_a_fixed_platform_list():
    response = create_preview(auth_headers(), recipient="contact@small-site.example")
    assert response.status_code == 200, response.text
    assert response.json()["target_domain"] == "example.com"
    assert response.json()["recipient"] == "contact@small-site.example"


def test_provider_error_is_returned_as_gateway_error(monkeypatch):
    monkeypatch.setattr(main.legal_email_service, "mode", "resend")
    headers = auth_headers()
    preview = create_preview(headers, recipient="abuse@example.test")
    assert preview.status_code == 200
    with patch("main.legal_email_service.send_notice", side_effect=RuntimeError("provider unavailable")):
        response = client.post(
            "/api/takedown/email",
            headers=headers,
            json={"preview_id": preview.json()["preview_id"]},
        )
    assert response.status_code == 502
    assert "provider unavailable" in response.json()["detail"]


def test_default_test_mode_never_sends_email():
    service = LegalEmail(api_key="not-a-real-key", mode="mock")
    result = service.send_notice(
        to_email="LOCAL TEST MODE — no email will be sent",
        victim_name="Test User",
        platform_name="Meta",
        content_url="https://example.com/candidate.jpg",
        hash_signature="sha256:" + "1" * 64,
    )
    assert result["status"] == "simulated_not_sent"
    assert result["id"] == "local_test_no_email_sent"


def test_legacy_legal_notice_route_is_a_no_send_preview():
    response = client.post(
        "/api/legal-notice",
        headers=auth_headers(),
        json={
            "target_url": "https://example.com/candidate.jpg",
            "recipient": "contact@example.test",
            "victim_name": "Test User",
            "hash_signature": "sha256:" + "c" * 64,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["delivery_mode"] == "mock"
    assert body["recipient"] == "contact@example.test"
    assert body["preview_id"]


def test_notice_preview_rejects_local_network_url():
    response = client.post(
        "/api/takedown/preview",
        headers=auth_headers(),
        json={
            "target_url": "http://127.0.0.1/admin",
            "recipient": "contact@example.test",
            "hash_signature": "sha256:" + "c" * 64,
        },
    )
    assert response.status_code == 422
