"""Minimal local operator authentication backed by SQLite.

Passwords use PBKDF2-HMAC-SHA256; opaque session tokens are stored as SHA-256
hashes. This database stores account/session metadata only, never uploaded
images or biometric vectors.
"""
from __future__ import annotations

import hashlib
import json
import hmac
import os
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Any

_ITERATIONS = 310_000
_SESSION_SECONDS = 7 * 24 * 60 * 60


class AuthError(ValueError):
    """Expected account/authentication error."""


class AuthService:
    def __init__(self, database_path: str | None = None) -> None:
        default_path = Path(__file__).resolve().parents[1] / "deepshield_auth.db"
        self.database_path = str(database_path or os.getenv("AUTH_DB_PATH") or default_path)
        if self.database_path != ":memory:":
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    expires_at REAL NOT NULL,
                    created_at REAL NOT NULL
                )
            """)
            db.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)")
            db.execute("""
                CREATE TABLE IF NOT EXISTS scan_history (
                    scan_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    query_text TEXT NOT NULL,
                    threshold REAL NOT NULL,
                    matches_json TEXT NOT NULL,
                    match_count INTEGER NOT NULL,
                    created_at REAL NOT NULL
                )
            """)
            db.execute("CREATE INDEX IF NOT EXISTS idx_scan_history_user_time ON scan_history(user_id, created_at DESC)")

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def _hash_password(password: str, salt: bytes | None = None) -> str:
        salt = salt or secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
        return "pbkdf2_sha256$%d$%s$%s" % (_ITERATIONS, salt.hex(), digest.hex())

    @staticmethod
    def _verify_password(password: str, stored: str) -> bool:
        try:
            algorithm, iterations, salt_hex, expected = stored.split("$", 3)
            if algorithm != "pbkdf2_sha256":
                return False
            actual = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
            ).hex()
            return hmac.compare_digest(actual, expected)
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _public_user(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "created_at": row["created_at"],
        }

    def _new_session(self, user_id: int) -> str:
        token = secrets.token_urlsafe(32)
        now = time.time()
        with self._connect() as db:
            db.execute("DELETE FROM sessions WHERE expires_at <= ?", (now,))
            db.execute(
                "INSERT INTO sessions(token_hash, user_id, expires_at, created_at) VALUES (?, ?, ?, ?)",
                (hashlib.sha256(token.encode()).hexdigest(), user_id, now + _SESSION_SECONDS, now),
            )
        return token

    def register(self, name: str, email: str, password: str) -> tuple[dict[str, Any], str]:
        name = name.strip()
        email = self.normalize_email(email)
        if not name:
            raise AuthError("Name is required.")
        if len(password) < 8:
            raise AuthError("Password must contain at least 8 characters.")
        if len(email) > 254 or "@" not in email:
            raise AuthError("Enter a valid email address.")
        now = time.time()
        try:
            with self._connect() as db:
                cursor = db.execute(
                    "INSERT INTO users(name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                    (name[:120], email, self._hash_password(password), now),
                )
                user_id = int(cursor.lastrowid)
                row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        except sqlite3.IntegrityError as exc:
            raise AuthError("An account with this email already exists. Please sign in.") from exc
        assert row is not None
        return self._public_user(row), self._new_session(user_id)

    def login(self, email: str, password: str) -> tuple[dict[str, Any], str]:
        email = self.normalize_email(email)
        with self._connect() as db:
            row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if row is None or not self._verify_password(password, row["password_hash"]):
            raise AuthError("Email or password is incorrect.")
        return self._public_user(row), self._new_session(int(row["id"]))

    def get_user(self, token: str | None) -> dict[str, Any] | None:
        if not token:
            return None
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        now = time.time()
        with self._connect() as db:
            row = db.execute(
                """SELECT users.* FROM sessions
                   JOIN users ON users.id = sessions.user_id
                   WHERE sessions.token_hash = ? AND sessions.expires_at > ?""",
                (token_hash, now),
            ).fetchone()
            db.execute("DELETE FROM sessions WHERE expires_at <= ?", (now,))
        return self._public_user(row) if row is not None else None

    def logout(self, token: str | None) -> None:
        if not token:
            return
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        with self._connect() as db:
            db.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))


    def save_scan(
        self,
        user_id: int,
        query_text: str,
        threshold: float,
        matches: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Persist only candidate metadata after the operator explicitly opts in.

        Reference images and face vectors are never accepted by this method.
        """
        scan_id = secrets.token_urlsafe(16)
        created_at = time.time()
        safe_matches = []
        for match in matches[:100]:
            safe_matches.append({
                "url": str(match.get("url", ""))[:2048],
                "domain": str(match.get("domain", ""))[:255],
                "similarity": float(match.get("similarity", 0.0)),
                "thumbnail": str(match.get("thumbnail") or match.get("url", ""))[:2048],
                "hash_signature": str(match.get("hash_signature") or "")[:200],
            })
        encoded = json.dumps(safe_matches, ensure_ascii=False)
        with self._connect() as db:
            db.execute(
                """INSERT INTO scan_history
                   (scan_id, user_id, query_text, threshold, matches_json, match_count, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (scan_id, user_id, query_text[:200], threshold, encoded, len(safe_matches), created_at),
            )
        return {
            "scan_id": scan_id,
            "query_text": query_text[:200],
            "threshold": threshold,
            "matches": safe_matches,
            "match_count": len(safe_matches),
            "created_at": created_at,
        }

    def list_scans(self, user_id: int, limit: int = 25) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 100))
        with self._connect() as db:
            rows = db.execute(
                """SELECT scan_id, query_text, threshold, matches_json, match_count, created_at
                   FROM scan_history WHERE user_id = ?
                   ORDER BY created_at DESC LIMIT ?""",
                (user_id, limit),
            ).fetchall()
        return [{
            "scan_id": row["scan_id"],
            "query_text": row["query_text"],
            "threshold": row["threshold"],
            "matches": json.loads(row["matches_json"]),
            "match_count": row["match_count"],
            "created_at": row["created_at"],
        } for row in rows]

    def delete_scan(self, user_id: int, scan_id: str) -> bool:
        with self._connect() as db:
            cursor = db.execute(
                "DELETE FROM scan_history WHERE user_id = ? AND scan_id = ?",
                (user_id, scan_id),
            )
            return cursor.rowcount > 0
