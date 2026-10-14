"""PDF evidence summary generator.

The report documents candidate findings. It does not certify that a candidate
is a deepfake, establish that an offence occurred, or replace legal advice.
"""
from __future__ import annotations

import io
import logging
from datetime import datetime, timezone
from html import escape
from typing import Dict, List

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import LongTable, Paragraph, SimpleDocTemplate, Spacer, TableStyle

logger = logging.getLogger(__name__)


class PDFDossier:
    def __init__(self) -> None:
        self.styles = getSampleStyleSheet()

    def generate_dossier_bytes(self, victim_name: str, matches: List[Dict]) -> bytes:
        buffer = io.BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.55 * inch,
            leftMargin=0.55 * inch,
            topMargin=0.6 * inch,
            bottomMargin=0.6 * inch,
            title="DeepShield Candidate Evidence Report",
            author="DeepShield",
        )
        title_style = ParagraphStyle(
            "DeepShieldTitle", parent=self.styles["Title"], fontSize=17,
            leading=21, alignment=TA_CENTER, spaceAfter=8,
        )
        subtitle_style = ParagraphStyle(
            "DeepShieldSubtitle", parent=self.styles["Normal"], fontSize=8,
            leading=11, alignment=TA_CENTER, textColor=colors.HexColor("#475569"),
        )
        cell_style = ParagraphStyle(
            "EvidenceCell", parent=self.styles["BodyText"], fontSize=7,
            leading=9, wordWrap="CJK",
        )
        small_style = ParagraphStyle(
            "EvidenceSmall", parent=cell_style, fontSize=6.5, leading=8,
        )

        story = [
            Paragraph("DEEPSHIELD — CANDIDATE EVIDENCE REPORT", title_style),
            Paragraph("Automated similarity candidates for human review", subtitle_style),
            Spacer(1, 16),
            Paragraph(f"<b>Report generated (UTC):</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}", self.styles["Normal"]),
            Paragraph(f"<b>Complainant name supplied by operator:</b> {escape(victim_name)}", self.styles["Normal"]),
            Spacer(1, 12),
            Paragraph("Candidate results", self.styles["Heading2"]),
            Paragraph(
                "A similarity score is not proof that an image is synthetic, unlawful, or an impersonation. "
                "Verify each source and evidence item before using this report in a complaint.",
                small_style,
            ),
            Spacer(1, 8),
        ]

        table_data = [[
            Paragraph("<b>#</b>", cell_style),
            Paragraph("<b>Source / URL</b>", cell_style),
            Paragraph("<b>Similarity</b>", cell_style),
            Paragraph("<b>Evidence signature</b>", cell_style),
        ]]
        for index, match in enumerate(matches, 1):
            url = str(match.get("url") or "Not supplied")
            domain = str(match.get("domain") or "Unknown domain")
            score = float(match.get("similarity", 0.0))
            signature = str(match.get("hash_signature") or "Not available")
            table_data.append([
                Paragraph(str(index), cell_style),
                Paragraph(f"<b>{escape(domain)}</b><br/>{escape(url)}", small_style),
                Paragraph(f"{score * 100:.1f}%", cell_style),
                Paragraph(escape(signature), small_style),
            ])

        table = LongTable(
            table_data,
            colWidths=[0.3 * inch, 3.35 * inch, 0.75 * inch, 1.65 * inch],
            repeatRows=1,
            hAlign="LEFT",
        )
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(table)
        story += [
            Spacer(1, 18),
            Paragraph("Limitations and operator declaration", self.styles["Heading2"]),
            Paragraph(
                "This report records data returned by automated public-web image search and similarity analysis. "
                "Remote images or URLs may change or become unavailable. The operator should verify the source, "
                "capture independent evidence where lawful, and obtain appropriate advice before making legal claims. "
                "DeepShield does not guarantee removal or provider acceptance of a complaint.",
                self.styles["BodyText"],
            ),
        ]
        document.build(story)
        buffer.seek(0)
        return buffer.read()

    def generate_dossier(self, victim_name: str, matches: List[Dict], output_path: str = "dossier.pdf") -> str:
        """Legacy local-export helper; API routes use the in-memory byte method."""
        pdf_bytes = self.generate_dossier_bytes(victim_name, matches)
        with open(output_path, "wb") as output:
            output.write(pdf_bytes)
        return output_path
