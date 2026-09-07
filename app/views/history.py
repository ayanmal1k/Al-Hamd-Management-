import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                               QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QFrame, QDateEdit, QFileDialog)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from services.transaction_service import get_filtered_history
from services.customer_service import get_all_customers
from services.booker_service import get_active_bookers
from services.report_service import generate_history_pdf
from utils import format_currency

class HistoryView(QWidget):
    def __init__(self):
        super().__init__()
        self.transactions = []
        self.setup_ui()
        
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)
        
        # Header Row
        self.header_layout = QHBoxLayout()
        self.title = QLabel("Transaction History")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.header_layout.addWidget(self.title)
        
        from icons import get_svg_icon, SVG_EXPORT
        self.btn_export = QPushButton(" Export View (PDF)")
        self.btn_export.setIcon(get_svg_icon(SVG_EXPORT, color="white"))
        self.btn_export.setProperty("class", "primary")
        self.btn_export.clicked.connect(lambda: self.export_pdf(export_all=False))
        self.header_layout.addWidget(self.btn_export, alignment=Qt.AlignRight)
        
        self.btn_export_all = QPushButton(" Export All (PDF)")
        self.btn_export_all.setIcon(get_svg_icon(SVG_EXPORT, color="#1d1d1f"))
        self.btn_export_all.clicked.connect(lambda: self.export_pdf(export_all=True))
        self.header_layout.addWidget(self.btn_export_all)
        
        self.layout.addLayout(self.header_layout)
        
        # Filters
        self.filters_frame = QFrame()
        self.filters_frame.setProperty("class", "CardWidget")
        self.filters_layout = QHBoxLayout(self.filters_frame)
        
        # Date From
        self.lbl_from = QLabel("From:")
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30)) # Default 30 days
        self.date_from.dateChanged.connect(self.refresh_table)
        self.filters_layout.addWidget(self.lbl_from)
        self.filters_layout.addWidget(self.date_from)
        
        # Date To
        self.lbl_to = QLabel("To:")
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.dateChanged.connect(self.refresh_table)
        self.filters_layout.addWidget(self.lbl_to)
        self.filters_layout.addWidget(self.date_to)
        
        # Customer
        self.filter_customer = QComboBox()
        self.filter_customer.currentIndexChanged.connect(self.refresh_table)
        self.filters_layout.addWidget(self.filter_customer)
        
        # Booker
        self.filter_booker = QComboBox()
        self.filter_booker.currentIndexChanged.connect(self.refresh_table)
        self.filters_layout.addWidget(self.filter_booker)
        
        # Type
        self.filter_type = QComboBox()
        self.filter_type.addItems(["All Types", "Bill", "Recovery"])
        self.filter_type.currentIndexChanged.connect(self.refresh_table)
        self.filters_layout.addWidget(self.filter_type)
        
        self.layout.addWidget(self.filters_frame)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Date", "Customer", "Booker", "Type", "Amount", "Prev. Balance", "New Balance"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.layout.addWidget(self.table)
        
        # Summary Row
        self.summary_layout = QHBoxLayout()
        self.lbl_total_bills = QLabel("Total Bills: Rs. 0")
        self.lbl_total_bills.setStyleSheet("font-weight: bold; font-size: 16px; color: #ff3b30;")
        
        self.lbl_total_recoveries = QLabel("Total Recoveries: Rs. 0")
        self.lbl_total_recoveries.setStyleSheet("font-weight: bold; font-size: 16px; color: green;")
        
        self.summary_layout.addWidget(self.lbl_total_bills)
        self.summary_layout.addWidget(self.lbl_total_recoveries)
        self.summary_layout.addStretch()
        
        self.layout.addLayout(self.summary_layout)
        
    def refresh_data(self):
        # Refresh filters
        self.filter_customer.blockSignals(True)
        self.filter_customer.clear()
        self.filter_customer.addItem("All Customers", None)
        for c in get_all_customers():
            self.filter_customer.addItem(c['name'], c['id'])
        self.filter_customer.blockSignals(False)
        
        self.filter_booker.blockSignals(True)
        self.filter_booker.clear()
        self.filter_booker.addItem("All Bookers", None)
        for b in get_active_bookers():
            self.filter_booker.addItem(b['name'], b['id'])
        self.filter_booker.blockSignals(False)
        
        self.refresh_table()
        
    def refresh_table(self):
        start_date = self.date_from.date().toString(Qt.ISODate)
        end_date = self.date_to.date().toString(Qt.ISODate)
        customer_id = self.filter_customer.currentData()
        booker_id = self.filter_booker.currentData()
        
        tx_type = None
        if self.filter_type.currentIndex() == 1:
            tx_type = "Bill"
        elif self.filter_type.currentIndex() == 2:
            tx_type = "Recovery"
            
        self.transactions = get_filtered_history(start_date, end_date, customer_id, booker_id, tx_type)
        
        self.table.setRowCount(len(self.transactions))
        total_bills = 0
        total_recoveries = 0
        
        for row_idx, tx in enumerate(self.transactions):
            self.table.setItem(row_idx, 0, QTableWidgetItem(tx['transaction_date']))
            self.table.setItem(row_idx, 1, QTableWidgetItem(tx['customer_name']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(tx['booker_name']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(tx['type']))
            
            amt_item = QTableWidgetItem(format_currency(tx['amount']))
            amt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row_idx, 4, amt_item)
            
            new_bal = tx['updated_balance']
            if tx['type'] == 'Bill':
                prev_bal = new_bal - tx['amount']
                total_bills += tx['amount']
            else:
                prev_bal = new_bal + tx['amount']
                total_recoveries += tx['amount']
                
            prev_item = QTableWidgetItem(format_currency(prev_bal))
            prev_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row_idx, 5, prev_item)
            
            new_item = QTableWidgetItem(format_currency(new_bal))
            new_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row_idx, 6, new_item)
                
        self.lbl_total_bills.setText(f"Total Bills: {format_currency(total_bills)}")
        self.lbl_total_recoveries.setText(f"Total Recoveries: {format_currency(total_recoveries)}")
        
    def export_pdf(self, export_all=False):
        from views.components import ModernDialog
        from paths import get_documents_dir
        from datetime import datetime
        try:
            if export_all:
                txs = get_filtered_history() # Fetches complete unfiltered transactions
                start_date = None
                end_date = None
                cust_filter = None
                booker_filter = None
                type_filter = None
                timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                default_name = f"AlHamd_Complete_History_{timestamp}.pdf"
            else:
                txs = self.transactions
                start_date = self.date_from.date().toString(Qt.ISODate)
                end_date = self.date_to.date().toString(Qt.ISODate)
                cust_filter = self.filter_customer.currentText()
                booker_filter = self.filter_booker.currentText()
                type_filter = self.filter_type.currentText()
                default_name = f"AlHamd_History_{start_date}_to_{end_date}.pdf"
                
            if not txs:
                ModernDialog("Notice", "No transactions found to export.", self).exec()
                return

            default_path = os.path.join(get_documents_dir(), default_name)
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save PDF Report", default_path, "PDF Documents (*.pdf);;All Files (*)"
            )
            if not save_path:
                return

            filename = generate_history_pdf(
                transactions=txs,
                start_date=start_date,
                end_date=end_date,
                customer_filter=cust_filter,
                booker_filter=booker_filter,
                type_filter=type_filter,
                output_path=save_path
            )
            
            ModernDialog("Export Successful", f"PDF report saved successfully to:\n{filename}", self).exec()
            # Automatically open the PDF
            QDesktopServices.openUrl(QUrl.fromLocalFile(filename))
        except Exception as e:
            ModernDialog("Export Failed", f"Failed to generate PDF:\n{str(e)}", self, is_error=True).exec()

