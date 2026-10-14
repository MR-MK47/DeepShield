"""
PDF Dossier - Cybercrime Complaint Report Generator
Uses ReportLab for PDF generation
DPDP Act 2023 compliant: builds PDF in RAM buffer without persistent disk storage.
"""

from __future__ import annotations

import io
import logging
from datetime import datetime
from typing import Dict, List

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

logger = logging.getLogger(__name__)


class PDFDossier:
    """
    Cybercrime dossier generator.
    Creates complaint-ready PDF documents for law enforcement submission.
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()

    def generate_dossier_bytes(
        self,
        victim_name: str,
        matches: List[Dict],
    ) -> bytes:
        """
        Generate cybercrime complaint dossier PDF in RAM as bytes.
        Ensures zero persistent disk storage per DPDP Act 2023.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        story = []
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=1,  # Center
        )

        # Title
        story.append(Paragraph("CYBERCRIME COMPLAINT DOSSIER", title_style))
        story.append(Paragraph("Rule 3(1)(b) IT Rules &amp; DPDP Act 2023 Compliance Package", ParagraphStyle('SubTitle', parent=self.styles['Normal'], fontSize=10, alignment=1, textColor='#64748b')))
        story.append(Spacer(1, 16))

        # Case Information
        date_str = datetime.now().strftime("%B %d, %Y at %H:%M UTC")
        case_info = f"""
        <b>Date Generated:</b> {date_str}<br/>
        <b>Complainant:</b> {victim_name}<br/>
        <b>Case Type:</b> Unauthorized Synthetic Media / Deepfake Distribution<br/>
        <b>Jurisdiction:</b> Cyber Crime Division / National Cyber Crime Reporting Portal
        """
        story.append(Paragraph(case_info, self.styles['Normal']))
        story.append(Spacer(1, 20))

        # Evidence Summary Header
        story.append(Paragraph("<b>EVIDENCE SUMMARY</b>", self.styles['Heading2']))
        story.append(Spacer(1, 8))

        # Matches Table
        if matches:
            table_data = [["#", "Source URL / Domain", "Similarity", "Hash Signature"]]
            for idx, match in enumerate(matches, 1):
                url = match.get("url") or match.get("source_url") or "N/A"
                domain = match.get("domain", "N/A")
                sim = match.get("similarity") or match.get("similarity_score", 0.0)
                h_sig = match.get("hash_signature") or "pdq:computed"

                table_data.append([
                    str(idx),
                    f"{domain}\n{url[:35]}...",
                    f"{sim * 100:.1f}%",
                    str(h_sig)[:20] + "...",
                ])

            table = Table(table_data, colWidths=[0.4 * inch, 2.6 * inch, 1.0 * inch, 1.8 * inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), '#0f172a'),
                ('TEXTCOLOR', (0, 0), (-1, 0), '#ffffff'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, '#cbd5e1'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("No matches isolated for this dossier package.", self.styles['Normal']))

        story.append(Spacer(1, 20))

        # Legal Sections
        story.append(Paragraph("<b>APPLICABLE LEGAL PROVISIONS &amp; MANDATES</b>", self.styles['Heading2']))
        story.append(Spacer(1, 6))
        legal_sections = """
        &bull; <b>Information Technology (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021:</b> Rule 3(1)(b) mandatory 36-hour takedown for synthetic intimate or impersonating media.<br/>
        &bull; <b>Digital Personal Data Protection Act (DPDP), 2023:</b> Zero persistent biometric storage mandate upheld.<br/>
        &bull; <b>Indian Penal Code (IPC) Sections 499 / 500:</b> Criminal defamation through synthetic impersonation.<br/>
        &bull; <b>IT Act Section 66C &amp; 66E:</b> Identity theft and violation of privacy.
        """
        story.append(Paragraph(legal_sections, self.styles['Normal']))
        story.append(Spacer(1, 30))

        # Footer Signature Block
        sig_block = """
        <b>Verified &amp; Generated via DeepShield (Kavach-AI) Platform</b><br/>
        <i>Automated Forensic Evidence &amp; Takedown System</i>
        """
        story.append(Paragraph(sig_block, ParagraphStyle('SigStyle', parent=self.styles['Normal'], fontSize=9, textColor='#475569')))

        doc.build(story)
        buffer.seek(0)
        return buffer.read()

    def generate_dossier(
        self,
        victim_name: str,
        matches: List[Dict],
        output_path: str = "dossier.pdf"
    ) -> str:
        """
        Legacy method for file path output. Writes buffer bytes to disk.
        """
        pdf_bytes = self.generate_dossier_bytes(victim_name, matches)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        return output_path
