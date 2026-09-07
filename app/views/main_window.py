from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QFrame)
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Alhamd Traders")
        self.setMinimumSize(1200, 800)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main Layout
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(250)
        
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(0)
        
        # Brand Logo
        import os
        from PySide6.QtGui import QPixmap
        
        self.brand_label = QLabel()
        self.brand_label.setObjectName("brandLabel")
        self.brand_label.setAlignment(Qt.AlignCenter)
        
        from paths import get_asset_path
        logo_path = get_asset_path('logo.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale the logo down slightly to fit well in the sidebar
            self.brand_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.brand_label.setText("ALHAMD\nTRADERS")
            
        self.sidebar_layout.addWidget(self.brand_label)
        
        # Navigation Buttons
        self.nav_buttons = []
        
        from icons import get_svg_icon, SVG_DASHBOARD, SVG_USERS, SVG_BOOKERS, SVG_BILL, SVG_RECOVERY, SVG_HISTORY, SVG_SETTINGS
        
        self.btn_dashboard = self.create_nav_button(" Dashboard", get_svg_icon(SVG_DASHBOARD))
        self.btn_customers = self.create_nav_button(" Customers", get_svg_icon(SVG_USERS))
        self.btn_bookers = self.create_nav_button(" Bookers", get_svg_icon(SVG_BOOKERS))
        
        self.sidebar_layout.addSpacing(20)
        self.btn_add_bill = self.create_nav_button(" Add Bill", get_svg_icon(SVG_BILL))
        self.btn_add_recovery = self.create_nav_button(" Add Recovery", get_svg_icon(SVG_RECOVERY))
        
        self.sidebar_layout.addSpacing(20)
        self.btn_history = self.create_nav_button(" History", get_svg_icon(SVG_HISTORY))
        
        self.sidebar_layout.addStretch()
        self.btn_settings = self.create_nav_button(" Settings", get_svg_icon(SVG_SETTINGS))
        self.sidebar_layout.addSpacing(20)
        
        self.main_layout.addWidget(self.sidebar)
        
        # Content Area
        self.content_area = QFrame()
        self.content_area.setObjectName("contentArea")
        
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
        from views.components import FadingStackedWidget
        self.stacked_widget = FadingStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)
        
        self.main_layout.addWidget(self.content_area, stretch=1)
        
        # Views
        from views.dashboard import DashboardView
        from views.customers import CustomersView
        from views.customer_detail import CustomerDetailView
        from views.bookers import BookersView
        from views.add_bill import AddTransactionView
        from views.history import HistoryView
        from views.settings import SettingsView
        
        self.view_dashboard = DashboardView()
        self.view_customers = CustomersView()
        self.view_customer_detail = CustomerDetailView()
        self.view_bookers = BookersView()
        self.view_add_bill = AddTransactionView("Bill")
        self.view_add_recovery = AddTransactionView("Recovery")
        self.view_history = HistoryView()
        self.view_settings = SettingsView()
        
        self.stacked_widget.addWidget(self.view_dashboard) # 0
        self.stacked_widget.addWidget(self.view_customers) # 1
        self.stacked_widget.addWidget(self.view_bookers) # 2
        self.stacked_widget.addWidget(self.view_add_bill) # 3
        self.stacked_widget.addWidget(self.view_add_recovery) # 4
        self.stacked_widget.addWidget(self.view_history) # 5
        self.stacked_widget.addWidget(self.view_settings) # 6
        self.stacked_widget.addWidget(self.view_customer_detail) # 7
        
        # Map buttons to indices
        self.btn_dashboard.clicked.connect(lambda: self.switch_view(0))
        self.btn_customers.clicked.connect(lambda: self.switch_view(1))
        self.btn_bookers.clicked.connect(lambda: self.switch_view(2))
        self.btn_add_bill.clicked.connect(lambda: self.switch_view(3))
        self.btn_add_recovery.clicked.connect(lambda: self.switch_view(4))
        self.btn_history.clicked.connect(lambda: self.switch_view(5))
        self.btn_settings.clicked.connect(lambda: self.switch_view(6))
        
        # Signals
        self.view_customers.customer_selected.connect(self.show_customer_detail)
        self.view_customer_detail.back_clicked.connect(lambda: self.switch_view(1))
        
        # Set active initially
        self.switch_view(0)
        
    def create_nav_button(self, text, icon=None):
        btn = QPushButton(text)
        if icon:
            btn.setIcon(icon)
        btn.setCheckable(True)
        self.sidebar_layout.addWidget(btn)
        self.nav_buttons.append(btn)
        return btn
        
    def switch_view(self, index):
        self.stacked_widget.setCurrentIndex(index)
        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, 'refresh_data'):
            current_widget.refresh_data()
            
        # Update active button (0-6 map directly to nav_buttons)
        if index < len(self.nav_buttons):
            for i, btn in enumerate(self.nav_buttons):
                btn.setChecked(i == index)
        else:
            # If it's a detail view (index 7), keep the parent's button active
            if index == 7:
                self.nav_buttons[1].setChecked(True) # Customers
                
    def show_customer_detail(self, customer_id):
        self.view_customer_detail.load_customer(customer_id)
        self.switch_view(7)
