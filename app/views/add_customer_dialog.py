from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit, 
                               QPushButton)
from views.components import ModernDialog
from PySide6.QtCore import Qt, QDate
from services.customer_service import get_all_areas, get_all_cities, get_or_create_area, get_or_create_city, create_customer
from services.booker_service import get_active_bookers

class AddCustomerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Customer")
        self.setMinimumWidth(400)
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        
        # Name
        self.layout.addWidget(QLabel("Customer Name:"))
        self.inp_name = QLineEdit()
        self.layout.addWidget(self.inp_name)
        
        # Area
        self.layout.addWidget(QLabel("Area:"))
        self.combo_area = QComboBox()
        self.combo_area.setEditable(True)
        self.layout.addWidget(self.combo_area)
        
        # City
        self.layout.addWidget(QLabel("City:"))
        self.combo_city = QComboBox()
        self.combo_city.setEditable(True)
        self.layout.addWidget(self.combo_city)
        
        # Booker
        self.layout.addWidget(QLabel("Assigned Booker:"))
        self.combo_booker = QComboBox()
        self.layout.addWidget(self.combo_booker)
        
        # Opening Balance
        self.layout.addWidget(QLabel("Opening Balance (Rs.):"))
        self.spin_balance = QDoubleSpinBox()
        self.spin_balance.setRange(0, 100000000)
        self.spin_balance.setDecimals(0)
        self.layout.addWidget(self.spin_balance)
        
        # Opening Date
        self.layout.addWidget(QLabel("Opening Date:"))
        self.date_open = QDateEdit()
        self.date_open.setCalendarPopup(True)
        self.date_open.setDate(QDate.currentDate())
        self.layout.addWidget(self.date_open)
        
        # Buttons
        self.btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save Customer")
        self.btn_save.setProperty("class", "primary")
        self.btn_save.clicked.connect(self.save_customer)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.btn_cancel)
        self.btn_layout.addWidget(self.btn_save)
        
        self.layout.addLayout(self.btn_layout)
        
    def load_data(self):
        # Load Areas
        areas = get_all_areas()
        for a in areas:
            self.combo_area.addItem(a['name'], a['id'])
            
        # Load Cities
        cities = get_all_cities()
        for c in cities:
            self.combo_city.addItem(c['name'], c['id'])
            
        # Set default city to Lahore if it exists
        index = self.combo_city.findText("Lahore")
        if index >= 0:
            self.combo_city.setCurrentIndex(index)
            
        # Load Bookers
        bookers = get_active_bookers()
        self.combo_booker.addItem("None", None)
        for b in bookers:
            self.combo_booker.addItem(b['name'], b['id'])
            
    def save_customer(self):
        name = self.inp_name.text().strip()
        if not name:
            ModernDialog("Validation Error", "Customer name is required.", self, is_error=True).exec()
            return
            
        area_name = self.combo_area.currentText().strip()
        city_name = self.combo_city.currentText().strip()
        booker_id = self.combo_booker.currentData()
        balance_rs = self.spin_balance.value()
        date_str = self.date_open.date().toString(Qt.ISODate)
        
        try:
            area_id = get_or_create_area(area_name) if area_name else None
            city_id = get_or_create_city(city_name) if city_name else None
            balance_paisa = int(balance_rs * 100)
            
            create_customer(name, area_id, city_id, booker_id, date_str, balance_paisa)
            self.accept()
        except Exception as e:
            ModernDialog("Error", f"Failed to save customer:\n{str(e)}", self, is_error=True).exec()
