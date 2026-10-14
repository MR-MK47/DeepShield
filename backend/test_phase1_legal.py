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


def test_generate_legal_notice_is_a_reviewable_request():
    notice = LegalEmail(api_key="").generate_legal_notice(
        victim_name="Jane Doe",
        platform_name="Meta",
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
    service = LegalEmail(api_key="")
    with pytest.raises(RuntimeError, match="not configured"):
        service.send_notice(
            to_email="grievance@example.test",
            victim_name="Jane Doe",
            platform_name="Meta",
            content_url="https://example.com/candidate.jpg",
            hash_signature="sha256:" + "a" * 64,
        )


def test_send_notice_with_mocked_resend():
    service = LegalEmail(api_key="re_test_key_for_mocking_only")
    with patch("resend.Emails.send", return_value={"id": "resend_email_id_999"}) as mock_send:
        result = service.send_notice(
            to_email="abuse@example.test",
            victim_name="John Doe",
            platform_name="Google",
            content_url="https://example.com/candidate.jpg",
            hash_signature="sha256:" + "b" * 64,
        )
    assert result["status"] == "accepted_by_provider"
    assert result["id"] == "resend_email_id_999"
    mock_send.assert_called_once()
    params = mock_send.call_args[0][0]
    assert params["to"] == ["abuse@example.test"]
    assert "John Doe" in params["text"]


def test_takedown_endpoint_requires_operator_authentication():
    response = client.post(
        "/api/takedown/email",
        json={
            "target_url": "https://example.com/candidate.jpg",
            "platform": "Meta",
            "hash_signature": "sha256:" + "c" * 64,
        },
    )
    assert response.status_code == 401


def test_takedown_endpoint_uses_mocked_provider_and_auth(monkeypatch):
    monkeypatch.setitem(main._PLATFORM_RECIPIENTS, "Meta", "meta-test-recipient@example.test")
    mocked_result = {
        "status": "accepted_by_provider",
        "id": "mock-id-123",
        "recipient": "fbgoindia@support.facebook.com",
        "timestamp": "2026-01-01T00:00:00+00:00",
    }
    with patch("main.legal_email_service.send_notice", return_value=mocked_result) as send:
        response = client.post(
            "/api/takedown/email",
            headers=auth_headers(),
            json={
                "target_url": "https://example.com/candidate.jpg",
                "platform": "Meta",
                "victim_name": "Test User",
                "hash_signature": "sha256:" + "d" * 64,
            },
        )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "accepted_by_provider"
    assert body["recipient"] == "meta-test-recipient@example.test"
    send.assert_called_once()


def test_unknown_platform_is_rejected_not_sent_to_fallback():
    with patch("main.legal_email_service.send_notice") as send:
        response = client.post(
            "/api/takedown/email",
            headers=auth_headers(),
            json={
                "target_url": "https://example.com/candidate.jpg",
                "platform": "UnknownNet",
                "hash_signature": "sha256:" + "e" * 64,
            },
        )
    assert response.status_code == 422
    send.assert_not_called()


def test_provider_error_is_returned_as_gateway_error(monkeypatch):
    monkeypatch.setitem(main._PLATFORM_RECIPIENTS, "TikTok", "tiktok-test-recipient@example.test")
    with patch("main.legal_email_service.send_notice", side_effect=RuntimeError("provider unavailable")):
        response = client.post(
            "/api/takedown/email",
            headers=auth_headers(),
            json={
                "target_url": "https://example.com/candidate.jpg",
                "platform": "TikTok",
                "hash_signature": "sha256:" + "f" * 64,
            },
        )
    assert response.status_code == 502
    assert "provider unavailable" in response.json()["detail"]
