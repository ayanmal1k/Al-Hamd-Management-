from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                               QLabel, QDoubleSpinBox, QDateEdit, QPushButton, QFrame)
from views.components import ModernDialog
from PySide6.QtCore import Qt, QDate
from services.customer_service import get_all_customers
from services.booker_service import get_active_bookers
from services.transaction_service import add_transaction
from utils import format_currency, add_shadow

class AddTransactionView(QWidget):
    def __init__(self, tx_type="Bill"):
        super().__init__()
        self.tx_type = tx_type
        self.customers = []
        self.bookers = []
        self.setup_ui()
        
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(20)
        
        # Header
        self.title = QLabel(f"Add {self.tx_type}")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title)
        
        # Form Card
        self.form_card = QFrame()
        self.form_card.setProperty("class", "CardWidget")
        add_shadow(self.form_card)
        
        self.form_layout = QVBoxLayout(self.form_card)
        self.form_layout.setSpacing(15)
        
        # Customer
        self.lbl_customer = QLabel("Customer:")
        self.combo_customer = QComboBox()
        self.combo_customer.currentIndexChanged.connect(self.on_customer_changed)
        self.form_layout.addWidget(self.lbl_customer)
        self.form_layout.addWidget(self.combo_customer)
        
        # Current Due display
        self.lbl_due = QLabel("Current Due: Rs. 0")
        self.lbl_due.setStyleSheet("font-size: 16px; font-weight: bold; color: #ff3b30;")
        self.form_layout.addWidget(self.lbl_due)
        
        # Booker
        self.lbl_booker = QLabel("Salesman / Booker:")
        self.combo_booker = QComboBox()
        self.form_layout.addWidget(self.lbl_booker)
        self.form_layout.addWidget(self.combo_booker)
        
        # Amount
        self.lbl_amount = QLabel(f"{self.tx_type} Amount (Rs.):")
        self.spin_amount = QDoubleSpinBox()
        self.spin_amount.setRange(0, 100000000)
        self.spin_amount.setDecimals(0) # Keep it simple
        self.form_layout.addWidget(self.lbl_amount)
        self.form_layout.addWidget(self.spin_amount)
        
        # Date
        self.lbl_date = QLabel("Date:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.form_layout.addWidget(self.lbl_date)
        self.form_layout.addWidget(self.date_edit)
        
        # Save Button
        self.btn_save = QPushButton("Save Transaction")
        self.btn_save.setProperty("class", "primary")
        self.btn_save.clicked.connect(self.save_transaction)
        self.form_layout.addWidget(self.btn_save)
        
        self.layout.addWidget(self.form_card)
        self.layout.addStretch()
        
    def refresh_data(self):
        self.combo_customer.blockSignals(True)
        self.combo_customer.clear()
        
        self.customers = get_all_customers()
        for c in self.customers:
            self.combo_customer.addItem(f"{c['name']} ({c.get('area') or 'No Area'})", c['id'])
            
        self.combo_customer.blockSignals(False)
        
        self.combo_booker.blockSignals(True)
        self.combo_booker.clear()
        self.bookers = get_active_bookers()
        for b in self.bookers:
            self.combo_booker.addItem(b['name'], b['id'])
        self.combo_booker.blockSignals(False)
        
        if self.customers:
            self.on_customer_changed(0)
            
    def on_customer_changed(self, index):
        if index < 0 or index >= len(self.customers):
            return
            
        customer = self.customers[index]
        self.lbl_due.setText(f"Current Due: {format_currency(customer['current_due'])}")
        
        # Pre-select assigned booker
        booker_name = customer.get('booker')
        if booker_name:
            index = self.combo_booker.findText(booker_name)
            if index >= 0:
                self.combo_booker.setCurrentIndex(index)
                
    def save_transaction(self):
        customer_id = self.combo_customer.currentData()
        booker_id = self.combo_booker.currentData()
        amount_rs = self.spin_amount.value()
        date_str = self.date_edit.date().toString(Qt.ISODate)
        
        if not customer_id or not booker_id:
            ModernDialog("Error", "Please select a customer and a booker.", self, is_error=True).exec()
            return
            
        if amount_rs <= 0:
            ModernDialog("Error", "Amount must be greater than 0.", self, is_error=True).exec()
            return
            
        amount_paisa = int(amount_rs * 100)
        
        try:
            add_transaction(customer_id, booker_id, self.tx_type, amount_paisa, date_str)
            ModernDialog("Success", f"{self.tx_type} saved successfully!", self).exec()
            self.spin_amount.setValue(0)
            self.refresh_data()
        except Exception as e:
            ModernDialog("Error", f"Failed to save transaction:\n{str(e)}", self, is_error=True).exec()
