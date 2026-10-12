import io
import base64
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from PIL import Image as PILImage


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print 'Page X of Y' page numbers
    along with running header and footer.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        # Top running header (pages > 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#0f172a"))
            self.drawString(40, 755, "LOOV VISION AI")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(125, 755, "— INDUSTRIAL LUBRICANT ANALYSIS REPORT")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.75)
            self.line(40, 748, 572, 748)

        # Bottom running footer
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(40, 30, "CONFIDENTIAL & PROPRIETARY — LOOV VISION AI INDUSTRIAL MONITORING")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 30, page_text)
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.75)
        self.line(40, 42, 572, 42)
        self.restoreState()


def prepare_image_flowable(image_data: Optional[str], max_width: float = 160, max_height: float = 130) -> Optional[RLImage]:
    """Decodes base64/data-URL image and returns a scaled ReportLab Image flowable."""
    if not image_data:
        return None

    try:
        if "," in image_data:
            _, encoded = image_data.split(",", 1)
        else:
            encoded = image_data

        raw_bytes = base64.b64decode(encoded)
        if len(raw_bytes) == 0:
            return None

        pil_img = PILImage.open(io.BytesIO(raw_bytes))
        orig_w, orig_h = pil_img.size

        if orig_w == 0 or orig_h == 0:
            return None

        # Compute scaling preserving aspect ratio
        ratio = min(max_width / orig_w, max_height / orig_h)
        target_w = orig_w * ratio
        target_h = orig_h * ratio

        # Convert to RGB if necessary for safe PDF embedding
        if pil_img.mode in ("RGBA", "P"):
            pil_img = pil_img.convert("RGB")

        out_buffer = io.BytesIO()
        pil_img.save(out_buffer, format="JPEG", quality=90)
        out_buffer.seek(0)

        rl_img = RLImage(out_buffer, width=target_w, height=target_h)
        return rl_img
    except Exception as e:
        print(f"[PDF GENERATOR] Warning: Failed to process report image: {e}")
        return None


def generate_report_pdf(report: Dict[str, Any]) -> bytes:
    """
    Renders an AnalysisReportData dict into a publication-grade industrial PDF report.
    Returns bytes of the compiled PDF.
    """
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    # Define custom typography and color styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a")
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0284c7")
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#334155")
    )

    bold_body = ParagraphStyle(
        "BoldBody",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#0f172a")
    )

    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1e293b")
    )

    table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#ffffff")
    )

    disclaimer_style = ParagraphStyle(
        "DisclaimerText",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#64748b")
    )

    story = []

    # 1. REPORT HEADER & BANNER
    meta = report.get("metadata", {})
    report_id = meta.get("report_id", "LOOV-RPT-N/A")
    timestamp = meta.get("timestamp_formatted", meta.get("timestamp_iso", "N/A"))

    header_table_data = [
        [
            Paragraph("<b>LOOV VISION AI</b>", title_style),
            Paragraph(f"<b>REPORT ID:</b> {report_id}<br/><b>DATE:</b> {timestamp}", ParagraphStyle("MetaRight", parent=body_style, alignment=2))
        ],
        [
            Paragraph("INDUSTRIAL MULTI-MODEL LUBRICANT CONDITION MONITORING REPORT", subtitle_style),
            Paragraph("<b>STANDARD:</b> ISO 4406 / Visual Screening", ParagraphStyle("MetaRight2", parent=body_style, alignment=2, textColor=colors.HexColor("#64748b")))
        ]
    ]

    header_table = Table(header_table_data, colWidths=[332, 200])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0f172a"), spaceBefore=2, spaceAfter=10))

    # 2. EXECUTIVE SUMMARY & CONDITION ASSESSMENT
    exec_data = report.get("executive_summary", {})
    final_class = str(exec_data.get("final_class", "c3")).lower()
    condition_label = exec_data.get("condition_label", "Analyzed")
    confidence_pct = exec_data.get("confidence_pct", "0.0%")
    headline = exec_data.get("summary_headline", "Lubricant Condition Assessment")
    summary_text = exec_data.get("summary_text", "")
    urgency = exec_data.get("operational_urgency", "Notice")

    # Condition Color Palette
    if final_class == "c1":
        badge_bg = colors.HexColor("#ecfdf5")
        badge_border = colors.HexColor("#059669")
        badge_text_color = colors.HexColor("#065f46")
        grade_str = "C1 — OPTIMAL / FRESH OIL"
    elif final_class == "c2":
        badge_bg = colors.HexColor("#fffbeb")
        badge_border = colors.HexColor("#d97706")
        badge_text_color = colors.HexColor("#92400e")
        grade_str = "C2 — TRANSITIONAL DEGRADATION"
    else:  # c3
        badge_bg = colors.HexColor("#fef2f2")
        badge_border = colors.HexColor("#dc2626")
        badge_text_color = colors.HexColor("#991b1b")
        grade_str = "C3 — ADVANCED DEGRADATION"

    # Executive Summary Card with Image Layout
    image_base64 = report.get("image_base64")
    image_flowable = prepare_image_flowable(image_base64, max_width=150, max_height=125)

    badge_cell = [
        Paragraph(f"<b>FINAL CONDITION ASSESSMENT: {grade_str}</b>", ParagraphStyle("BadgeTitle", parent=bold_body, fontSize=10, textColor=badge_text_color)),
        Spacer(1, 3),
        Paragraph(f"<b>System Confidence:</b> {confidence_pct} &nbsp;|&nbsp; <b>Operational Urgency:</b> {urgency}", ParagraphStyle("BadgeSub", parent=body_style, fontSize=8, textColor=badge_text_color)),
        Spacer(1, 4),
        Paragraph(f"<b>{headline}</b>", bold_body),
        Spacer(1, 2),
        Paragraph(summary_text, body_style)
    ]

    if image_flowable:
        img_box = [
            Paragraph("<b>Analysed Sample Image:</b>", ParagraphStyle("ImgTitle", parent=body_style, fontSize=7.5, textColor=colors.HexColor("#475569"))),
            Spacer(1, 2),
            image_flowable
        ]
        exec_table_data = [[badge_cell, img_box]]
        exec_table = Table(exec_table_data, colWidths=[362, 170])
        exec_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (0, 0), badge_bg),
            ("BOX", (0, 0), (0, 0), 1, badge_border),
            ("PADDING", (0, 0), (0, 0), 8),
            ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ("VALIGN", (1, 0), (1, 0), "MIDDLE"),
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#f8fafc")),
            ("BOX", (1, 0), (1, 0), 0.75, colors.HexColor("#cbd5e1")),
            ("PADDING", (1, 0), (1, 0), 6),
        ]))
    else:
        exec_table = Table([[badge_cell]], colWidths=[532])
        exec_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (0, 0), badge_bg),
            ("BOX", (0, 0), (0, 0), 1, badge_border),
            ("PADDING", (0, 0), (0, 0), 8),
        ]))

    story.append(exec_table)
    story.append(Spacer(1, 8))

    # 3. INDIVIDUAL MACHINE LEARNING MODEL ANALYSIS
    story.append(Paragraph("1. MULTI-MODEL INFERENCE & EVIDENCE BREAKDOWN", section_heading))

    models_data = report.get("models", {})
    eff = models_data.get("efficientnet", {})
    col = models_data.get("color", {})
    tex = models_data.get("texture", {})

    def get_prob_str(m_dict, key):
        probs = m_dict.get("probabilities", {})
        val = probs.get(key, 0.0)
        return f"{val * 100:.1f}%"

    ml_table_rows = [
        [
            Paragraph("AI Model Component", table_header),
            Paragraph("Weight", table_header),
            Paragraph("Predicted Class", table_header),
            Paragraph("C1 (Fresh)", table_header),
            Paragraph("C2 (Semi)", table_header),
            Paragraph("C3 (Degraded)", table_header)
        ],
        [
            Paragraph(f"<b>{eff.get('model_name', 'EfficientNet-B3')}</b>", table_cell),
            Paragraph(f"{int(eff.get('weight', 0.55)*100)}%", table_cell),
            Paragraph(f"<b>{eff.get('predicted_class', '-').upper()}</b> ({eff.get('condition_label', '-')})", table_cell),
            Paragraph(get_prob_str(eff, "c1"), table_cell),
            Paragraph(get_prob_str(eff, "c2"), table_cell),
            Paragraph(get_prob_str(eff, "c3"), table_cell),
        ],
        [
            Paragraph(f"<b>{col.get('model_name', 'Color Analysis Pipeline')}</b>", table_cell),
            Paragraph(f"{int(col.get('weight', 0.15)*100)}%", table_cell),
            Paragraph(f"<b>{col.get('predicted_class', '-').upper()}</b> ({col.get('condition_label', '-')})", table_cell),
            Paragraph(get_prob_str(col, "c1"), table_cell),
            Paragraph(get_prob_str(col, "c2"), table_cell),
            Paragraph(get_prob_str(col, "c3"), table_cell),
        ],
        [
            Paragraph(f"<b>{tex.get('model_name', 'Texture Random Forest')}</b>", table_cell),
            Paragraph(f"{int(tex.get('weight', 0.30)*100)}%", table_cell),
            Paragraph(f"<b>{tex.get('predicted_class', '-').upper()}</b> ({tex.get('condition_label', '-')})", table_cell),
            Paragraph(get_prob_str(tex, "c1"), table_cell),
            Paragraph(get_prob_str(tex, "c2"), table_cell),
            Paragraph(get_prob_str(tex, "c3"), table_cell),
        ]
    ]

    ml_table = Table(ml_table_rows, colWidths=[182, 50, 130, 56, 56, 58])
    ml_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
    ]))
    story.append(ml_table)
    story.append(Spacer(1, 7))

    # 4. EXTRACTED PHYSICAL & STATISTICAL FEATURE METRICS
    col_feat = col.get("features") or {}
    tex_feat = tex.get("features") or {}

    feat_text_col = []
    if col_feat:
        feat_text_col = [
            f"<b>L* Median:</b> {col_feat.get('L_median', 'N/A')}",
            f"<b>V Median:</b> {col_feat.get('V_median', 'N/A')}",
            f"<b>Norm Green:</b> {col_feat.get('NG_median', 'N/A')}",
            f"<b>LAB B*:</b> {col_feat.get('LAB_B_median', 'N/A')}",
            f"<b>R Median:</b> {col_feat.get('R_median', 'N/A')}",
            f"<b>G Median:</b> {col_feat.get('G_median', 'N/A')}",
        ]

    feat_text_tex = []
    if tex_feat:
        feat_text_tex = [
            f"<b>GLCM Contrast:</b> {tex_feat.get('contrast', 'N/A')}",
            f"<b>Homogeneity:</b> {tex_feat.get('homogeneity', 'N/A')}",
            f"<b>Energy:</b> {tex_feat.get('energy', 'N/A')}",
            f"<b>Correlation:</b> {tex_feat.get('correlation', 'N/A')}",
            f"<b>Dissimilarity:</b> {tex_feat.get('dissimilarity', 'N/A')}",
            f"<b>Edge Density:</b> {tex_feat.get('edge_density', 'N/A')}",
        ]

    feat_row_1 = "<br/>".join(feat_text_col[:3]) if feat_text_col else "No colorimetric features extracted"
    feat_row_2 = "<br/>".join(feat_text_col[3:]) if len(feat_text_col) > 3 else ""
    feat_tex_1 = "<br/>".join(feat_text_tex[:3]) if feat_text_tex else "No texture spatial features extracted"
    feat_tex_2 = "<br/>".join(feat_text_tex[3:]) if len(feat_text_tex) > 3 else ""

    feature_table_data = [
        [
            Paragraph("<b>Colorimetric Optical Metrics (Median Profiles):</b><br/>" + feat_row_1 + "<br/>" + feat_row_2, table_cell),
            Paragraph("<b>Surface Texture Spatial Metrics (GLCM Profiles):</b><br/>" + feat_tex_1 + "<br/>" + feat_tex_2, table_cell)
        ]
    ]
    feature_table = Table(feature_table_data, colWidths=[266, 266])
    feature_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(feature_table)
    story.append(Spacer(1, 7))

    # 5. MODEL AGREEMENT & CONSENSUS
    agreement = report.get("agreement", {})
    consensus_status = agreement.get("consensus_status", "Consensus Evaluated")
    agree_analysis = agreement.get("agreement_analysis", "")
    supporting_count = agreement.get("models_supporting", 0)
    total_m = agreement.get("total_models", 3)

    agree_card_data = [[
        Paragraph(f"<b>CONSENSUS STATUS:</b> {consensus_status} ({supporting_count}/{total_m} Models)", bold_body),
    ], [
        Paragraph(agree_analysis, body_style)
    ]]
    agree_table = Table(agree_card_data, colWidths=[532])
    agree_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
    ]))
    story.append(agree_table)
    story.append(Spacer(1, 8))

    # 6. LLM EVIDENCE-BASED REASONING & TECHNICAL NARRATIVE
    reasoning_block = report.get("reasoning", {})
    narrative = reasoning_block.get("decision_narrative", "")
    supporting = reasoning_block.get("supporting_factors", [])
    uncertainties = reasoning_block.get("uncertainties_or_caveats", [])

    story.append(Paragraph("2. AI DECISION REASONING & EVIDENCE SYNTHESIS", section_heading))
    story.append(Paragraph(narrative, body_style))
    story.append(Spacer(1, 4))

    bullets_data = []
    if supporting:
        bullets_data.append([Paragraph("<b>Key Supporting Visual Evidence:</b>", bold_body)])
        for sf in supporting:
            bullets_data.append([Paragraph(f"• {sf}", body_style)])
    if uncertainties:
        bullets_data.append([Spacer(1, 2)])
        bullets_data.append([Paragraph("<b>Technical Uncertainties & Industrial Constraints:</b>", bold_body)])
        for un in uncertainties:
            bullets_data.append([Paragraph(f"• {un}", body_style)])

    if bullets_data:
        bullets_table = Table(bullets_data, colWidths=[532])
        bullets_table.setStyle(TableStyle([
            ("PADDING", (0, 0), (-1, -1), 1),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(bullets_table)

    story.append(Spacer(1, 8))

    # 7. OPERATIONAL RECOMMENDATIONS
    recs = report.get("recommendations", {})
    primary_act = recs.get("primary_action", "")
    guidance_list = recs.get("operational_guidance", [])
    lab_adv = recs.get("laboratory_advisory", "")

    rec_elements = [
        Paragraph("3. LUBRICANT MAINTENANCE & ACTION RECOMMENDATIONS", section_heading),
        Paragraph(f"<b>Primary Operational Directive:</b> {primary_act}", bold_body),
        Spacer(1, 3)
    ]
    for g in guidance_list:
        rec_elements.append(Paragraph(f"✔ &nbsp; {g}", body_style))
        rec_elements.append(Spacer(1, 2))

    if lab_adv:
        rec_elements.append(Spacer(1, 2))
        rec_elements.append(Paragraph(f"<b>Laboratory Advisory:</b> {lab_adv}", body_style))

    story.append(KeepTogether(rec_elements))
    story.append(Spacer(1, 10))

    # 8. LIMITATIONS & INDUSTRIAL DISCLAIMER
    disclaimer_text = report.get("disclaimer", "")
    disclaimer_card = Table([[
        Paragraph(disclaimer_text, disclaimer_style)
    ]], colWidths=[532])
    disclaimer_card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(KeepTogether([disclaimer_card]))

    # Build PDF with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_bytes = pdf_buffer.getvalue()
    pdf_buffer.close()
    return pdf_bytes
