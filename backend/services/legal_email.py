"""Operator-reviewed takedown request email service.

An accepted email-provider request is not proof that a platform has removed
content. No successful result is returned when the Resend key is missing.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Dict, Optional

import resend

logger = logging.getLogger(__name__)


class LegalEmail:
    """Create and send a reviewable takedown request through Resend."""

    def __init__(self, api_key: Optional[str] = None):
        configured = api_key if api_key is not None else os.getenv("RESEND_API_KEY", "")
        self.api_key = configured.strip()
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
Platform: {platform_name}
To: The platform's designated grievance or abuse team

Subject: Request to review suspected unauthorized synthetic or impersonating media

Dear Grievance Team,

I request a review of the content identified below. I believe it may involve
unauthorized use of my image or identity. Please review the report under your
applicable policies and the laws relevant to the facts and jurisdiction.

Complainant name supplied by operator: {victim_name}
Reported content URL: {content_url}
Evidence signature supplied by operator: {hash_signature}

Please acknowledge receipt and advise if further information is required.
This report is generated with software assistance. It should be checked for
accuracy and legal suitability by the complainant or a qualified adviser before
sending. A report does not itself establish that the content is unlawful.

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
        """Submit the reviewed notice to Resend and return provider acceptance."""
        if not self.api_key or self.api_key.startswith("re_xxx") or self.api_key == "test_key":
            raise RuntimeError(
                "Email delivery is not configured. Set a valid RESEND_API_KEY in backend/.env."
            )
        sender = from_email or os.getenv(
            "RESEND_FROM_EMAIL", "DeepShield Legal <onboarding@resend.dev>"
        )
        notice = self.generate_legal_notice(
            victim_name=victim_name,
            platform_name=platform_name,
            content_url=content_url,
            hash_signature=hash_signature,
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
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            logger.error("Resend delivery error: %s", exc)
            raise RuntimeError(f"Email provider could not accept the notice: {exc}") from exc
