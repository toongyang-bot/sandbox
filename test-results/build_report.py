"""Build the combined PDF report from iteration-1 and iteration-2 test results.
One-off script for this report; not part of the site or its test tooling."""
import json
import os
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    PageBreak, HRFlowable, KeepTogether
)
from PIL import Image as PILImage

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "ticket-form-test-report.pdf")

styles = getSampleStyleSheet()
title_style = styles["Title"]
h1 = styles["Heading1"]
h2 = styles["Heading2"]
body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10, leading=14, spaceAfter=6)
small = ParagraphStyle("small", parent=styles["Normal"], fontSize=8.5, leading=11, textColor=colors.HexColor("#475569"))
caption = ParagraphStyle("caption", parent=styles["Normal"], fontSize=9, leading=12,
                          textColor=colors.HexColor("#334155"), spaceBefore=4, spaceAfter=2)

PASS_GREEN = colors.HexColor("#1E7A34")
HEADER_BG = colors.HexColor("#1E293B")
ROW_ALT = colors.HexColor("#F8FAFC")

def load_iteration(n):
    path = os.path.join(BASE, f"iteration-{n}", "ticket-submissions.json")
    with open(path) as f:
        return json.load(f)

def summary_table(records):
    header = ["Scenario", "Result", "Ticket Ref", "Priority", "SLA"]
    data = [header]
    for r in records:
        data.append([
            r["scenario"],
            "PASS" if r["result"] == "pass" else "FAIL",
            r.get("ticketRef") or "—",
            r.get("priorityShown") or "—",
            r.get("slaShown") or "—",
        ])
    t = Table(data, colWidths=[1.9 * inch, 0.6 * inch, 1.7 * inch, 0.8 * inch, 1.2 * inch], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for i, r in enumerate(records, start=1):
        if r["result"] == "pass":
            style.append(("TEXTCOLOR", (1, i), (1, i), PASS_GREEN))
            style.append(("FONTNAME", (1, i), (1, i), "Helvetica-Bold"))
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    t.setStyle(TableStyle(style))
    return t

def scaled_image(path, max_width_in=6.3, max_height_in=3.6):
    with PILImage.open(path) as im:
        w, h = im.size
    ratio = min(max_width_in * 72 / w, max_height_in * 72 / h)
    return Image(path, width=w * ratio, height=h * ratio)

story = []

# --- Title page ---
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("UOB IT Service Desk", ParagraphStyle(
    "subtitle0", parent=body, fontSize=13, textColor=colors.HexColor("#475569"), alignment=1)))
story.append(Paragraph("Ticket Submission Form &mdash; Automated Test Report", ParagraphStyle(
    "title0", parent=title_style, alignment=1, fontSize=22, spaceAfter=6)))
story.append(Spacer(1, 6))
story.append(Paragraph(
    f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} "
    f"&middot; two back-to-back runs via the project's <b>ticket-form-tester</b> agent "
    f"(Playwright, served over a local HTTP server) against <b>index.html</b>.",
    ParagraphStyle("sub", parent=body, alignment=1, textColor=colors.HexColor("#475569"))))
story.append(Spacer(1, 0.3 * inch))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0")))
story.append(Spacer(1, 0.25 * inch))

iter1 = load_iteration(1)
iter2 = load_iteration(2)

def pass_count(records):
    return sum(1 for r in records if r["result"] == "pass"), len(records)

p1, t1 = pass_count(iter1)
p2, t2 = pass_count(iter2)

overview = Table([
    ["Iteration", "Scenarios", "Passed", "Failed"],
    ["1", str(t1), str(p1), str(t1 - p1)],
    ["2", str(t2), str(p2), str(t2 - p2)],
], colWidths=[1.6 * inch, 1.6 * inch, 1.6 * inch, 1.6 * inch])
overview.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("TEXTCOLOR", (2, 1), (2, -1), PASS_GREEN),
    ("FONTNAME", (2, 1), (2, -1), "Helvetica-Bold"),
]))
story.append(overview)
story.append(Spacer(1, 0.2 * inch))
story.append(Paragraph(
    "<b>Result: all 16 scenario-runs passed across both iterations.</b> Each iteration covered "
    "the same 8-scenario matrix: a valid submission at every priority level "
    "(Low / Medium / High / Critical, checking the ticket reference format and the SLA text "
    "shown), a blank-required-fields submission (checking inline errors, "
    "<font face=\"Courier\">aria-invalid</font>, and focus handling), a credential-warning "
    "trigger, a deliberately wrong security-check answer, and a bad Staff&nbsp;ID / bad email "
    "format submission.", body))
story.append(Paragraph(
    "<b>Consistency across runs:</b> both iterations produced identical pass/fail outcomes for "
    "every scenario. Ticket references and the random security-check numbers differed between "
    "runs as expected (each is freshly generated per submission/question). No JavaScript "
    "console errors occurred in either run beyond a single benign "
    "<font face=\"Courier\">favicon.ico</font> 404 on page load. "
    "<font color=\"#B45309\">index.html was not modified by either test run</font> "
    "(confirmed via <font face=\"Courier\">git diff</font> after each iteration).", body))
story.append(PageBreak())

# --- Per-iteration sections ---
for n, records in ((1, iter1), (2, iter2)):
    story.append(Paragraph(f"Iteration {n}", h1))
    p, t = pass_count(records)
    story.append(Paragraph(f"{p} / {t} scenarios passed.", small))
    story.append(Spacer(1, 8))
    story.append(summary_table(records))
    story.append(Spacer(1, 0.15 * inch))
    story.append(PageBreak())

    screenshots_dir = os.path.join(BASE, f"iteration-{n}", "screenshots")
    for r in records:
        img_path = os.path.join(screenshots_dir, f"{r['scenario']}.png")
        block = [Paragraph(f"{r['scenario']} &mdash; iteration {n}", h2)]
        detail_bits = [f"Result: <b><font color='#1E7A34'>PASS</font></b>" if r["result"] == "pass"
                        else "Result: <b><font color='#B3261E'>FAIL</font></b>"]
        if r.get("ticketRef"):
            detail_bits.append(f"Ticket ref: {r['ticketRef']}")
        if r.get("priorityShown"):
            detail_bits.append(f"Priority: {r['priorityShown']}")
        if r.get("slaShown"):
            detail_bits.append(f"SLA: {r['slaShown']}")
        block.append(Paragraph(" &nbsp;|&nbsp; ".join(detail_bits), caption))
        if r.get("notes"):
            block.append(Paragraph(f"<i>{r['notes']}</i>", small))
        if os.path.exists(img_path):
            block.append(Spacer(1, 6))
            block.append(scaled_image(img_path))
        story.append(KeepTogether(block))
        story.append(Spacer(1, 0.25 * inch))
    if n == 1:
        story.append(PageBreak())

doc = SimpleDocTemplate(
    OUT, pagesize=letter,
    leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    topMargin=0.75 * inch, bottomMargin=0.7 * inch,
    title="Ticket Submission Form — Automated Test Report",
    author="ticket-form-tester agent",
)
doc.build(story)
print("Wrote", OUT)
