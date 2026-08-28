from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLabel, QFrame)
from PySide6.QtCore import Qt, Signal
from services.customer_service import get_all_customers, get_all_cities, get_all_areas
from services.booker_service import get_all_bookers
from utils import format_currency

class CustomersView(QWidget):
    customer_selected = Signal(int) # Emitted when a customer is clicked for detail view
    
    def __init__(self):
        super().__init__()
        self.customers_data = []
        self.setup_ui()
        
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)
        
        # Header Row (Title + Add Button)
        self.header_layout = QHBoxLayout()
        self.title = QLabel("Customers")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.header_layout.addWidget(self.title)
        
        from icons import get_svg_icon, SVG_ADD
        self.btn_add = QPushButton(" Add Customer")
        self.btn_add.setIcon(get_svg_icon(SVG_ADD, color="white"))
        self.btn_add.setProperty("class", "primary")
        self.btn_add.clicked.connect(self.show_add_dialog)
        self.header_layout.addWidget(self.btn_add, alignment=Qt.AlignRight)
        
        self.layout.addLayout(self.header_layout)
        
        # Filters
        self.filters_frame = QFrame()
        self.filters_frame.setProperty("class", "CardWidget")
        self.filters_layout = QHBoxLayout(self.filters_frame)
        self.filters_layout.setSpacing(15)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search customers...")
        self.search_input.setMaximumWidth(300)
        self.search_input.textChanged.connect(self.filter_table)
        self.filters_layout.addWidget(self.search_input)
        
        self.filter_booker = QComboBox()
        self.filter_booker.setMinimumWidth(200)
        self.filter_booker.currentIndexChanged.connect(self.filter_table)
        self.filters_layout.addWidget(self.filter_booker)
        
        self.filter_city = QComboBox()
        self.filter_city.setMinimumWidth(200)
        self.filter_city.currentIndexChanged.connect(self.filter_table)
        self.filters_layout.addWidget(self.filter_city)
        
        self.filters_layout.addStretch()
        
        self.layout.addWidget(self.filters_frame)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Customer", "Area", "City", "Booker", "Due", "Last Order"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellDoubleClicked.connect(self.on_customer_double_clicked)
        self.layout.addWidget(self.table)
        
        # Summary Row
        self.summary_layout = QHBoxLayout()
        self.lbl_total_customers = QLabel("0 Customers")
        self.lbl_total_customers.setStyleSheet("font-weight: bold; color: #86868b;")
        
        self.lbl_total_due = QLabel("Total Outstanding: Rs. 0")
        self.lbl_total_due.setStyleSheet("font-weight: bold; font-size: 16px; color: #ff3b30;")
        
        self.summary_layout.addWidget(self.lbl_total_customers)
        self.summary_layout.addStretch()
        self.summary_layout.addWidget(self.lbl_total_due)
        
        self.layout.addLayout(self.summary_layout)
        
    def refresh_data(self):
        # Update filter dropdowns
        self.filter_booker.blockSignals(True)
        self.filter_booker.clear()
        self.filter_booker.addItem("All Bookers", None)
        for b in get_all_bookers():
            self.filter_booker.addItem(b['name'], b['id'])
        self.filter_booker.blockSignals(False)
        
        self.filter_city.blockSignals(True)
        self.filter_city.clear()
        self.filter_city.addItem("All Cities", None)
        for c in get_all_cities():
            self.filter_city.addItem(c['name'], c['id'])
        self.filter_city.blockSignals(False)
        
        self.customers_data = get_all_customers()
        self.filter_table()
        
    def show_add_dialog(self):
        from views.add_customer_dialog import AddCustomerDialog
        from views.components import ModernDialog
        
        dialog = AddCustomerDialog(self)
        if dialog.exec():
            ModernDialog("Success", "Customer added successfully!", self).exec()
            self.refresh_data()
        
    def filter_table(self):
        search_text = self.search_input.text().lower()
        selected_booker_id = self.filter_booker.currentData()
        selected_city_id = self.filter_city.currentData()
        
        filtered = []
        for c in self.customers_data:
            if search_text and search_text not in c['name'].lower():
                continue
            # Since my get_all_customers query currently doesn't return booker_id/city_id but their names
            # Wait, get_all_customers() needs to return those IDs if we filter by them. 
            # I will modify the filtering to use names instead for simplicity, or just fetch them.
            # Actually, I can just use the string text for now.
            if selected_booker_id and self.filter_booker.currentText() != c.get('booker'):
                continue
            if selected_city_id and self.filter_city.currentText() != c.get('city'):
                continue
                
            filtered.append(c)
            
        self.populate_table(filtered)
        
    def populate_table(self, data):
        self.table.setRowCount(len(data))
        total_due = 0
        
        for row_idx, customer in enumerate(data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(customer['name']))
            self.table.setItem(row_idx, 1, QTableWidgetItem(customer.get('area') or ''))
            self.table.setItem(row_idx, 2, QTableWidgetItem(customer.get('city') or ''))
            self.table.setItem(row_idx, 3, QTableWidgetItem(customer.get('booker') or ''))
            
            due_amount = customer['current_due']
            total_due += due_amount
            
            due_item = QTableWidgetItem(format_currency(due_amount))
            due_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if due_amount == 0:
                due_item.setForeground(Qt.darkGreen)
            
            self.table.setItem(row_idx, 4, due_item)
            self.table.setItem(row_idx, 5, QTableWidgetItem(customer.get('last_order_date') or ''))
            
            # Store ID in the first column for reference
            self.table.item(row_idx, 0).setData(Qt.UserRole, customer['id'])
            
        self.lbl_total_customers.setText(f"{len(data)} Customers")
        self.lbl_total_due.setText(f"Total Outstanding: {format_currency(total_due)}")
        
    def on_customer_double_clicked(self, row, col):
        item = self.table.item(row, 0)
        if item:
            customer_id = item.data(Qt.UserRole)
            self.customer_selected.emit(customer_id)
