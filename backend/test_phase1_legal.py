"""
Unit & Integration Tests for Phase 1 — Legal Notice Dispatch via Resend
Run with: python -m pytest backend/test_phase1_legal.py -v
"""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from main import app
from services.legal_email import LegalEmail

client = TestClient(app)


def test_generate_legal_notice():
    service = LegalEmail()
    notice = service.generate_legal_notice(
        victim_name="Jane Doe",
        platform_name="Meta",
        content_url="https://facebook.com/fake_profile_123",
        hash_signature="pdq:1234567890abcdef",
    )
    assert "LEGAL NOTICE - TAKEDOWN REQUEST" in notice
    assert "Rule 3(1)(b)" in notice
    assert "Jane Doe" in notice
    assert "https://facebook.com/fake_profile_123" in notice
    assert "pdq:1234567890abcdef" in notice
    assert "Meta" in notice
    assert "within 36 hours" in notice


def test_send_notice_simulation_when_no_api_key():
    service = LegalEmail(api_key=None)
    result = service.send_notice(
        to_email="fbgoindia@support.facebook.com",
        victim_name="Jane Doe",
        platform_name="Meta",
        content_url="https://facebook.com/fake_profile_123",
        hash_signature="pdq:1234567890abcdef",
    )
    assert result["status"] == "dispatched"
    assert result["id"] == "simulated_dispatch_id"
    assert result["recipient"] == "fbgoindia@support.facebook.com"
    assert "timestamp" in result


def test_send_notice_with_mocked_resend():
    service = LegalEmail(api_key="re_real_configured_key_123")
    with patch("resend.Emails.send") as mock_send:
        mock_send.return_value = {"id": "resend_email_id_999"}
        result = service.send_notice(
            to_email="abuse@google.com",
            victim_name="John Doe",
            platform_name="Google",
            content_url="https://youtube.com/watch?v=fake",
            hash_signature="pdq:abc",
        )
        assert result["status"] == "dispatched"
        assert result["id"] == "resend_email_id_999"
        assert result["recipient"] == "abuse@google.com"
        mock_send.assert_called_once()
        args = mock_send.call_args[0][0]
        assert args["to"] == ["abuse@google.com"]
        assert "Google" in args["subject"]
        assert "John Doe" in args["text"]


def test_send_notice_raises_runtime_error_on_resend_failure():
    service = LegalEmail(api_key="re_real_configured_key_123")
    with patch("resend.Emails.send", side_effect=Exception("API limit exceeded")):
        with pytest.raises(RuntimeError) as exc_info:
            service.send_notice(
                to_email="abuse@x.com",
                victim_name="Test",
                platform_name="X",
                content_url="https://x.com/fake",
                hash_signature="pdq:123",
            )
        assert "Resend delivery failed" in str(exc_info.value)


def test_api_takedown_endpoint():
    response = client.post(
        "/api/takedown/email",
        json={
            "target_url": "https://instagram.com/fake123",
            "platform": "Meta",
            "victim_name": "Test User",
            "hash_signature": "pdq:test123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "dispatched"
    assert data["notice_type"] == "Rule 3(1)(b)"
    assert data["recipient"] == "fbgoindia@support.facebook.com"
    assert "timestamp" in data


def test_api_takedown_endpoint_error_handling():
    with patch("services.legal_email.LegalEmail.send_notice", side_effect=RuntimeError("Connection dropped")):
        response = client.post(
            "/api/takedown/email",
            json={
                "target_url": "https://tiktok.com/@fake",
                "platform": "TikTok",
            },
        )
        assert response.status_code == 502
        assert "Connection dropped" in response.json()["detail"]
