import io
from datetime import datetime

try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors as rl_colors
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ModuleNotFoundError:
    REPORTLAB_AVAILABLE = False

def reportlab_image_preserve_aspect(image_bytes, max_width, max_height):
    """Opret et ReportLab-billede uden at forvride bredde/højde-forhold."""
    img_buffer = io.BytesIO(image_bytes)
    image = RLImage(img_buffer)
    width = getattr(image, "imageWidth", None)
    height = getattr(image, "imageHeight", None)
    if width and height:
        scale = min(max_width / width, max_height / height)
        image.drawWidth = width * scale
        image.drawHeight = height * scale
    else:
        image.drawWidth = max_width
        image.drawHeight = max_height
    return image

def make_pdf(app_title, scenario_name, ophavstekst, show_display, map_png, changed):
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("ReportLab er ikke installeret.")

    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(app_title, styles["Title"]))
    story.append(Paragraph(f"Scenarie: {scenario_name}", styles["Heading2"]))
    story.append(Paragraph(datetime.now().strftime("Genereret %d-%m-%Y kl. %H:%M"), styles["Normal"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(ophavstekst, styles["Normal"]))
    story.append(Spacer(1, 12))

    table_data = [list(show_display.columns)] + show_display.astype(str).values.tolist()
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor("#444444")),
        ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.25, rl_colors.black),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
    ]))
    story.append(table)
    story.append(Spacer(1, 14))

    if changed:
        story.append(Paragraph("Ændringer fra nuværende forhold", styles["Heading3"]))
        story.append(Paragraph(", ".join(changed), styles["Normal"]))
        story.append(Spacer(1, 10))

    story.append(reportlab_image_preserve_aspect(map_png, max_width=500, max_height=360))
    story.append(Spacer(1, 8))
    story.append(Paragraph(ophavstekst, styles["Italic"]))

    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
