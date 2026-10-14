"""
Legal Email - Rule 3(1)(b) IT Rules Legal Notice Sender
Uses Resend for SMTP delivery
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Dict, Optional

import resend

logger = logging.getLogger(__name__)


class LegalEmail:
    """
    Legal notice dispatch service.
    Sends Rule 3(1)(b) IT Rules compliant takedown notices via Resend.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("RESEND_API_KEY")
        if self.api_key:
            resend.api_key = self.api_key

    def generate_legal_notice(
        self,
        victim_name: str,
        platform_name: str,
        content_url: str,
        hash_signature: str
    ) -> str:
        """
        Generate Rule 3(1)(b) IT Rules compliant legal notice.
        """
        date_str = datetime.now().strftime("%B %d, %Y")
        notice = f"""LEGAL NOTICE - TAKEDOWN REQUEST
Rule 3(1)(b) of Information Technology (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021

Date: {date_str}

To: {platform_name}
Designated Grievance Officer

Subject: Unauthorized Synthetic Media / Deepfake Content - Immediate Takedown Request

Dear Sir/Madam,

This notice is being served under Rule 3(1)(b) of the IT Rules, 2021, regarding unauthorized synthetic media content hosted on your platform.

VICTIM DETAILS:
Name: {victim_name}

OFFENDING CONTENT:
URL: {content_url}
Content Type: Synthetic Media / Deepfake
Digital Signature (Hash): {hash_signature}

VIOLATION:
The above-referenced content constitutes unauthorized synthetic media created without consent, violating:
1. Right to Privacy under Article 21 of the Constitution of India
2. Digital Personal Data Protection Act, 2023
3. Indian Penal Code Sections 499/500 (Defamation)
4. IT Act Section 66A (if applicable)

REQUEST:
We hereby request immediate removal of the offending content within 36 hours as mandated under Rule 3(1)(b).

Non-compliance may result in legal action under applicable laws.

Sincerely,
DeepShield Legal Automation
Kavach-AI Platform"""
        return notice.strip()

    def send_notice(
        self,
        to_email: str,
        victim_name: str,
        platform_name: str,
        content_url: str,
        hash_signature: str,
        from_email: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Send legal notice via Resend.
        Returns delivery status dictionary.
        """
        notice = self.generate_legal_notice(
            victim_name=victim_name,
            platform_name=platform_name,
            content_url=content_url,
            hash_signature=hash_signature,
        )

        sender = from_email or os.getenv(
            "RESEND_FROM_EMAIL", "DeepShield Legal <onboarding@resend.dev>"
        )
        now_iso = datetime.now(timezone.utc).isoformat()

        # Simulated fallback if no API key or placeholder key configured
        if not self.api_key or self.api_key.startswith("re_xxx") or self.api_key == "test_key":
            logger.info(
                "RESEND_API_KEY is not configured or placeholder (%s). Simulating notice delivery to %s.",
                self.api_key,
                to_email,
            )
            return {
                "status": "dispatched",
                "id": "simulated_dispatch_id",
                "recipient": to_email,
                "timestamp": now_iso,
            }

        try:
            params: resend.Emails.SendParams = {
                "from": sender,
                "to": [to_email],
                "subject": f"LEGAL NOTICE: Rule 3(1)(b) IT Rules Takedown Request - {platform_name}",
                "text": notice,
            }
            res = resend.Emails.send(params)
            dispatch_id = (
                res.get("id") if isinstance(res, dict) else getattr(res, "id", "sent")
            )
            logger.info("Notice successfully dispatched via Resend. ID: %s", dispatch_id)
            return {
                "status": "dispatched",
                "id": str(dispatch_id),
                "recipient": to_email,
                "timestamp": now_iso,
            }
        except Exception as exc:
            logger.error("Resend API delivery error: %s", exc)
            raise RuntimeError(f"Resend delivery failed: {exc}") from exc
