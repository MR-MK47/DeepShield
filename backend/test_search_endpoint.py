"""Deterministic OSINT utility tests; no local server or external search is needed."""
from services.osint_search import _extract_domain, _is_public_http_url


def test_extract_domain():
    assert _extract_domain("https://images.example.org/photo.jpg?q=1") == "images.example.org"


def test_url_policy_rejects_non_http_local_and_embedded_credentials():
    assert not _is_public_http_url("file:///etc/passwd")
    assert not _is_public_http_url("http://127.0.0.1/secret")
    assert not _is_public_http_url("http://localhost/admin")
    assert not _is_public_http_url("https://user:password@example.com/image.png")


def test_url_policy_accepts_public_literal_ip():
    assert _is_public_http_url("https://1.1.1.1/cdn-cgi/image/test.png")
