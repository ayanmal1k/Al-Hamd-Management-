from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QFrame)
from PySide6.QtCore import Qt, Signal
from services.customer_service import get_customer_by_id
from services.transaction_service import get_customer_transactions
from utils import format_currency, add_shadow

class CustomerDetailView(QWidget):
    back_clicked = Signal()
    
    def __init__(self):
        super().__init__()
        self.customer_id = None
        self.setup_ui()
        
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(20)
        
        # Header (Back Button + Title)
        self.header_layout = QHBoxLayout()
        from icons import get_svg_icon, SVG_BACK
        self.btn_back = QPushButton(" Back")
        self.btn_back.setIcon(get_svg_icon(SVG_BACK, color="#1d1d1f"))
        self.btn_back.clicked.connect(self.back_clicked.emit)
        self.header_layout.addWidget(self.btn_back)
        
        self.title = QLabel("Customer Detail")
        self.title.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.header_layout.addWidget(self.title, stretch=1)
        
        self.layout.addLayout(self.header_layout)
        
        # Info Card
        self.info_card = QFrame()
        self.info_card.setProperty("class", "CardWidget")
        add_shadow(self.info_card)
        self.info_layout = QHBoxLayout(self.info_card)
        
        self.lbl_name = QLabel("Name: ")
        self.lbl_name.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.lbl_area_city = QLabel("Area, City")
        self.lbl_booker = QLabel("Assigned Booker:")
        self.lbl_due = QLabel("Current Due: Rs. 0")
        self.lbl_due.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff3b30;")
        
        left_info = QVBoxLayout()
        left_info.addWidget(self.lbl_name)
        left_info.addWidget(self.lbl_area_city)
        left_info.addWidget(self.lbl_booker)
        
        self.info_layout.addLayout(left_info)
        self.info_layout.addStretch()
        self.info_layout.addWidget(self.lbl_due, alignment=Qt.AlignTop)
        
        self.layout.addWidget(self.info_card)
        
        # Ledger Title
        self.ledger_label = QLabel("Mini-Ledger (Chronological History)")
        self.ledger_label.setStyleSheet("font-size: 16px; font-weight: 500;")
        self.layout.addWidget(self.ledger_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Date", "Type", "Notes", "Bill", "Recovery", "Balance"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.layout.addWidget(self.table)
        
    def load_customer(self, customer_id):
        self.customer_id = customer_id
        customer = get_customer_by_id(customer_id)
        if not customer:
            return
            
        self.lbl_name.setText(customer['name'])
        area = customer.get('area') or 'Unknown'
        city = customer.get('city') or 'Unknown'
        self.lbl_area_city.setText(f"{area}, {city}")
        
        booker = customer.get('booker') or 'None'
        self.lbl_booker.setText(f"Assigned Booker: {booker}")
        
        due = customer['current_due']
        self.lbl_due.setText(f"Current Due: {format_currency(due)}")
        if due == 0:
            self.lbl_due.setStyleSheet("font-size: 18px; font-weight: bold; color: green;")
        else:
            self.lbl_due.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff3b30;")
            
        self.load_ledger(customer['opening_balance'])
        
    def load_ledger(self, opening_balance):
        transactions = get_customer_transactions(self.customer_id)
        
        # Row count = 1 (Opening) + transactions
        self.table.setRowCount(len(transactions) + 1)
        
        # Opening row
        self.table.setItem(0, 0, QTableWidgetItem("-"))
        self.table.setItem(0, 1, QTableWidgetItem("Opening Balance"))
        self.table.setItem(0, 2, QTableWidgetItem("-"))
        self.table.setItem(0, 3, QTableWidgetItem("-"))
        self.table.setItem(0, 4, QTableWidgetItem("-"))
        
        balance = opening_balance
        bal_item = QTableWidgetItem(format_currency(balance))
        bal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(0, 5, bal_item)
        
        # Transactions
        for i, tx in enumerate(transactions, start=1):
            self.table.setItem(i, 0, QTableWidgetItem(tx['transaction_date']))
            self.table.setItem(i, 1, QTableWidgetItem(tx['type']))
            self.table.setItem(i, 2, QTableWidgetItem(tx.get('notes') or ''))
            
            bill_item = QTableWidgetItem("-")
            rec_item = QTableWidgetItem("-")
            
            if tx['type'] == 'Bill':
                bill_item.setText(format_currency(tx['amount']))
                balance += tx['amount']
            elif tx['type'] == 'Recovery':
                rec_item.setText(format_currency(tx['amount']))
                balance -= tx['amount']
                
            bill_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            rec_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            self.table.setItem(i, 3, bill_item)
            self.table.setItem(i, 4, rec_item)
            
            bal_item = QTableWidgetItem(format_currency(balance))
            bal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 5, bal_item)
