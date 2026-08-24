"""
AI Job Hunter - PDF Application Package Exporter

Generates professional PDF documents containing candidate's tailored resume,
cover letter, recruiter message, and interview preparation guide.
"""

from __future__ import annotations

import io
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from backend.utils.logger import get_logger

logger = get_logger("utils.pdf_generator")


def generate_application_pdf(
    candidate_name: str,
    job_title: str,
    company_name: str,
    cover_letter: str = "",
    tailored_resume: str = "",
    recruiter_message: str = "",
    interview_prep: dict[str, Any] | None = None,
) -> bytes:
    """Generate a compiled PDF application dossier.

    Args:
        candidate_name: Name of the applicant.
        job_title: Target job title.
        company_name: Target company name.
        cover_letter: Cover letter body text.
        tailored_resume: Tailored resume body text.
        recruiter_message: Cold outreach message text.
        interview_prep: Dict of interview prep data.

    Returns:
        Bytes of the generated PDF document.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#4F46E5"),
        alignment=0,
    )

    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#64748B"),
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=12,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
    )

    elements = []

    # Header Banner
    elements.append(Paragraph(f"Application Package: {job_title}", title_style))
    elements.append(Paragraph(f"Target Company: <b>{company_name}</b> | Candidate: <b>{candidate_name}</b>", subtitle_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#7C3AED"), spaceBefore=5, spaceAfter=15))

    # Section 1: Cover Letter
    if cover_letter:
        elements.append(Paragraph("📄 Tailored Cover Letter", heading_style))
        for paragraph_text in cover_letter.split("\n\n"):
            if paragraph_text.strip():
                clean_p = paragraph_text.replace("\n", "<br/>")
                elements.append(Paragraph(clean_p, body_style))
                elements.append(Spacer(1, 6))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceBefore=5, spaceAfter=15))

    # Section 2: Tailored Resume
    if tailored_resume:
        elements.append(Paragraph("📋 Tailored Resume Overview", heading_style))
        for paragraph_text in tailored_resume.split("\n\n"):
            if paragraph_text.strip():
                clean_p = paragraph_text.replace("\n", "<br/>")
                elements.append(Paragraph(clean_p, body_style))
                elements.append(Spacer(1, 6))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceBefore=5, spaceAfter=15))

    # Section 3: Recruiter Outreach Message
    if recruiter_message:
        elements.append(Paragraph("💬 Recruiter Cold Outreach Strategy", heading_style))
        clean_msg = recruiter_message.replace("\n", "<br/>")
        elements.append(Paragraph(f"<i>Suggested Outreach Text:</i><br/><br/>{clean_msg}", body_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceBefore=5, spaceAfter=15))

    # Section 4: Interview Preparation Guide
    if interview_prep:
        elements.append(Paragraph("💡 Interview Preparation Guide", heading_style))
        
        tech_qs = interview_prep.get("technical_questions", [])
        if tech_qs:
            elements.append(Paragraph("<b>Key Technical & System Design Focus:</b>", body_style))
            for tq in tech_qs:
                q_text = tq.get("question", "")
                ans_text = tq.get("suggested_answer", "")
                elements.append(Paragraph(f"• <b>Q: {q_text}</b><br/>&nbsp;&nbsp;<i>Suggested Answer: {ans_text}</i>", body_style))
                elements.append(Spacer(1, 4))
            elements.append(Spacer(1, 6))

        ask_qs = interview_prep.get("questions_to_ask_interviewer", [])
        if ask_qs:
            elements.append(Paragraph("<b>Questions to Ask the Interviewer:</b>", body_style))
            for aq in ask_qs:
                elements.append(Paragraph(f"• {aq}", body_style))

    doc.build(elements)
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    logger.info("Application PDF generated", size=len(pdf_bytes))
    return pdf_bytes
