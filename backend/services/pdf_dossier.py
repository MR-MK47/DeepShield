"""
PDF Dossier - Cybercrime Complaint Report Generator
Uses ReportLab for PDF generation
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from datetime import datetime
from typing import List, Dict
import os


class PDFDossier:
    """
    Cybercrime dossier generator.
    Creates complaint-ready PDF documents for law enforcement submission.
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()

    def generate_dossier(
        self,
        victim_name: str,
        matches: List[Dict],
        output_path: str = "dossier.pdf"
    ) -> str:
        """
        Generate cybercrime complaint dossier PDF.
        Returns path to generated PDF.
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        story = []
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center
        )

        # Title
        story.append(Paragraph(
            "CYBERCRIME COMPLAINT DOSSIER",
            title_style
        ))
        story.append(Spacer(1, 12))

        # Case Information
        case_info = f"""
        <b>Date Generated:</b> {datetime.now().strftime("%B %d, %Y at %H:%M")}<br/>
        <b>Complainant:</b> {victim_name}<br/>
        <b>Case Type:</b> Unauthorized Synthetic Media / Deepfake Distribution<br/>
        <b>Jurisdiction:</b> Cyber Crime Division, Mumbai
        """
        story.append(Paragraph(case_info, self.styles['Normal']))
        story.append(Spacer(1, 24))

        # Evidence Summary
        story.append(Paragraph("<b>EVIDENCE SUMMARY</b>", self.styles['Heading2']))
        story.append(Spacer(1, 12))

        # Matches Table
        if matches:
            table_data = [["#", "Source URL", "Similarity", "Hash Signature"]]
            for idx, match in enumerate(matches, 1):
                table_data.append([
                    str(idx),
                    match.get("source_url", "N/A")[:40],
                    f"{match.get('similarity_score', 0):.2%}",
                    match.get("hash_signature", "N/A")[:16] + "..."
                ])

            table = Table(table_data, colWidths=[0.4*inch, 2.5*inch, 1*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), '#333333'),
                ('TEXTCOLOR', (0, 0), (-1, 0), '#FFFFFF'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, '#CCCCCC'),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("No matches found.", self.styles['Normal']))

        story.append(Spacer(1, 24))

        # Legal Sections
        story.append(Paragraph("<b>APPLICABLE LEGAL PROVISIONS</b>", self.styles['Heading2']))
        legal_sections = """
        • Indian Penal Code Sections 499/500 - Defamation<br/>
        • IT Act Section 66A - Offensive Messages<br/>
        • IT Act Section 67 - Obscene Content<br/>
        • Digital Personal Data Protection Act, 2023<br/>
        • Article 21 - Right to Privacy (Constitutional)
        """
        story.append(Paragraph(legal_sections, self.styles['Normal']))

        # Build PDF
        doc.build(story)
        return output_path
