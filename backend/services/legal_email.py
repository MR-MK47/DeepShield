"""
Legal Email - Rule 3(1)(b) IT Rules Legal Notice Sender
Uses Resend for SMTP delivery
"""

import resend
from typing import Optional, Dict
from datetime import datetime


class LegalEmail:
    """
    Legal notice dispatch service.
    Sends Rule 3(1)(b) IT Rules compliant takedown notices.
    """

    def __init__(self, api_key: Optional[str] = None):
        if api_key:
            resend.api_key = api_key

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
        notice = f"""
LEGAL NOTICE - TAKEDOWN REQUEST
Rule 3(1)(b) of Information Technology (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021

Date: {datetime.now().strftime("%B %d, %Y")}

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
Kavach-AI Platform
        """
        return notice.strip()

    def send_notice(
        self,
        to_email: str,
        victim_name: str,
        platform_name: str,
        content_url: str,
        hash_signature: str
    ) -> Dict[str, str]:
        """
        Send legal notice via Resend.
        Returns delivery status.
        """
        notice = self.generate_legal_notice(
            victim_name,
            platform_name,
            content_url,
            hash_signature
        )

        # TODO: Implement actual email sending
        # Requires RESEND_API_KEY environment variable
        raise NotImplementedError("Email sending requires API key configuration")
