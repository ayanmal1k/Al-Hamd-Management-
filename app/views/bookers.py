from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView, QLabel)
from PySide6.QtCore import Qt
from services.booker_service import get_all_bookers
from utils import format_currency

class BookersView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)
        
        # Header Row
        self.header_layout = QHBoxLayout()
        self.title = QLabel("Bookers / Salesmen")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.header_layout.addWidget(self.title)
        
        from icons import get_svg_icon, SVG_ADD
        self.btn_add_booker = QPushButton(" Add Booker")
        self.btn_add_booker.setIcon(get_svg_icon(SVG_ADD, color="white"))
        self.btn_add_booker.setProperty("class", "primary")
        self.btn_add_booker.clicked.connect(self.show_add_dialog)
        self.header_layout.addWidget(self.btn_add_booker, alignment=Qt.AlignRight)
        
        self.layout.addLayout(self.header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Status", "Assigned Customers", "Total Outstanding"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.layout.addWidget(self.table)
        
    def show_add_dialog(self):
        from PySide6.QtWidgets import QInputDialog
        from views.components import ModernDialog
        from services.booker_service import create_booker
        
        name, ok = QInputDialog.getText(self, "Add Booker", "Enter Booker Name:")
        if ok and name.strip():
            try:
                create_booker(name.strip())
                self.refresh_data()
                ModernDialog("Success", "Booker added successfully.", self).exec()
            except Exception as e:
                ModernDialog("Error", f"Failed to add booker:\n{str(e)}", self, is_error=True).exec()
                
    def refresh_data(self):
        bookers = get_all_bookers()
        self.table.setRowCount(len(bookers))
        
        for row_idx, booker in enumerate(bookers):
            self.table.setItem(row_idx, 0, QTableWidgetItem(booker['name']))
            
            status = "Active" if booker['is_active'] else "Inactive"
            self.table.setItem(row_idx, 1, QTableWidgetItem(status))
            
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(booker['total_customers'])))
            
            due_item = QTableWidgetItem(format_currency(booker['total_outstanding']))
            due_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row_idx, 3, due_item)
