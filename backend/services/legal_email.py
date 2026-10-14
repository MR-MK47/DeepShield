"""Operator-reviewed takedown request email service.

Local test mode is the safe default and never sends email. Live delivery requires
explicit NOTICE_EMAIL_MODE=resend plus a valid Resend API key and verified
recipient configuration. Provider acceptance is not proof of removal.
"""
from __future__ import annotations

import logging
import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import make_msgid
from typing import Dict, Optional

import resend

logger = logging.getLogger(__name__)


class LegalEmail:
    """Create a reviewable notice and optionally submit it via Resend."""

    def __init__(self, api_key: Optional[str] = None, mode: Optional[str] = None):
        self.api_key = (api_key if api_key is not None else os.getenv("RESEND_API_KEY", "")).strip()
        self.mode = (mode or os.getenv("NOTICE_EMAIL_MODE") or "mock").strip().lower()
        if self.mode not in {"mock", "resend", "smtp"}:
            raise ValueError("NOTICE_EMAIL_MODE must be either 'mock', 'resend', or 'smtp'.")
        if self.api_key:
            resend.api_key = self.api_key

        self.smtp_host = os.getenv("SMTP_HOST", "").strip()
        try:
            self.smtp_port = int(os.getenv("SMTP_PORT", "587").strip())
        except ValueError as exc:
            raise ValueError("SMTP_PORT must be an integer.") from exc
        self.smtp_username = os.getenv("SMTP_USERNAME", "").strip()
        self.smtp_password = os.getenv("SMTP_PASSWORD", "").replace(" ", "").strip()
        self.smtp_from_email = (
            os.getenv("SMTP_FROM_EMAIL", "").strip() or self.smtp_username
        )

    def generate_legal_notice(
        self,
        victim_name: str,
        platform_name: str,
        content_url: str,
        hash_signature: str,
    ) -> str:
        """Generate a request template for operator review, not legal advice."""
        date_str = datetime.now(timezone.utc).strftime("%B %d, %Y")
        return f"""REQUEST FOR REVIEW AND REMOVAL OF SUSPECTED UNAUTHORIZED MEDIA

Date: {date_str}
Website associated with the reported URL: {platform_name}
To: Public contact address listed for this website

Subject: Request to review reported content hosted on {platform_name}

Dear Website Contact Team,

I request a review of the content identified below. It may involve unauthorized
use of the named individual's image or identity. Please review the facts under
your applicable policies and the laws relevant to the circumstances.

Name supplied by the operator: {victim_name}
Reported content URL: {content_url}
Evidence signature supplied by the operator: {hash_signature}

If this inbox is not responsible for copyright, privacy, impersonation, or abuse
reports, please forward this request to the appropriate department or advise the
correct reporting channel. Please acknowledge receipt if possible.

This report was prepared with software assistance. The named person or an
authorized representative should verify the facts, the recipient, and the legal
suitability before sending. A similarity result is not proof that content is
synthetic or unlawful.

Regards,
{victim_name}
Prepared using DeepShield

This is a report template, not legal advice or a guarantee of removal timing.
""".strip()

    def send_notice(
        self,
        to_email: str,
        victim_name: str,
        platform_name: str,
        content_url: str,
        hash_signature: str,
        from_email: Optional[str] = None,
    ) -> Dict[str, str]:
        """Run a no-send local test or submit a notice using SMTP or Resend."""
        now_iso = datetime.now(timezone.utc).isoformat()
        if self.mode == "mock":
            logger.warning(
                "NOTICE TEST MODE: no email sent. platform=%s recipient_label=%s url=%s",
                platform_name, to_email, content_url,
            )
            return {
                "status": "simulated_not_sent",
                "id": "local_test_no_email_sent",
                "recipient": to_email,
                "timestamp": now_iso,
            }

        notice = self.generate_legal_notice(
            victim_name=victim_name,
            platform_name=platform_name,
            content_url=content_url,
            hash_signature=hash_signature,
        )
        if self.mode == "smtp":
            message_id = self._send_smtp(
                to_email=to_email,
                subject=f"Request for review of reported content - {platform_name}",
                body=notice,
            )
            return {
                "status": "accepted_by_smtp",
                "id": message_id,
                "recipient": to_email,
                "timestamp": now_iso,
            }

        if not self.api_key or self.api_key.startswith("re_xxx") or self.api_key == "test_key":
            raise RuntimeError(
                "Resend delivery is enabled but RESEND_API_KEY is missing or a placeholder."
            )
        # In Resend mode, only send from a verified domain for external recipients.
        notice = self.generate_legal_notice(
            victim_name=victim_name,
            platform_name=platform_name,
            content_url=content_url,
            hash_signature=hash_signature,
        )
        sender = from_email or os.getenv(
            "RESEND_FROM_EMAIL", "DeepShield Legal <onboarding@resend.dev>"
        )
        if "onboarding@resend.dev" in sender.lower():
            raise RuntimeError(
                "RESEND_FROM_EMAIL still uses Resend's test sender. Set it to an address on a domain verified in your Resend account to email external website contacts."
            )
        try:
            params: resend.Emails.SendParams = {
                "from": sender,
                "to": [to_email],
                "subject": f"Request for review of reported content - {platform_name}",
                "text": notice,
            }
            response = resend.Emails.send(params)
            dispatch_id = response.get("id") if isinstance(response, dict) else getattr(response, "id", None)
            if not dispatch_id:
                raise RuntimeError("Email provider did not return an acceptance identifier.")
            logger.info("Email provider accepted notice id=%s", dispatch_id)
            return {
                "status": "accepted_by_provider",
                "id": str(dispatch_id),
                "recipient": to_email,
                "timestamp": now_iso,
            }
        except Exception as exc:
            logger.error("Resend delivery error: %s", exc)
            raise RuntimeError(f"Email provider could not accept the notice: {exc}") from exc

    def send_test_email(self, to_email: str, operator_name: str) -> Dict[str, str]:
        """Send one real test email to the signed-in operator via configured SMTP."""
        if self.mode != "smtp":
            raise RuntimeError(
                "Test email requires NOTICE_EMAIL_MODE=smtp and valid SMTP settings."
            )
        recipient = to_email.strip()
        if not recipient or "@" not in recipient:
            raise RuntimeError("The signed-in operator account does not have a valid email address.")
        sent_at = datetime.now(timezone.utc).isoformat()
        body = (
            "DeepShield SMTP delivery test\n\n"
            f"Hello {operator_name},\n\n"
            "This message was submitted by DeepShield using the SMTP server configured "
            "in your local backend environment. If you receive it in this mailbox, "
            "the application's authenticated SMTP delivery path is working.\n\n"
            f"Sent at (UTC): {sent_at}\n"
            "Note: SMTP server acceptance does not guarantee inbox placement; check spam "
            "or junk folders if it is not visible in the inbox."
        )
        message_id = self._send_smtp(
            to_email=recipient,
            subject="DeepShield — SMTP delivery test",
            body=body,
        )
        return {
            "status": "accepted_by_smtp",
            "id": message_id,
            "recipient": recipient,
            "timestamp": sent_at,
        }

    def _send_smtp(self, to_email: str, subject: str, body: str) -> str:
        """Submit a single message over authenticated STARTTLS or implicit-TLS SMTP."""
        if not self.smtp_host or not self.smtp_username or not self.smtp_password:
            raise RuntimeError(
                "SMTP delivery needs SMTP_HOST, SMTP_USERNAME, and SMTP_PASSWORD in backend/.env."
            )
        if not 1 <= self.smtp_port <= 65535:
            raise RuntimeError("SMTP_PORT must be between 1 and 65535.")
        sender = self.smtp_from_email
        if not sender or "@" not in sender:
            raise RuntimeError("Set SMTP_FROM_EMAIL to an address permitted by your SMTP account.")

        message = EmailMessage()
        message["From"] = sender
        message["To"] = to_email
        message["Subject"] = subject
        message["Message-ID"] = make_msgid(domain=None)
        message.set_content(body)
        context = ssl.create_default_context()

        try:
            if self.smtp_port == 465:
                with smtplib.SMTP_SSL(
                    self.smtp_host, self.smtp_port, timeout=20, context=context
                ) as server:
                    server.login(self.smtp_username, self.smtp_password)
                    server.send_message(message)
            else:
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=20) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login(self.smtp_username, self.smtp_password)
                    server.send_message(message)
        except (OSError, smtplib.SMTPException) as exc:
            logger.warning("SMTP submission failed: %s", exc)
            raise RuntimeError(
                f"SMTP server could not accept the email: {exc}"
            ) from exc

        return str(message["Message-ID"])
