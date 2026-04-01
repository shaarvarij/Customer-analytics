from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import duckdb
import pandas as pd
from datetime import datetime
import os

DB_PATH = "data/analytics.db"

def generate_report():
    con = duckdb.connect(DB_PATH, read_only=True)
    customers = con.execute("SELECT * FROM customer_order_summary").df()
    segments  = con.execute("SELECT * FROM customer_segments").df()
    churn     = con.execute("SELECT * FROM churn_predictions").df()
    forecast  = con.execute("SELECT * FROM revenue_forecast").df()
    con.close()

    os.makedirs("reports/output", exist_ok=True)
    date_str  = datetime.now().strftime("%Y-%m-%d")
    filename  = f"reports/output/customer_analytics_{date_str}.pdf"
    doc       = SimpleDocTemplate(filename, pagesize=letter,
                                  rightMargin=inch, leftMargin=inch,
                                  topMargin=inch, bottomMargin=inch)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                 fontSize=24, textColor=colors.HexColor('#1a1a2e'),
                                 alignment=TA_CENTER, spaceAfter=6)
    h2_style    = ParagraphStyle('H2', parent=styles['Heading2'],
                                 fontSize=14, textColor=colors.HexColor('#16213e'),
                                 spaceBefore=16, spaceAfter=6)
    body_style  = ParagraphStyle('Body', parent=styles['Normal'],
                                 fontSize=11, leading=16,
                                 textColor=colors.HexColor('#333333'))

    story = []

    # ── Cover ──────────────────────────────────────────
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Customer Analytics Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", 
                           ParagraphStyle('sub', parent=styles['Normal'],
                                          fontSize=11, alignment=TA_CENTER,
                                          textColor=colors.grey)))
    story.append(Spacer(1, 0.3*inch))
    story.append(HRFlowable(width="100%", thickness=2,
                             color=colors.HexColor('#636EFA')))
    story.append(Spacer(1, 0.3*inch))

    # ── Executive Summary ──────────────────────────────
    story.append(Paragraph("Executive Summary", h2_style))
    total_rev   = customers['total_spent'].sum()
    total_cust  = len(customers)
    high_risk   = len(churn[churn['churn_risk'] == 'High'])
    forecast_30 = forecast['predicted_revenue'].sum()
    champions   = len(segments[segments['segment'] == 'Champion'])

    summary = f"""
    This report covers <b>{total_cust:,} customers</b> generating 
    <b>${total_rev:,.0f}</b> in total revenue. 
    Customer segmentation identifies <b>{champions} Champion customers</b> 
    driving the majority of revenue. Churn analysis flags 
    <b>{high_risk} high-risk customers</b> requiring immediate retention action. 
    The 30-day revenue forecast projects <b>${forecast_30:,.0f}</b> 
    with 95% confidence intervals.
    """
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 0.2*inch))

    # ── KPI Table ──────────────────────────────────────
    story.append(Paragraph("Key Performance Indicators", h2_style))
    kpi_data = [
        ['Metric', 'Value'],
        ['Total Customers',          f"{total_cust:,}"],
        ['Total Revenue',            f"${total_rev:,.0f}"],
        ['Avg Revenue per Customer', f"${total_rev/total_cust:,.0f}"],
        ['Champion Customers',       f"{champions:,}"],
        ['High Risk (Churn)',         f"{high_risk:,}"],
        ['30-Day Forecast',          f"${forecast_30:,.0f}"],
    ]
    kpi_table = Table(kpi_data, colWidths=[3.5*inch, 2.5*inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0),  colors.HexColor('#636EFA')),
        ('TEXTCOLOR',   (0,0), (-1,0),  colors.white),
        ('FONTNAME',    (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,0),  12),
        ('FONTSIZE',    (0,1), (-1,-1), 11),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
         [colors.HexColor('#f8f9fa'), colors.white]),
        ('GRID',        (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('PADDING',     (0,0), (-1,-1), 8),
        ('ALIGN',       (1,0), (1,-1), 'RIGHT'),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.2*inch))

    # ── Segments ──────────────────────────────────────
    story.append(Paragraph("Customer Segmentation", h2_style))
    seg_counts = segments['segment'].value_counts()
    seg_data   = [['Segment', 'Customers', '% of Total']]
    for seg, count in seg_counts.items():
        seg_data.append([seg, f"{count:,}", f"{count/total_cust*100:.1f}%"])

    seg_table = Table(seg_data, colWidths=[2.5*inch, 2*inch, 2*inch])
    seg_table.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0),  colors.HexColor('#16213e')),
        ('TEXTCOLOR',   (0,0), (-1,0),  colors.white),
        ('FONTNAME',    (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 11),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
         [colors.HexColor('#f8f9fa'), colors.white]),
        ('GRID',        (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('PADDING',     (0,0), (-1,-1), 8),
        ('ALIGN',       (1,0), (-1,-1), 'CENTER'),
    ]))
    story.append(seg_table)
    story.append(Spacer(1, 0.2*inch))

    # ── Churn ─────────────────────────────────────────
    story.append(Paragraph("Churn Risk Analysis", h2_style))
    churn_summary = f"""
    Of the {total_cust:,} active customers, <b>{high_risk} are at high risk 
    of churning</b> within the next 90 days. These customers have not made a 
    purchase recently and show declining engagement patterns. Immediate 
    retention campaigns targeting these customers are recommended.
    """
    story.append(Paragraph(churn_summary, body_style))

    # ── Forecast ──────────────────────────────────────
    story.append(Paragraph("30-Day Revenue Forecast", h2_style))
    forecast_summary = f"""
    Based on historical purchase patterns and seasonal trends, revenue over 
    the next 30 days is projected at <b>${forecast_30:,.0f}</b> with an 
    average daily revenue of <b>${forecast_30/30:,.0f}</b>.
    """
    story.append(Paragraph(forecast_summary, body_style))

    doc.build(story)
    print(f"✓ Report generated → {filename}")
    return filename

if __name__ == "__main__":
    generate_report()