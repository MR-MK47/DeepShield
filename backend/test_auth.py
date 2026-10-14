"""Unit tests for local SQLite operator accounts and opaque sessions."""
from services.auth import AuthError, AuthService


def test_register_login_and_logout(tmp_path):
    service = AuthService(str(tmp_path / "auth.sqlite3"))
    user, token = service.register("Test Operator", "User@Example.test", "a-strong-test-password")
    assert user["email"] == "user@example.test"
    assert service.get_user(token)["id"] == user["id"]

    same_user, second_token = service.login("USER@example.test", "a-strong-test-password")
    assert same_user["id"] == user["id"]
    assert second_token != token

    service.logout(token)
    assert service.get_user(token) is None
    assert service.get_user(second_token)["id"] == user["id"]


def test_bad_password_and_duplicate_email_are_rejected(tmp_path):
    service = AuthService(str(tmp_path / "auth.sqlite3"))
    service.register("Test Operator", "user@example.test", "a-strong-test-password")
    try:
        service.login("user@example.test", "wrong-password")
        assert False, "bad password should be rejected"
    except AuthError as exc:
        assert "incorrect" in str(exc).lower()
    try:
        service.register("Another Operator", "USER@example.test", "another-strong-password")
        assert False, "duplicate email should be rejected"
    except AuthError as exc:
        assert "already exists" in str(exc).lower()


def test_short_password_and_blank_name_are_rejected(tmp_path):
    service = AuthService(str(tmp_path / "auth.sqlite3"))
    for name, email, password in [
        ("Operator", "one@example.test", "short"),
        (" ", "two@example.test", "a-strong-test-password"),
    ]:
        try:
            service.register(name, email, password)
            assert False, "invalid registration should be rejected"
        except AuthError:
            pass
