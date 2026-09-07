import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from paths import get_documents_dir, get_asset_path

DOCUMENTS_DIR = get_documents_dir()

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print 'Page X of Y' on all pages."""
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
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        # Clean subtle footer line
        self.setStrokeColor(colors.HexColor('#cbd5e1'))
        self.setLineWidth(0.75)
        self.line(36, 28, 792 - 36, 28)
        
        # Footer text
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#64748b'))
        self.drawString(36, 16, "Al Hamd Traders — Distribution & Accounts Management System")
        self.drawRightString(792 - 36, 16, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def _get_brand_header(report_title: str, period_or_subtitle: str, styles, filter_text: str = None):
    """Creates a standardized executive header table with logo and report metadata."""
    brand_title_style = ParagraphStyle(
        'BrandTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=18, leading=22,
        textColor=colors.HexColor('#0f172a')
    )
    brand_sub_style = ParagraphStyle(
        'BrandSub', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=12,
        textColor=colors.HexColor('#64748b')
    )
    rep_title_style = ParagraphStyle(
        'RepTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=13, leading=16,
        alignment=2, textColor=colors.HexColor('#1e293b')
    )
    rep_meta_style = ParagraphStyle(
        'RepMeta', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12,
        alignment=2, textColor=colors.HexColor('#475569')
    )

    logo_path = get_asset_path('logo.png')
    has_logo = os.path.exists(logo_path)

    if has_logo:
        logo_img = Image(logo_path, width=48, height=48)
        logo_table = Table([[logo_img, [
            Paragraph("AL HAMD TRADERS", brand_title_style),
            Spacer(1, 2),
            Paragraph("Distribution & Accounts Management System", brand_sub_style)
        ]]], colWidths=[54, 320])
        logo_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        left_header = logo_table
    else:
        left_header = [
            Paragraph("AL HAMD TRADERS", brand_title_style),
            Spacer(1, 2),
            Paragraph("Distribution & Accounts Management System", brand_sub_style)
        ]

    now_str = datetime.now().strftime("%d-%b-%Y %I:%M %p")
    meta_lines = [
        Paragraph(report_title, rep_title_style),
        Spacer(1, 3),
        Paragraph(f"<b>{period_or_subtitle}</b>", rep_meta_style),
        Paragraph(f"Generated on: {now_str}", rep_meta_style)
    ]
    if filter_text:
        meta_lines.append(Paragraph(filter_text, rep_meta_style))

    header_table = Table([[left_header, meta_lines]], colWidths=[380, 340])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    return header_table


def generate_history_pdf(transactions: list, start_date: str = None, end_date: str = None,
                         customer_filter: str = None, booker_filter: str = None,
                         type_filter: str = None, output_path: str = None) -> str:
    """
    Generates an executive-level, professionally styled PDF report of transaction history.
    Saves to output_path if provided, or DOCUMENTS_DIR with a timestamped name.
    Returns the absolute path to the generated PDF.
    """
    if not output_path:
        os.makedirs(DOCUMENTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = os.path.join(DOCUMENTS_DIR, f"AlHamd_History_Report_{timestamp}.pdf")
    else:
        filename = output_path
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)

    # Landscape letter is 792 x 612 pt. With 36 pt margins, printable width is 720 pt.
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    card_label_style = ParagraphStyle(
        'CardLabel', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.5, leading=10, alignment=1
    )
    card_val_style = ParagraphStyle(
        'CardVal', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, leading=15, alignment=1
    )
    cell_style = ParagraphStyle(
        'CellText', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=11,
        textColor=colors.HexColor('#1e293b')
    )
    cell_bold_style = ParagraphStyle('CellBold', parent=cell_style, fontName='Helvetica-Bold')
    cell_right_style = ParagraphStyle('CellRight', parent=cell_style, alignment=2)
    cell_right_bold = ParagraphStyle('CellRightBold', parent=cell_bold_style, alignment=2)

    elements = []

    # 1. Header Section
    if start_date and end_date:
        period_text = f"Period: {start_date} to {end_date}"
    elif start_date:
        period_text = f"From: {start_date}"
    elif end_date:
        period_text = f"Up to: {end_date}"
    else:
        period_text = "Period: All Recorded Transactions"

    filter_details = []
    if customer_filter and customer_filter != "All Customers":
        filter_details.append(f"Customer: {customer_filter}")
    if booker_filter and booker_filter != "All Bookers":
        filter_details.append(f"Booker: {booker_filter}")
    if type_filter and type_filter != "All Types":
        filter_details.append(f"Type: {type_filter}")
    f_str = f"Filter: {' | '.join(filter_details)}" if filter_details else None

    elements.append(_get_brand_header("TRANSACTION HISTORY REPORT", period_text, styles, f_str))
    elements.append(Spacer(1, 8))

    # Divider Line
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563eb'), spaceBefore=0, spaceAfter=10))

    # 2. Executive KPI Cards
    total_bills = 0
    total_recoveries = 0
    for tx in transactions:
        if tx['type'] == 'Bill':
            total_bills += tx['amount']
        else:
            total_recoveries += tx['amount']
            
    total_bills_rs = total_bills / 100.0
    total_rec_rs = total_recoveries / 100.0
    net_diff_rs = (total_bills - total_recoveries) / 100.0

    kpi_card_1 = [
        Paragraph("<font color='#991b1b'>TOTAL BILLS</font>", card_label_style),
        Spacer(1, 3),
        Paragraph(f"<font color='#b91c1c'>Rs. {total_bills_rs:,.2f}</font>", card_val_style)
    ]
    kpi_card_2 = [
        Paragraph("<font color='#166534'>TOTAL RECOVERIES</font>", card_label_style),
        Spacer(1, 3),
        Paragraph(f"<font color='#15803d'>Rs. {total_rec_rs:,.2f}</font>", card_val_style)
    ]
    kpi_card_3 = [
        Paragraph("<font color='#1e40af'>NET BALANCE MOVEMENT</font>", card_label_style),
        Spacer(1, 3),
        Paragraph(f"<font color='#1d4ed8'>Rs. {net_diff_rs:,.2f}</font>", card_val_style)
    ]
    kpi_card_4 = [
        Paragraph("<font color='#475569'>TOTAL RECORDS</font>", card_label_style),
        Spacer(1, 3),
        Paragraph(f"<font color='#0f172a'>{len(transactions):,} Entries</font>", card_val_style)
    ]

    summary_table = Table(
        [[kpi_card_1, kpi_card_2, kpi_card_3, kpi_card_4]],
        colWidths=[175, 175, 175, 175],
        rowHeights=[44]
    )
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#fef2f2')),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#f0fdf4')),
        ('BACKGROUND', (2, 0), (2, 0), colors.HexColor('#eff6ff')),
        ('BACKGROUND', (3, 0), (3, 0), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (0, 0), 1, colors.HexColor('#fecaca')),
        ('BOX', (1, 0), (1, 0), 1, colors.HexColor('#bbf7d0')),
        ('BOX', (2, 0), (2, 0), 1, colors.HexColor('#bfdbfe')),
        ('BOX', (3, 0), (3, 0), 1, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 12))

    # 3. Main Data Table: Date (75), Customer (185), Booker (100), Type (65), Amount (95), Prev Bal (100), New Bal (100) = 720
    header_row = [
        Paragraph("<b>Date</b>", ParagraphStyle('TH1', parent=cell_bold_style, textColor=colors.white)),
        Paragraph("<b>Customer Name</b>", ParagraphStyle('TH2', parent=cell_bold_style, textColor=colors.white)),
        Paragraph("<b>Booker</b>", ParagraphStyle('TH3', parent=cell_bold_style, textColor=colors.white)),
        Paragraph("<b>Type</b>", ParagraphStyle('TH4', parent=cell_bold_style, textColor=colors.white, alignment=1)),
        Paragraph("<b>Amount (Rs.)</b>", ParagraphStyle('TH5', parent=cell_bold_style, textColor=colors.white, alignment=2)),
        Paragraph("<b>Prev. Balance</b>", ParagraphStyle('TH6', parent=cell_bold_style, textColor=colors.white, alignment=2)),
        Paragraph("<b>New Balance</b>", ParagraphStyle('TH7', parent=cell_bold_style, textColor=colors.white, alignment=2)),
    ]
    
    table_data = [header_row]

    for tx in transactions:
        amount_rs = tx['amount'] / 100.0
        new_bal = tx['updated_balance']
        if tx['type'] == 'Bill':
            prev_bal = new_bal - tx['amount']
            type_markup = "<font color='#dc2626'><b>Bill</b></font>"
        else:
            prev_bal = new_bal + tx['amount']
            type_markup = "<font color='#16a34a'><b>Recovery</b></font>"

        prev_bal_rs = prev_bal / 100.0
        new_bal_rs = new_bal / 100.0

        row = [
            Paragraph(tx['transaction_date'], cell_style),
            Paragraph(tx.get('customer_name', ''), cell_bold_style),
            Paragraph(tx.get('booker_name', ''), cell_style),
            Paragraph(type_markup, ParagraphStyle('TCell', parent=cell_style, alignment=1)),
            Paragraph(f"{amount_rs:,.2f}", cell_right_bold),
            Paragraph(f"{prev_bal_rs:,.2f}", cell_right_style),
            Paragraph(f"{new_bal_rs:,.2f}", cell_right_bold),
        ]
        table_data.append(row)

    # Summary Row at bottom of table
    summary_row = [
        Paragraph("<b>TOTALS</b>", cell_bold_style),
        "", "", "", # Spanned across 4 columns
        Paragraph(f"<b>Rs. {(total_bills + total_recoveries) / 100.0:,.2f}</b>", cell_right_bold),
        "",
        Paragraph(f"<b>Diff: Rs. {net_diff_rs:,.2f}</b>", cell_right_bold)
    ]
    table_data.append(summary_row)

    main_table = Table(
        table_data,
        colWidths=[75, 185, 100, 65, 95, 100, 100],
        repeatRows=1
    )

    t_style = [
        # Header Row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        
        # Row styling
        ('TOPPADDING', (0, 1), (-1, -2), 3.5),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        
        # Lines
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#0f172a')),
        ('LINEBELOW', (0, 1), (-1, -2), 0.5, colors.HexColor('#e2e8f0')),
        
        # Totals Row
        ('SPAN', (0, -1), (3, -1)),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f1f5f9')),
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.HexColor('#94a3b8')),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor('#475569')),
        ('TOPPADDING', (0, -1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 5),
    ]

    # Alternating zebra striping
    for i in range(1, len(table_data) - 1):
        if i % 2 == 0:
            t_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8fafc')))
        else:
            t_style.append(('BACKGROUND', (0, i), (-1, i), colors.white))

    main_table.setStyle(TableStyle(t_style))
    elements.append(main_table)

    doc.build(elements, canvasmaker=NumberedCanvas)
    return filename


def generate_customer_ledger_pdf(customer: dict, transactions: list, output_path: str = None) -> str:
    """
    Generates an executive-level customer statement / ledger PDF report.
    Includes customer profile, opening balance, transaction ledger, and closing balance.
    """
    if not output_path:
        os.makedirs(DOCUMENTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        safe_name = "".join(c for c in customer.get('name', 'Customer') if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
        filename = os.path.join(DOCUMENTS_DIR, f"Statement_{safe_name}_{timestamp}.pdf")
    else:
        filename = output_path
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)

    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    elements = []

    # 1. Header
    cust_name = customer.get('name', 'Unknown Customer')
    elements.append(_get_brand_header("CUSTOMER ACCOUNT STATEMENT", f"Account: {cust_name}", styles))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563eb'), spaceBefore=0, spaceAfter=10))

    # 2. Customer Profile & Outstanding Banner Table
    opening_rs = customer.get('opening_balance', 0) / 100.0
    current_due_rs = customer.get('current_due', 0) / 100.0
    area_city = f"{customer.get('area') or 'N/A'}, {customer.get('city') or 'N/A'}"
    booker = customer.get('booker') or 'None'
    opening_date = customer.get('opening_date') or 'N/A'

    info_text = Paragraph(
        f"<b>Customer Name:</b> <font size='11'>{cust_name}</font><br/>"
        f"<b>Location:</b> {area_city} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Assigned Booker:</b> {booker}<br/>"
        f"<b>Account Opening Date:</b> {opening_date} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Opening Balance:</b> Rs. {opening_rs:,.2f}",
        ParagraphStyle('CustInfo', parent=styles['Normal'], fontSize=9, leading=14, textColor=colors.HexColor('#1e293b'))
    )

    due_text = Paragraph(
        f"<font size='8' color='#991b1b'>CURRENT OUTSTANDING BALANCE</font><br/>"
        f"<b><font size='15' color='#b91c1c'>Rs. {current_due_rs:,.2f}</font></b>",
        ParagraphStyle('DueBadge', parent=styles['Normal'], alignment=1, leading=18)
    )

    info_table = Table([[info_text, due_text]], colWidths=[520, 200])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#fef2f2')),
        ('BOX', (0, 0), (0, 0), 1, colors.HexColor('#e2e8f0')),
        ('BOX', (1, 0), (1, 0), 1, colors.HexColor('#fecaca')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 14))

    # 3. Ledger Table
    # Width: Date (80), Type (70), Notes (230), Bill (110), Recovery (110), Balance (120) = 720
    header_style = ParagraphStyle('LgHead', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)
    cell_style = ParagraphStyle('LgCell', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor('#1e293b'))
    cell_bold = ParagraphStyle('LgCellBold', parent=cell_style, fontName='Helvetica-Bold')
    cell_right = ParagraphStyle('LgRight', parent=cell_style, alignment=2)
    cell_right_bold = ParagraphStyle('LgRightBold', parent=cell_bold, alignment=2)

    ledger_data = [[
        Paragraph("<b>Date</b>", header_style),
        Paragraph("<b>Type</b>", ParagraphStyle('HType', parent=header_style, alignment=1)),
        Paragraph("<b>Description / Notes</b>", header_style),
        Paragraph("<b>Bill (Rs.)</b>", ParagraphStyle('HBill', parent=header_style, alignment=2)),
        Paragraph("<b>Recovery (Rs.)</b>", ParagraphStyle('HRec', parent=header_style, alignment=2)),
        Paragraph("<b>Balance (Rs.)</b>", ParagraphStyle('HBal', parent=header_style, alignment=2)),
    ]]

    # Opening row
    running_bal = customer.get('opening_balance', 0)
    ledger_data.append([
        Paragraph(opening_date if opening_date != 'N/A' else '-', cell_style),
        Paragraph("<b>Opening</b>", ParagraphStyle('OpType', parent=cell_style, alignment=1, textColor=colors.HexColor('#475569'))),
        Paragraph("Initial Account Balance", cell_style),
        Paragraph("-", cell_right),
        Paragraph("-", cell_right),
        Paragraph(f"{running_bal / 100.0:,.2f}", cell_right_bold)
    ])

    tot_bills = 0
    tot_rec = 0

    for tx in transactions:
        amt = tx['amount']
        if tx['type'] == 'Bill':
            running_bal += amt
            tot_bills += amt
            bill_str = f"{amt / 100.0:,.2f}"
            rec_str = "-"
            type_markup = "<font color='#dc2626'><b>Bill</b></font>"
        else:
            running_bal -= amt
            tot_rec += amt
            bill_str = "-"
            rec_str = f"{amt / 100.0:,.2f}"
            type_markup = "<font color='#16a34a'><b>Recovery</b></font>"

        ledger_data.append([
            Paragraph(tx['transaction_date'], cell_style),
            Paragraph(type_markup, ParagraphStyle('TType', parent=cell_style, alignment=1)),
            Paragraph(tx.get('notes') or '-', cell_style),
            Paragraph(bill_str, cell_right),
            Paragraph(rec_str, cell_right),
            Paragraph(f"{running_bal / 100.0:,.2f}", cell_right_bold)
        ])

    # Totals Row
    ledger_data.append([
        Paragraph("<b>TOTALS</b>", cell_bold),
        "", "",
        Paragraph(f"<b>Rs. {tot_bills / 100.0:,.2f}</b>", cell_right_bold),
        Paragraph(f"<b>Rs. {tot_rec / 100.0:,.2f}</b>", cell_right_bold),
        Paragraph(f"<b>Rs. {running_bal / 100.0:,.2f}</b>", cell_right_bold)
    ])

    l_table = Table(ledger_data, colWidths=[80, 70, 230, 110, 110, 120], repeatRows=1)
    lt_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 1), (-1, -2), 3.5),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#0f172a')),
        ('LINEBELOW', (0, 1), (-1, -2), 0.5, colors.HexColor('#e2e8f0')),
        
        # Totals
        ('SPAN', (0, -1), (2, -1)),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f1f5f9')),
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.HexColor('#94a3b8')),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor('#475569')),
        ('TOPPADDING', (0, -1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 5),
    ]

    for i in range(1, len(ledger_data) - 1):
        if i % 2 == 0:
            lt_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8fafc')))
        else:
            lt_style.append(('BACKGROUND', (0, i), (-1, i), colors.white))

    l_table.setStyle(TableStyle(lt_style))
    elements.append(l_table)

    doc.build(elements, canvasmaker=NumberedCanvas)
    return filename
