from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QFrame, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from utils import format_currency, add_shadow
from database import db_session
from datetime import date

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(20)
        
        # Header
        self.header_label = QLabel("Good Morning\nALHAMD TRADERS")
        self.header_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.header_label)
        
        # Stats Row
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(20)
        
        self.card_customers = self.create_stat_card("Customers", "0")
        self.card_outstanding = self.create_stat_card("Total Outstanding", "Rs. 0", True)
        self.card_bills = self.create_stat_card("Today's Bills", "Rs. 0")
        self.card_recoveries = self.create_stat_card("Today's Recoveries", "Rs. 0")
        
        self.stats_layout.addWidget(self.card_customers[0])
        self.stats_layout.addWidget(self.card_outstanding[0])
        self.stats_layout.addWidget(self.card_bills[0])
        self.stats_layout.addWidget(self.card_recoveries[0])
        
        self.layout.addLayout(self.stats_layout)
        
        # Top Customers Table
        self.layout.addSpacing(20)
        self.table_label = QLabel("Top Outstanding Customers")
        self.table_label.setStyleSheet("font-size: 18px; font-weight: 500;")
        self.layout.addWidget(self.table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Customer", "Outstanding"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)
        self.layout.addWidget(self.table)
        
    def create_stat_card(self, title, initial_value, is_primary=False):
        card = QFrame()
        card.setProperty("class", "CardWidget")
        add_shadow(card)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #86868b; font-size: 14px; font-weight: 600;")
        
        value_label = QLabel(initial_value)
        if is_primary:
            value_label.setStyleSheet("color: #ff3b30; font-size: 28px; font-weight: bold;")
        else:
            value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
            
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card, value_label
        
    def refresh_data(self):
        with db_session() as conn:
            cursor = conn.cursor()
            
            # Total Customers
            cursor.execute("SELECT COUNT(*) FROM customers WHERE is_active = 1")
            self.card_customers[1].setText(str(cursor.fetchone()[0]))
            
            # Total Outstanding
            cursor.execute('''
                SELECT COALESCE(SUM(c.opening_balance), 0) + 
                       COALESCE((SELECT SUM(amount) FROM transactions WHERE type = 'Bill'), 0) -
                       COALESCE((SELECT SUM(amount) FROM transactions WHERE type = 'Recovery'), 0)
                FROM customers c WHERE c.is_active = 1
            ''')
            total_out = cursor.fetchone()[0] or 0
            self.card_outstanding[1].setText(format_currency(total_out))
            
            # Today's Bills & Recoveries
            today = date.today().isoformat()
            cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type = 'Bill' AND transaction_date = ?", (today,))
            self.card_bills[1].setText(format_currency(cursor.fetchone()[0]))
            
            cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type = 'Recovery' AND transaction_date = ?", (today,))
            self.card_recoveries[1].setText(format_currency(cursor.fetchone()[0]))
            
            # Top Customers
            cursor.execute('''
                SELECT c.name, 
                       c.opening_balance + 
                       COALESCE(SUM(CASE WHEN t.type = 'Bill' THEN t.amount ELSE 0 END), 0) -
                       COALESCE(SUM(CASE WHEN t.type = 'Recovery' THEN t.amount ELSE 0 END), 0) as current_due
                FROM customers c
                LEFT JOIN transactions t ON c.id = t.customer_id
                WHERE c.is_active = 1
                GROUP BY c.id
                ORDER BY current_due DESC
                LIMIT 10
            ''')
            
            top_customers = cursor.fetchall()
            self.table.setRowCount(len(top_customers))
            
            for row_idx, row_data in enumerate(top_customers):
                self.table.setItem(row_idx, 0, QTableWidgetItem(row_data['name']))
                
                due_item = QTableWidgetItem(format_currency(row_data['current_due']))
                due_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row_idx, 1, due_item)
