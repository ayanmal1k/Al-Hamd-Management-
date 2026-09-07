import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from services.transaction_service import get_filtered_history

from paths import get_documents_dir, get_asset_path

DOCUMENTS_DIR = get_documents_dir()

def generate_history_pdf(transactions: list, start_date: str = None, end_date: str = None) -> str:
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = os.path.join(DOCUMENTS_DIR, f"History_Report_{timestamp}.pdf")
    
    doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
    elements = []
    
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', 
        parent=styles['Heading1'], 
        textColor=colors.HexColor('#cc0000'), 
        alignment=1 # Center
    )
    subtitle_style = ParagraphStyle('SubtitleStyle', parent=styles['Normal'], alignment=1)
    
    # Add Logo
    logo_path = get_asset_path('logo.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1*inch, height=1*inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 0.1 * inch))
        
    elements.append(Paragraph("ALHAMD TRADERS", title_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Transaction History", subtitle_style))
    
    date_str = ""
    if start_date and end_date:
        date_str = f"{start_date} - {end_date}"
    elif start_date:
        date_str = f"From {start_date}"
    elif end_date:
        date_str = f"Up to {end_date}"
    else:
        date_str = "All Time"
        
    elements.append(Paragraph(date_str, subtitle_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Table Header
    data = [['Date', 'Customer', 'Booker', 'Type', 'Amount (Rs.)', 'Prev. Bal.', 'New Bal.']]
    
    total_bills = 0
    total_recoveries = 0
    
    for tx in transactions:
        amount_rs = tx['amount'] / 100.0
        new_bal = tx['updated_balance']
        
        if tx['type'] == 'Bill':
            prev_bal = new_bal - tx['amount']
            total_bills += tx['amount']
        else:
            prev_bal = new_bal + tx['amount']
            total_recoveries += tx['amount']
            
        prev_bal_rs = prev_bal / 100.0
        new_bal_rs = new_bal / 100.0
        
        data.append([
            tx['transaction_date'],
            tx.get('customer_name', ''),
            tx.get('booker_name', ''),
            tx['type'],
            f"{amount_rs:,.2f}",
            f"{prev_bal_rs:,.2f}",
            f"{new_bal_rs:,.2f}"
        ])
            
    # Table Style
    table = Table(data, colWidths=[1.1*inch, 1.8*inch, 1.2*inch, 0.8*inch, 1.1*inch, 1.1*inch, 1.1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (4, 0), (6, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.4 * inch))
    
    # Totals
    totals_style = ParagraphStyle('TotalsStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12)
    elements.append(Paragraph(f"Total Bills: Rs. {total_bills / 100.0:,.2f}", totals_style))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph(f"Total Recoveries: Rs. {total_recoveries / 100.0:,.2f}", totals_style))
    
    doc.build(elements)
    
    return filename
