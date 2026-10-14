"""Operator-reviewed takedown request email service.

Local test mode is the safe default and never sends email. Live delivery requires
explicit NOTICE_EMAIL_MODE=resend plus a valid Resend API key and verified
recipient configuration. Provider acceptance is not proof of removal.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Dict, Optional

import resend

logger = logging.getLogger(__name__)


class LegalEmail:
    """Create a reviewable notice and optionally submit it via Resend."""

    def __init__(self, api_key: Optional[str] = None, mode: Optional[str] = None):
        self.api_key = (api_key if api_key is not None else os.getenv("RESEND_API_KEY", "")).strip()
        self.mode = (mode or os.getenv("NOTICE_EMAIL_MODE") or "mock").strip().lower()
        if self.mode not in {"mock", "resend"}:
            raise ValueError("NOTICE_EMAIL_MODE must be either 'mock' or 'resend'.")
        if self.api_key:
            resend.api_key = self.api_key

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
        """Run a no-send local test or submit a notice to Resend."""
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

        if not self.api_key or self.api_key.startswith("re_xxx") or self.api_key == "test_key":
            raise RuntimeError(
                "Live email delivery is enabled but RESEND_API_KEY is missing or a placeholder."
            )
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
