import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QFrame, QComboBox,
    QLineEdit, QDateEdit, QAbstractItemView, QCompleter
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor, QDesktopServices
from PySide6.QtCore import QUrl

from services.customer_service import get_all_customers, get_customer_by_id
from services.transaction_service import get_customer_transactions
from utils import format_currency, add_shadow
from icons import get_svg_icon, SVG_BACK, SVG_EXPORT, SVG_RECOVERY, SVG_BILL, SVG_CHECK
from paths import get_documents_dir

class LedgerView(QWidget):
    back_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.customers_list = []
        self.current_customer = None
        self.current_transactions = []
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(14)

        # 1. Header (Back Button, Title, Export PDF)
        self.header_layout = QHBoxLayout()
        self.btn_back = QPushButton(" Back")
        self.btn_back.setIcon(get_svg_icon(SVG_BACK, color="#1d1d1f"))
        self.btn_back.clicked.connect(self.back_clicked.emit)
        self.btn_back.setVisible(False) # Shown when navigated from another view
        self.header_layout.addWidget(self.btn_back)

        title_layout = QVBoxLayout()
        self.title = QLabel("Customer Ledger")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1d1d1f;")
        self.subtitle = QLabel("Track transaction dates, bill history, and payment recoveries")
        self.subtitle.setStyleSheet("font-size: 13px; color: #64748b;")
        title_layout.addWidget(self.title)
        title_layout.addWidget(self.subtitle)
        self.header_layout.addLayout(title_layout, stretch=1)

        self.btn_export_pdf = QPushButton(" Export Statement (PDF)")
        self.btn_export_pdf.setIcon(get_svg_icon(SVG_EXPORT, color="white"))
        self.btn_export_pdf.setProperty("class", "primary")
        self.btn_export_pdf.clicked.connect(self.export_statement_pdf)
        self.header_layout.addWidget(self.btn_export_pdf)

        self.main_layout.addLayout(self.header_layout)

        # 2. Controls & Filter Card
        self.filter_card = QFrame()
        self.filter_card.setProperty("class", "CardWidget")
        add_shadow(self.filter_card)
        filter_card_layout = QVBoxLayout(self.filter_card)
        filter_card_layout.setSpacing(10)
        filter_card_layout.setContentsMargins(16, 14, 16, 14)

        # Row 1: Customer Selection & Quick Steppers
        cust_row = QHBoxLayout()
        cust_row.setSpacing(10)

        lbl_cust = QLabel("Customer:")
        lbl_cust.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        cust_row.addWidget(lbl_cust)

        self.combo_customers = QComboBox()
        self.combo_customers.setEditable(True)
        self.combo_customers.setInsertPolicy(QComboBox.NoInsert)
        self.combo_customers.setMinimumWidth(320)
        self.combo_customers.currentIndexChanged.connect(self.on_customer_changed)
        cust_row.addWidget(self.combo_customers, stretch=2)

        self.btn_prev_cust = QPushButton("◀ Prev")
        self.btn_prev_cust.setToolTip("Previous Customer")
        self.btn_prev_cust.clicked.connect(self.prev_customer)
        cust_row.addWidget(self.btn_prev_cust)

        self.btn_next_cust = QPushButton("Next ▶")
        self.btn_next_cust.setToolTip("Next Customer")
        self.btn_next_cust.clicked.connect(self.next_customer)
        cust_row.addWidget(self.btn_next_cust)

        cust_row.addSpacing(15)

        lbl_filter = QLabel("Show:")
        lbl_filter.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        cust_row.addWidget(lbl_filter)

        self.combo_type_filter = QComboBox()
        self.combo_type_filter.addItem("All Entries (Bills & Recoveries)", "All")
        self.combo_type_filter.addItem("🟢 Recoveries Only (Payments In)", "Recovery")
        self.combo_type_filter.addItem("🔴 Bills Only (Sales Out)", "Bill")
        self.combo_type_filter.setMinimumWidth(240)
        self.combo_type_filter.currentIndexChanged.connect(self.filter_ledger)
        cust_row.addWidget(self.combo_type_filter, stretch=1)

        filter_card_layout.addLayout(cust_row)

        # Row 2: Date Filters
        date_row = QHBoxLayout()
        date_row.setSpacing(10)

        lbl_date_filter = QLabel("Date Range:")
        lbl_date_filter.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        date_row.addWidget(lbl_date_filter)

        self.combo_date_preset = QComboBox()
        self.combo_date_preset.addItems(["All Dates", "This Month", "Last 30 Days", "Custom Range"])
        self.combo_date_preset.currentIndexChanged.connect(self.on_date_preset_changed)
        date_row.addWidget(self.combo_date_preset)

        self.lbl_from = QLabel("From:")
        self.lbl_from.setStyleSheet("font-size: 12px; color: #64748b;")
        date_row.addWidget(self.lbl_from)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setEnabled(False)
        self.date_from.dateChanged.connect(self.filter_ledger)
        date_row.addWidget(self.date_from)

        self.lbl_to = QLabel("To:")
        self.lbl_to.setStyleSheet("font-size: 12px; color: #64748b;")
        date_row.addWidget(self.lbl_to)

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("yyyy-MM-dd")
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setEnabled(False)
        self.date_to.dateChanged.connect(self.filter_ledger)
        date_row.addWidget(self.date_to)

        self.btn_clear_dates = QPushButton("Reset Filter")
        self.btn_clear_dates.clicked.connect(self.reset_filters)
        date_row.addWidget(self.btn_clear_dates)

        date_row.addStretch()
        filter_card_layout.addLayout(date_row)

        self.main_layout.addWidget(self.filter_card)

        # 3. Customer Profile & Recovery Summary Cards
        self.summary_frame = QFrame()
        self.summary_frame.setProperty("class", "CardWidget")
        add_shadow(self.summary_frame)
        summary_layout = QHBoxLayout(self.summary_frame)
        summary_layout.setContentsMargins(18, 14, 18, 14)
        summary_layout.setSpacing(18)

        # Left info block
        cust_info_layout = QVBoxLayout()
        cust_info_layout.setSpacing(4)
        self.lbl_cust_name = QLabel("Customer Name")
        self.lbl_cust_name.setStyleSheet("font-size: 20px; font-weight: bold; color: #0f172a;")
        self.lbl_cust_meta = QLabel("Area: - | City: - | Booker: -")
        self.lbl_cust_meta.setStyleSheet("font-size: 13px; color: #64748b;")
        self.lbl_opening = QLabel("Opening Balance: Rs. 0 (Date: -)")
        self.lbl_opening.setStyleSheet("font-size: 12px; color: #475569;")

        cust_info_layout.addWidget(self.lbl_cust_name)
        cust_info_layout.addWidget(self.lbl_cust_meta)
        cust_info_layout.addWidget(self.lbl_opening)
        summary_layout.addLayout(cust_info_layout, stretch=2)

        # Metric Blocks
        self.stat_bills = self._create_stat_widget("Total Bills", "Rs. 0", "#dc2626")
        summary_layout.addWidget(self.stat_bills)

        self.stat_recoveries = self._create_stat_widget("Total Recovered", "Rs. 0", "#059669")
        summary_layout.addWidget(self.stat_recoveries)

        self.stat_last_recovery = self._create_stat_widget("Last Recovery Date", "None", "#2563eb")
        summary_layout.addWidget(self.stat_last_recovery)

        self.stat_due = self._create_stat_widget("Current Balance Due", "Rs. 0", "#8b0000")
        summary_layout.addWidget(self.stat_due)

        self.main_layout.addWidget(self.summary_frame)

        # 4. Table Header Indicator
        table_top_layout = QHBoxLayout()
        self.lbl_table_heading = QLabel("Transaction History & Recovery Dates")
        self.lbl_table_heading.setStyleSheet("font-size: 15px; font-weight: 600; color: #1e293b;")
        table_top_layout.addWidget(self.lbl_table_heading)

        self.lbl_records_count = QLabel("0 transactions")
        self.lbl_records_count.setStyleSheet("font-size: 12px; color: #64748b;")
        table_top_layout.addStretch()
        table_top_layout.addWidget(self.lbl_records_count)
        self.main_layout.addLayout(table_top_layout)

        # 5. Ledger Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Date", "Type", "Booker", "Notes / Description", "Bill (+)", "Recovery (-)", "Running Balance"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(False)
        self.table.setColumnWidth(0, 115) # Date
        self.table.setColumnWidth(1, 110) # Type
        self.table.setColumnWidth(2, 135) # Booker
        self.table.setColumnWidth(3, 260) # Notes
        self.table.setColumnWidth(4, 130) # Bill
        self.table.setColumnWidth(5, 140) # Recovery
        self.table.setColumnWidth(6, 145) # Balance

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.main_layout.addWidget(self.table, stretch=1)

        # 6. Bottom Summary Bar
        self.bottom_bar = QFrame()
        self.bottom_bar.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; padding: 6px 14px;")
        bottom_layout = QHBoxLayout(self.bottom_bar)
        bottom_layout.setContentsMargins(10, 6, 10, 6)

        self.lbl_sum_bills = QLabel("Total Bills: Rs. 0")
        self.lbl_sum_bills.setStyleSheet("font-weight: 600; color: #dc2626; font-size: 13px;")
        bottom_layout.addWidget(self.lbl_sum_bills)

        bottom_layout.addSpacing(25)

        self.lbl_sum_recoveries = QLabel("Total Recoveries: Rs. 0")
        self.lbl_sum_recoveries.setStyleSheet("font-weight: 600; color: #059669; font-size: 13px;")
        bottom_layout.addWidget(self.lbl_sum_recoveries)

        bottom_layout.addStretch()

        self.lbl_closing_balance = QLabel("Closing Balance: Rs. 0")
        self.lbl_closing_balance.setStyleSheet("font-weight: bold; color: #1e293b; font-size: 14px;")
        bottom_layout.addWidget(self.lbl_closing_balance)

        self.main_layout.addWidget(self.bottom_bar)

    def _create_stat_widget(self, title, default_val, color):
        box = QFrame()
        box.setStyleSheet(f"background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 14px;")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        lbl_t = QLabel(title)
        lbl_t.setStyleSheet("font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase;")
        lbl_v = QLabel(default_val)
        lbl_v.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {color};")
        lbl_v.setObjectName("val")

        layout.addWidget(lbl_t)
        layout.addWidget(lbl_v)
        return box

    def _set_stat_val(self, stat_widget, text):
        lbl = stat_widget.findChild(QLabel, "val")
        if lbl:
            lbl.setText(text)

    def refresh_data(self):
        """Reload customer list and preserve current selection if any."""
        current_id = self.current_customer['id'] if self.current_customer else None

        self.customers_list = get_all_customers()

        self.combo_customers.blockSignals(True)
        self.combo_customers.clear()

        selected_idx = 0
        for idx, c in enumerate(self.customers_list):
            area = c.get('area') or 'General'
            display_text = f"{c['name']} ({area}) - Due: {format_currency(c.get('current_due', 0))}"
            self.combo_customers.addItem(display_text, c['id'])
            if current_id and c['id'] == current_id:
                selected_idx = idx

        self.combo_customers.blockSignals(False)

        # Set completer for fast typing
        completer = QCompleter([self.combo_customers.itemText(i) for i in range(self.combo_customers.count())], self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.combo_customers.setCompleter(completer)

        if self.customers_list:
            self.combo_customers.setCurrentIndex(selected_idx)
            self.load_customer(self.customers_list[selected_idx]['id'])
        else:
            self._clear_customer_view()

    def load_customer(self, customer_id: int):
        """Loads a specific customer into the ledger view."""
        customer = get_customer_by_id(customer_id)
        if not customer:
            return

        self.current_customer = customer

        # Ensure combobox matches
        self.combo_customers.blockSignals(True)
        for i in range(self.combo_customers.count()):
            if self.combo_customers.itemData(i) == customer_id:
                self.combo_customers.setCurrentIndex(i)
                break
        self.combo_customers.blockSignals(False)

        # Update customer profile card
        self.lbl_cust_name.setText(customer['name'])
        area = customer.get('area') or 'Unknown'
        city = customer.get('city') or 'Unknown'
        booker = customer.get('booker') or 'None'
        self.lbl_cust_meta.setText(f"Area: {area}  |  City: {city}  |  Assigned Booker: {booker}")

        op_date = customer.get('opening_date') or 'N/A'
        op_bal = customer.get('opening_balance', 0)
        self.lbl_opening.setText(f"Opening Balance: {format_currency(op_bal)} (Date: {op_date})")

        # Load all transactions for customer
        self.current_transactions = get_customer_transactions(customer_id)

        # Compute stats (total bills, total recoveries, last recovery date)
        tot_bills = sum(t['amount'] for t in self.current_transactions if t['type'] == 'Bill')
        recoveries = [t for t in self.current_transactions if t['type'] == 'Recovery']
        tot_recoveries = sum(t['amount'] for t in recoveries)

        last_recovery_str = "None"
        if recoveries:
            # Sort by date descending to find latest recovery
            rec_sorted = sorted(recoveries, key=lambda x: (x['transaction_date'], x['id']), reverse=True)
            latest_rec = rec_sorted[0]
            last_recovery_str = f"{latest_rec['transaction_date']} ({format_currency(latest_rec['amount'])})"

        due = customer.get('current_due', 0)

        self._set_stat_val(self.stat_bills, format_currency(tot_bills))
        self._set_stat_val(self.stat_recoveries, format_currency(tot_recoveries))
        self._set_stat_val(self.stat_last_recovery, last_recovery_str)
        self._set_stat_val(self.stat_due, format_currency(due))

        # Render filtered table
        self.filter_ledger()

    def _clear_customer_view(self):
        self.current_customer = None
        self.current_transactions = []
        self.lbl_cust_name.setText("No Customer Selected")
        self.lbl_cust_meta.setText("-")
        self.lbl_opening.setText("-")
        self._set_stat_val(self.stat_bills, "Rs. 0")
        self._set_stat_val(self.stat_recoveries, "Rs. 0")
        self._set_stat_val(self.stat_last_recovery, "None")
        self._set_stat_val(self.stat_due, "Rs. 0")
        self.table.setRowCount(0)

    def on_customer_changed(self, index):
        if index >= 0:
            cust_id = self.combo_customers.itemData(index)
            if cust_id:
                self.load_customer(cust_id)

    def prev_customer(self):
        cur = self.combo_customers.currentIndex()
        if cur > 0:
            self.combo_customers.setCurrentIndex(cur - 1)

    def next_customer(self):
        cur = self.combo_customers.currentIndex()
        if cur < self.combo_customers.count() - 1:
            self.combo_customers.setCurrentIndex(cur + 1)

    def on_date_preset_changed(self, index):
        preset = self.combo_date_preset.currentText()
        today = QDate.currentDate()

        if preset == "All Dates":
            self.date_from.setEnabled(False)
            self.date_to.setEnabled(False)
        elif preset == "This Month":
            self.date_from.setEnabled(False)
            self.date_to.setEnabled(False)
            first_of_month = QDate(today.year(), today.month(), 1)
            self.date_from.setDate(first_of_month)
            self.date_to.setDate(today)
        elif preset == "Last 30 Days":
            self.date_from.setEnabled(False)
            self.date_to.setEnabled(False)
            self.date_from.setDate(today.addDays(-30))
            self.date_to.setDate(today)
        elif preset == "Custom Range":
            self.date_from.setEnabled(True)
            self.date_to.setEnabled(True)

        self.filter_ledger()

    def reset_filters(self):
        self.combo_type_filter.setCurrentIndex(0)
        self.combo_date_preset.setCurrentIndex(0)
        self.filter_ledger()

    def filter_ledger(self):
        if not self.current_customer:
            return

        type_filter = self.combo_type_filter.currentData()
        preset = self.combo_date_preset.currentText()

        start_date_str = None
        end_date_str = None
        if preset in ("This Month", "Last 30 Days", "Custom Range"):
            start_date_str = self.date_from.date().toString("yyyy-MM-dd")
            end_date_str = self.date_to.date().toString("yyyy-MM-dd")

        opening_balance = self.current_customer.get('opening_balance', 0)
        opening_date = self.current_customer.get('opening_date') or '-'

        # Filter transactions
        filtered = []
        for tx in self.current_transactions:
            t_date = tx['transaction_date']
            t_type = tx['type']

            if type_filter != "All" and t_type != type_filter:
                continue

            if start_date_str and t_date < start_date_str:
                continue
            if end_date_str and t_date > end_date_str:
                continue

            filtered.append(tx)

        # Compute running balance up to each transaction
        # Note: Running balance always computes in chronological order
        balance = opening_balance
        tx_balances = {}
        for tx in self.current_transactions:
            if tx['type'] == 'Bill':
                balance += tx['amount']
            elif tx['type'] == 'Recovery':
                balance -= tx['amount']
            tx_balances[tx['id']] = balance

        # If filtered by recovery only, indicate clearly in table heading
        if type_filter == "Recovery":
            self.lbl_table_heading.setText("🟢 Customer Recoveries by Date (Payment In)")
        elif type_filter == "Bill":
            self.lbl_table_heading.setText("🔴 Customer Bills by Date (Sales Invoices)")
        else:
            self.lbl_table_heading.setText("Transaction History & Recovery Dates")

        # Populate table
        include_opening_row = (type_filter == "All") and (not start_date_str or opening_date >= start_date_str)
        total_rows = len(filtered) + (1 if include_opening_row else 0)
        self.table.setRowCount(total_rows)

        row_idx = 0
        if include_opening_row:
            self._set_opening_row(row_idx, opening_date, opening_balance)
            row_idx += 1

        sum_bills = 0
        sum_recoveries = 0

        for tx in filtered:
            # 0. Date
            date_item = QTableWidgetItem(tx['transaction_date'])
            date_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 0, date_item)

            # 1. Type with Badge
            type_text = tx['type']
            type_item = QTableWidgetItem(type_text)
            type_item.setTextAlignment(Qt.AlignCenter)
            if type_text == 'Recovery':
                type_item.setForeground(QColor('#059669')) # Emerald Green
                sum_recoveries += tx['amount']
            else:
                type_item.setForeground(QColor('#dc2626')) # Crimson Red
                sum_bills += tx['amount']
            self.table.setItem(row_idx, 1, type_item)

            # 2. Booker
            booker_item = QTableWidgetItem(tx.get('booker_name') or '-')
            self.table.setItem(row_idx, 2, booker_item)

            # 3. Notes
            notes_text = tx.get('notes') or ''
            notes_item = QTableWidgetItem(notes_text)
            self.table.setItem(row_idx, 3, notes_item)

            # 4. Bill Amount
            bill_str = format_currency(tx['amount']) if tx['type'] == 'Bill' else '-'
            bill_item = QTableWidgetItem(bill_str)
            bill_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if tx['type'] == 'Bill':
                bill_item.setForeground(QColor('#dc2626'))
            self.table.setItem(row_idx, 4, bill_item)

            # 5. Recovery Amount (Bold Green)
            rec_str = format_currency(tx['amount']) if tx['type'] == 'Recovery' else '-'
            rec_item = QTableWidgetItem(rec_str)
            rec_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if tx['type'] == 'Recovery':
                rec_item.setForeground(QColor('#059669'))
            self.table.setItem(row_idx, 5, rec_item)

            # 6. Running Balance
            run_bal = tx_balances.get(tx['id'], 0)
            bal_item = QTableWidgetItem(format_currency(run_bal))
            bal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            bal_item.setForeground(QColor('#1e293b'))
            self.table.setItem(row_idx, 6, bal_item)

            row_idx += 1

        self.lbl_records_count.setText(f"{len(filtered)} records shown")
        self.lbl_sum_bills.setText(f"Total Bills in View: {format_currency(sum_bills)}")
        self.lbl_sum_recoveries.setText(f"Total Recoveries in View: {format_currency(sum_recoveries)}")

        closing_bal = self.current_customer.get('current_due', 0)
        self.lbl_closing_balance.setText(f"Current Total Due: {format_currency(closing_bal)}")

    def _set_opening_row(self, row_idx, opening_date, opening_balance):
        d_item = QTableWidgetItem(opening_date if opening_date != '-' else 'Opening')
        d_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row_idx, 0, d_item)

        t_item = QTableWidgetItem("Opening Bal.")
        t_item.setTextAlignment(Qt.AlignCenter)
        t_item.setForeground(QColor('#2563eb'))
        self.table.setItem(row_idx, 1, t_item)

        b_item = QTableWidgetItem("-")
        self.table.setItem(row_idx, 2, b_item)

        n_item = QTableWidgetItem("Initial account opening balance")
        self.table.setItem(row_idx, 3, n_item)

        bill_item = QTableWidgetItem(format_currency(opening_balance) if opening_balance > 0 else '-')
        bill_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row_idx, 4, bill_item)

        rec_item = QTableWidgetItem("-")
        rec_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row_idx, 5, rec_item)

        bal_item = QTableWidgetItem(format_currency(opening_balance))
        bal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bal_item.setForeground(QColor('#1e293b'))
        self.table.setItem(row_idx, 6, bal_item)

    def export_statement_pdf(self):
        from views.components import ModernDialog
        from PySide6.QtWidgets import QFileDialog
        from services.report_service import generate_customer_ledger_pdf

        if not self.current_customer:
            ModernDialog("Notice", "Please select a customer first to export statement.", self).exec()
            return

        try:
            safe_name = "".join(c for c in self.current_customer.get('name', 'Customer') if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            default_name = f"Statement_{safe_name}_{timestamp}.pdf"
            default_path = os.path.join(get_documents_dir(), default_name)

            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Customer Statement PDF", default_path, "PDF Documents (*.pdf);;All Files (*)"
            )
            if not save_path:
                return

            filename = generate_customer_ledger_pdf(
                customer=self.current_customer,
                transactions=self.current_transactions,
                output_path=save_path
            )

            ModernDialog("Export Successful", f"Statement PDF saved successfully to:\n{filename}", self).exec()
            QDesktopServices.openUrl(QUrl.fromLocalFile(filename))
        except Exception as e:
            ModernDialog("Export Failed", f"Failed to generate statement PDF:\n{str(e)}", self, is_error=True).exec()
