"""
Sample Enterprise Data Generator
Creates the 4 realistic enterprise case study files specified in the prompt:
1. Annual_Report.pdf (4 pages, corporate report & CEO letter)
2. Sales_Data.xlsx (3 sheets, quarterly performance & regional contraction)
3. Product_Screenshot.png (High-res telemetry dashboard showing checkout funnel dropout)
4. Market_Research.pdf (3 pages, macro research on IT budget freezes & competitor price war)
"""

import os
from PIL import Image, ImageDraw, ImageFont
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.join(BASE_DIR)


def generate_sales_excel():
    """Generate multi-sheet Sales_Data.xlsx."""
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # remove default sheet

    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    q3_highlight_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    bold_font = Font(name="Calibri", size=11, bold=True)
    align_center = Alignment(horizontal="center", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # 1. Quarterly_Performance Sheet
    ws1 = wb.create_sheet(title="Quarterly_Performance")
    headers1 = [
        "Quarter", "Fiscal_Year", "Revenue_M_USD", "Gross_Profit_M",
        "OpEx_M_USD", "Net_Income_M", "Enterprise_Accounts", "Churn_Rate_Pct"
    ]
    ws1.append(headers1)

    rows1 = [
        ["Q1 2024", 2024, 14.2, 10.8, 6.2, 4.6, 1240, 2.1],
        ["Q2 2024", 2024, 15.8, 12.1, 6.5, 5.6, 1385, 2.4],
        ["Q3 2024", 2024, 11.1, 7.2, 7.4, -0.2, 1290, 6.8],  # The drop!
        ["Q4 2024", 2024, 16.5, 12.9, 6.8, 6.1, 1460, 2.2],
    ]
    for r in rows1:
        ws1.append(r)

    # 2. Regional_Sales Sheet
    ws2 = wb.create_sheet(title="Regional_Sales")
    headers2 = ["Region", "Q1_2024_M", "Q2_2024_M", "Q3_2024_M", "Q4_2024_M", "Q3_Contraction_Pct"]
    ws2.append(headers2)
    rows2 = [
        ["North America", 6.5, 7.4, 5.1, 7.9, -31.1],
        ["EMEA (Europe)", 4.1, 4.6, 3.2, 4.8, -30.4],
        ["APAC", 2.4, 2.6, 1.9, 2.7, -26.9],
        ["LATAM", 1.2, 1.2, 0.9, 1.1, -25.0],
    ]
    for r in rows2:
        ws2.append(r)

    # 3. Product_Lines Sheet
    ws3 = wb.create_sheet(title="Product_Lines")
    headers3 = ["Product_Line", "Q2_Revenue_M", "Q3_Revenue_M", "Delta_USD_M", "Primary_Root_Cause"]
    ws3.append(headers3)
    rows3 = [
        ["AuraCloud Platform", 8.6, 5.8, -2.8, "Checkout Funnel Gateway Dropout Spike"],
        ["Enterprise AI Suite", 4.2, 3.5, -0.7, "Competitor HyperScale Price Slashing"],
        ["Managed Infrastructure", 3.0, 1.8, -1.2, "Enterprise Procurement Freeze & Delayed Audits"]
    ]
    for r in rows3:
        ws3.append(r)

    # Style all sheets
    for ws in [ws1, ws2, ws3]:
        for col in ws.iter_cols(min_row=1, max_row=1):
            for cell in col:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = align_center

        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.border = thin_border
                if isinstance(cell.value, (int, float)):
                    cell.alignment = align_right
                if cell.value == "Q3 2024" or cell.value == -0.2 or cell.value == 6.8:
                    cell.fill = q3_highlight_fill
                    cell.font = bold_font

        # Auto fit column widths
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

    file_path = os.path.join(SAMPLE_DIR, "Sales_Data.xlsx")
    wb.save(file_path)
    print(f"Generated: {file_path}")


def generate_annual_report_pdf():
    """Generate 4-page Annual_Report.pdf using reportlab."""
    file_path = os.path.join(SAMPLE_DIR, "Annual_Report.pdf")
    doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=14,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=10
    )
    quote_style = ParagraphStyle(
        'Callout',
        parent=styles['Italic'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#991B1B'),
        spaceBefore=8,
        spaceAfter=10
    )

    story = []

    # PAGE 1: Corporate Overview
    story.append(Paragraph("AuraCorp Enterprise Technologies Inc.", title_style))
    story.append(Paragraph("<b>2024 Annual Corporate & Financial Report</b>", h2_style))
    story.append(Paragraph("<i>Fiscal Year Ended December 31, 2024 | SEC Form 10-K Summary</i>", body_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("Executive Summary & Corporate Mission", h2_style))
    story.append(Paragraph(
        "AuraCorp Enterprise Technologies is a premier cloud infrastructure and business AI workflow provider "
        "serving over 1,400 global enterprises across North America, EMEA, APAC, and Latin America. In fiscal 2024, "
        "consolidated annual revenue reached $57.6M, representing an 8.2% annual growth over 2023. While the firm "
        "achieved record performance in Q1, Q2, and Q4, significant operational volatility was experienced during the "
        "third quarter (Q3 2024), resulting in a temporary revenue trough of $11.1M.",
        body_style
    ))
    story.append(Paragraph(
        "This report provides full operational transparency into the operational catalysts, product bottlenecks, "
        "and market shifts that precipitated the Q3 contraction, as well as the corrective remediation programs "
        "that enabled the decisive Q4 resurgence to $16.5M.",
        body_style
    ))

    overview_data = [
        ["Key Metric", "FY 2023", "FY 2024", "YoY Change"],
        ["Total Annual Revenue", "$53.2M", "$57.6M", "+8.2%"],
        ["Gross Margin", "74.1%", "74.6%", "+50 bps"],
        ["Q3 Revenue Contraction", "$12.8M", "$11.1M", "-13.3% YoY"],
        ["Active Enterprise Logos", "1,210", "1,460", "+20.6%"],
        ["Cash Reserves (Dec 31)", "$18.4M", "$22.1M", "+$3.7M"]
    ]
    t1 = Table(overview_data, colWidths=[180, 100, 100, 120])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    story.append(t1)

    story.append(PageBreak())

    # PAGE 2: Letter from the CEO (Discloses Q3 issues)
    story.append(Paragraph("Letter to Shareholders from the Chief Executive Officer", title_style))
    story.append(Paragraph("<b>Author: Elena Vance, Chief Executive Officer & Co-Founder</b>", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "To Our Shareholders, Customers, and Global Partners:\n\n"
        "2024 was a defining year of technical evolution for AuraCorp. However, transparent leadership requires "
        "addressing our missteps with unsparing candor. The third quarter of 2024 was our most challenging quarter "
        "since our initial public offering.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Q3 Revenue Anomaly: Root Causes:</b><br/>"
        "Our consolidated top-line revenue dropped from $15.8M in Q2 to $11.1M in Q3—a sequential contraction of "
        "-$4.7M (-29.7%). Two internal operational factors collided during August and September:",
        body_style
    ))
    story.append(Paragraph(
        "1. <b>The Multi-Currency Payment Gateway Migration Bug:</b> In early August, our engineering team migrated "
        "AuraCloud's automated billing architecture to a next-generation distributed payment gateway. An unforeseen "
        "token serialization flaw caused automated corporate card authorizations to time out for 214 mid-market "
        "and enterprise clients, elevating checkout funnel dropouts to an unprecedented 34.2%. Over $1.9M in contract "
        "renewals were blocked before emergency engineering hotfixes were deployed in late September.",
        body_style
    ))
    story.append(Paragraph(
        "2. <b>EMEA Compliance & Contract Delays:</b> New European digital operational resilience mandates (DORA) "
        "prompted 18 enterprise banking clients to temporarily freeze software onboarding pending independent vendor "
        "compliance reviews. This pushed approximately $1.4M in booked annual contract value from Q3 into Q4.",
        body_style
    ))
    story.append(Paragraph(
        "\"We took immediate responsibility. By late September, the checkout pipeline was stabilized, and our customer success "
        "teams re-engaged every impacted account, successfully recovering 94% of deferred contracts in Q4.\"",
        quote_style
    ))

    story.append(PageBreak())

    # PAGE 3: Management Discussion & Financial Review
    story.append(Paragraph("Management Discussion & Financial Performance Review", title_style))
    story.append(Paragraph("<b>Detailed Analysis of Operating Results & Expenses</b>", h2_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "<b>Quarterly Operating Margin Contraction in Q3:</b><br/>"
        "Operating expenses rose in Q3 to $7.4M (compared to $6.5M in Q2) due to dual expenditures: emergency external "
        "security audit consultations ($650,000) and customer goodwill credits ($480,000) issued to enterprise clients "
        "affected by the payment gateway downtime. Consequently, net income compressed to a -$200,000 loss during Q3.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Supply Chain Hardware Restructuring:</b><br/>"
        "In addition to software billing glitches, AuraCorp recorded a one-time non-cash charge of $520,000 in Q3 related "
        "to decommissioning legacy dedicated hardware hosting nodes in our Frankfurt colocation facility as part of our "
        "transition to 100% hyperscale cloud native infrastructure.",
        body_style
    ))

    story.append(Paragraph("Q3 vs Q4 Financial Turnaround Comparison", h2_style))
    turnaround_data = [
        ["Line Item", "Q2 2024", "Q3 2024 (Trough)", "Q4 2024 (Recovery)"],
        ["Total Revenue", "$15.8M", "$11.1M (-29.7%)", "$16.5M (+48.6%)"],
        ["Gross Profit Margin", "76.6%", "64.9% (-11.7 pts)", "78.2% (+13.3 pts)"],
        ["Operating Expenses", "$6.5M", "$7.4M (Emergency Costs)", "$6.8M (Normalized)"],
        ["Net Income", "+$5.6M", "-$0.2M (Loss)", "+$6.1M (Record)"],
        ["Gross Churn Rate", "2.4%", "6.8% (Spike)", "2.2% (Normalized)"]
    ]
    t2 = Table(turnaround_data, colWidths=[150, 110, 130, 110])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (2, 1), (2, -1), colors.HexColor('#FEE2E2')),  # Highlight Q3 column
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    story.append(t2)

    story.append(PageBreak())

    # PAGE 4: Governance & Future Outlook
    story.append(Paragraph("Strategic Roadmap & 2025 Guidance", title_style))
    story.append(Paragraph("<b>Remediation Roadmap and Enterprise Safeguards</b>", h2_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "To ensure operational anomalies of this nature never recur, the Board of Directors approved three "
        "structural governance safeguards:",
        body_style
    ))
    story.append(Paragraph(
        "1. <b>Mandatory Zero-Downtime Billing Deployments:</b> All critical transactional pathways must now undergo "
        "staged canary rollouts with automated rollbacks if conversion errors exceed 0.5% over a 15-minute window.",
        body_style
    ))
    story.append(Paragraph(
        "2. <b>Enterprise SLA Guarantee Reserve:</b> A dedicated $2.0M liquidity reserve has been designated to backstop "
        "enterprise customer SLAs and ensure continuous operational continuity.",
        body_style
    ))
    story.append(Paragraph(
        "3. <b>2025 Fiscal Projections:</b> Management reiterates full-year 2025 revenue guidance of $72M - $76M, "
        "supported by the enterprise release of AuraGen Studio and expansion into APAC financial markets.",
        body_style
    ))
    story.append(Paragraph(
        "Certified by the Board of Directors, AuraCorp Enterprise Technologies, March 15, 2025.",
        body_style
    ))

    doc.build(story)
    print(f"Generated: {file_path}")


def generate_market_research_pdf():
    """Generate 3-page Market_Research.pdf using reportlab."""
    file_path = os.path.join(SAMPLE_DIR, "Market_Research.pdf")
    doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0369A1'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=10
    )

    story = []

    # PAGE 1: Macro Environment & IT Spend
    story.append(Paragraph("Global Enterprise Cloud & SaaS Market Intelligence Report", title_style))
    story.append(Paragraph("<b>Q3 2024 Market Shifts, Spending Freezes, and Sector Contractions</b>", h2_style))
    story.append(Paragraph("<i>Prepared by AlphaPoint Research Partners | Industry Intelligence Series</i>", body_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("Macroeconomic Pressures & IT Procurement Freezes in Q3", h2_style))
    story.append(Paragraph(
        "The third quarter of 2024 presented severe headwinds across enterprise technology providers. "
        "Central bank interest rate signals, persistent inflation in vendor overhead, and tighter CFO scrutiny "
        "prompted 42% of Fortune 1000 CTOs to enact temporary spending pauses or delayed sign-offs on all SaaS "
        "and cloud contract expansions above $100,000.",
        body_style
    ))
    story.append(Paragraph(
        "Key macroeconomic metrics documented during Q3 2024 include:\n"
        "- **Sales Cycle Expansion:** Average B2B SaaS contract closure duration stretched from 45 days in Q1/Q2 "
        "to 78 days in Q3 2024.\n"
        "- **Tier-1 Budget Reallocations:** Approximately $4.2B in planned enterprise digital transformation budgets "
        "were shifted into compliance and cost-containment audits.\n"
        "- **Departmental Software Consolidation:** 61% of enterprise buyers initiated vendor consolidation exercises, "
        "delaying multi-vendor renewals until late Q4.",
        body_style
    ))

    story.append(PageBreak())

    # PAGE 2: Competitor Price Wars
    story.append(Paragraph("Competitive Landscape: The HyperScale Price War", title_style))
    story.append(Paragraph("<b>Aggressive Discounting by Major Market Incumbents in Q3</b>", h2_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "In mid-July 2024, dominant market incumbent *HyperScale Cloud Solutions* initiated an unprecedented pricing "
        "campaign, slashing baseline enterprise subscription tiers by **18% to 22%** for all competitive displacement "
        "agreements. HyperScale specifically targeted accounts using mid-sized providers like AuraCorp, offering "
        "free data migration credits and waived implementation fees.",
        body_style
    ))
    story.append(Paragraph(
        "Impact on Mid-Enterprise Market Competitors:\n"
        "- **Price Deflation Pressure:** Mid-tier cloud vendors faced margin compression or temporary churn as price-sensitive "
        "enterprise procurement teams leveraged HyperScale's offers to demand steep contract renegotiations.\n"
        "- **AuraCorp Impact:** Estimated $900,000 in competitive renewal displacement during August and September 2024, "
        "contributing directly to the Q3 revenue contraction.\n"
        "- **Market Share Shift:** HyperScale captured an incremental 2.4% market share during the summer before competitor "
        "counter-bundling programs neutralized the pricing advantage in Q4.",
        body_style
    ))

    story.append(PageBreak())

    # PAGE 3: Regulatory Shifts & Conclusions
    story.append(Paragraph("Regulatory Frameworks: European DORA & AI Compliance", title_style))
    story.append(Paragraph("<b>Compliance Audits Delaying Cross-Border Software Deployments</b>", h2_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "The enforcement preparation for the European Digital Operational Resilience Act (DORA) and the European Union "
        "AI Act generated significant friction for enterprise cloud vendors operating across the EU during Q3 2024.",
        body_style
    ))
    story.append(Paragraph(
        "Financial institutions, healthcare conglomerates, and critical infrastructure providers were required to "
        "perform comprehensive operational resilience audits on third-party cloud sub-processors. Across the European "
        "market, more than 350 enterprise procurement approvals were placed on formal administrative hold while vendors "
        "completed updated SOC2 Type II, ISO 27001:2022, and DORA attestation packages.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Analyst Consensus Conclusion:</b><br/>"
        "The Q3 2024 revenue contraction observed across innovative enterprise software firms was predominantly cyclical "
        "and transient, driven by the synchrony of IT procurement delays, temporary incumbent price wars, and European "
        "compliance freezes. Providers with robust fundamental unit economics experienced sharp rebounds in Q4 as deferred "
        "pipeline budgets were executed before fiscal year-end.",
        body_style
    ))

    doc.build(story)
    print(f"Generated: {file_path}")


def generate_product_screenshot_image():
    """Generate high-resolution Product_Screenshot.png with telemetry metrics and drop-off alert."""
    width, height = 1200, 750
    img = Image.new("RGB", (width, height), color=(15, 23, 42))  # slate-900
    draw = ImageDraw.Draw(img)

    # Header Bar
    draw.rectangle([(0, 0), (width, 70)], fill=(30, 41, 59))  # slate-800
    draw.line([(0, 70), (width, 70)], fill=(51, 65, 85), width=2)

    # Title & Brand
    draw.text((30, 22), "AuraCloud Telemetry & Operations Console — v4.1.8", fill=(56, 189, 248))
    draw.text((width - 320, 25), "Environment: PRODUCTION (us-east-1 / eu-west-1)", fill=(148, 163, 184))

    # Alert Banner for Q3 Checkout Dropout
    draw.rectangle([(30, 95), (width - 30, 165)], fill=(69, 10, 10), outline=(239, 68, 68), width=2)
    draw.text((50, 108), "CRITICAL ALERT: Payment Gateway Serialization Failure & Funnel Dropout Spike", fill=(254, 202, 202))
    draw.text(
        (50, 134),
        "Automated renewal timeouts detected during Multi-Currency Gateway migration | Impact: 214 Accounts ($1.9M ARR at risk)",
        fill=(252, 165, 165)
    )

    # Metric Cards
    cards = [
        ("Checkout Funnel Conversion", "54.2%", "Normal: 88.4% (▼ 34.2% Dropout)", (239, 68, 68)),
        ("Payment Gateway Timeouts", "4,892", "Status: Spike during Q3 (Aug 12 - Sep 18)", (245, 158, 11)),
        ("Impacted Enterprise ARR", "$1.92M", "214 Enterprise Renewals Blocked", (244, 63, 94)),
        ("Platform Health Index", "76.4%", "Down from 99.8% 90-day SLA", (56, 189, 248))
    ]

    card_w = 260
    card_gap = 25
    start_x = 35

    for idx, (title, val, subtitle, val_color) in enumerate(cards):
        cx = start_x + idx * (card_w + card_gap)
        draw.rectangle([(cx, 190), (cx + card_w, 305)], fill=(30, 41, 59), outline=(51, 65, 85), width=1)
        draw.text((cx + 15, 205), title, fill=(148, 163, 184))
        draw.text((cx + 15, 235), val, fill=val_color)
        draw.text((cx + 15, 275), subtitle, fill=(203, 213, 225))

    # Graph Section
    draw.rectangle([(35, 335), (width - 35, 715)], fill=(30, 41, 59), outline=(51, 65, 85), width=1)
    draw.text((55, 355), "Daily Checkout Funnel Conversion Rate (July 1 - Oct 31, 2024)", fill=(248, 250, 252))
    draw.text((width - 450, 355), "Red Zone: Gateway Migration Dropout Incident (August 2024)", fill=(239, 68, 68))

    # Draw Chart Axis
    chart_x1, chart_y1 = 80, 410
    chart_x2, chart_y2 = width - 60, 660
    draw.line([(chart_x1, chart_y2), (chart_x2, chart_y2)], fill=(100, 116, 139), width=2)
    draw.line([(chart_x1, chart_y1), (chart_x1, chart_y2)], fill=(100, 116, 139), width=2)

    # Grid lines & Labels
    for y_val, label in [(chart_y1, "100%"), (chart_y1 + 80, "75%"), (chart_y1 + 160, "50%"), (chart_y2, "25%")]:
        draw.line([(chart_x1, y_val), (chart_x2, y_val)], fill=(51, 65, 85), width=1)
        draw.text((chart_x1 - 38, y_val - 7), label, fill=(148, 163, 184))

    # X axis months
    months = [("July (Baseline)", 150), ("August (Migration Bug)", 420), ("September (Hotfix)", 720), ("October (Recovery)", 980)]
    for m_label, mx in months:
        draw.text((mx, chart_y2 + 10), m_label, fill=(148, 163, 184))

    # Incident Highlight Box in Chart
    draw.rectangle([(380, chart_y1 + 10), (680, chart_y2)], fill=(69, 10, 10, 100), outline=(239, 68, 68), width=1)
    draw.text((410, chart_y1 + 30), "Dropout Spike (34.2%)", fill=(254, 202, 202))

    # Draw Conversion Rate Trend Line
    points = [
        (90, 435), (150, 438), (220, 436), (300, 440), (370, 445),  # Normal July (~88%)
        (400, 520), (450, 610), (510, 630), (570, 615), (630, 580),  # August drop to ~54%
        (690, 490), (750, 450), (840, 435), (940, 432), (1050, 430), (1110, 428) # Recovery
    ]

    for i in range(len(points) - 1):
        color = (239, 68, 68) if 380 <= points[i][0] <= 660 else (56, 189, 248)
        draw.line([points[i], points[i + 1]], fill=color, width=3)
        draw.ellipse([(points[i][0] - 3, points[i][1] - 3), (points[i][0] + 3, points[i][1] + 3)], fill=color)

    file_path = os.path.join(SAMPLE_DIR, "Product_Screenshot.png")
    img.save(file_path)
    print(f"Generated: {file_path}")


def main():
    print("Generating sample enterprise files...")
    generate_sales_excel()
    generate_annual_report_pdf()
    generate_market_research_pdf()
    generate_product_screenshot_image()
    print("All sample enterprise files created successfully!")


if __name__ == "__main__":
    main()
