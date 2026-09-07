import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QFrame, QMessageBox, QListWidget, QListWidgetItem, QFileDialog)
from PySide6.QtCore import Qt
from services.backup_service import create_backup, get_available_backups, restore_backup, get_backup_info
from views.components import ModernDialog

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(20)
        
        # Header Row
        self.header_layout = QHBoxLayout()
        self.title = QLabel("Settings")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.header_layout.addWidget(self.title)
        self.layout.addLayout(self.header_layout)
        
        # Backup Card
        self.backup_card = QFrame()
        self.backup_card.setProperty("class", "CardWidget")
        self.backup_layout = QVBoxLayout(self.backup_card)
        self.backup_layout.setSpacing(15)
        
        self.lbl_backup = QLabel("Database Backup & Restore")
        self.lbl_backup.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.backup_layout.addWidget(self.lbl_backup)
        
        from icons import get_svg_icon, SVG_BACKUP, SVG_RESTORE
        self.btn_backup = QPushButton(" Create Backup Now")
        self.btn_backup.setIcon(get_svg_icon(SVG_BACKUP, color="white"))
        self.btn_backup.setProperty("class", "primary")
        self.btn_backup.setFixedWidth(200)
        self.btn_backup.clicked.connect(self.handle_create_backup)
        self.backup_layout.addWidget(self.btn_backup)
        
        self.lbl_available = QLabel("Available Backups in System:")
        self.lbl_available.setStyleSheet("font-weight: 500;")
        self.backup_layout.addWidget(self.lbl_available)
        
        self.backup_list = QListWidget()
        self.backup_list.setMinimumHeight(180)
        self.backup_layout.addWidget(self.backup_list)
        
        self.restore_btn_layout = QHBoxLayout()
        self.restore_btn_layout.setSpacing(12)
        
        self.btn_restore = QPushButton(" Restore Selected Backup")
        self.btn_restore.setIcon(get_svg_icon(SVG_RESTORE, color="#1d1d1f"))
        self.btn_restore.setFixedWidth(220)
        self.btn_restore.clicked.connect(self.handle_restore_backup)
        self.restore_btn_layout.addWidget(self.btn_restore)
        
        self.btn_restore_file = QPushButton(" Restore from File... (Browse Disk)")
        self.btn_restore_file.setFixedWidth(260)
        self.btn_restore_file.clicked.connect(self.handle_restore_from_file)
        self.restore_btn_layout.addWidget(self.btn_restore_file)
        
        self.restore_btn_layout.addStretch()
        self.backup_layout.addLayout(self.restore_btn_layout)
        
        self.layout.addWidget(self.backup_card)
        self.layout.addStretch()
        
    def refresh_data(self):
        self.backup_list.clear()
        backups = get_available_backups()
        if backups:
            for b in backups:
                status_icon = "🟢" if b['customers'] > 0 else "⚪"
                display_text = f"{status_icon}  {b['filename']}   |   {b['size_kb']} KB   |   {b['customers']} Customers, {b['transactions']} Transactions"
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, b['path'])
                self.backup_list.addItem(item)
        else:
            self.backup_list.addItem("No backups available.")
            
    def handle_create_backup(self):
        if create_backup():
            ModernDialog("Success", "Backup created successfully!", self).exec()
            self.refresh_data()
        else:
            ModernDialog("Error", "Failed to create backup.", self, is_error=True).exec()
            
    def handle_restore_backup(self):
        selected = self.backup_list.currentItem()
        if not selected or not selected.data(Qt.UserRole):
            ModernDialog("Warning", "Please select a backup to restore.", self, is_error=True).exec()
            return
            
        backup_path = selected.data(Qt.UserRole)
        filename = os.path.basename(backup_path)
        
        reply = QMessageBox.question(self, "Confirm Restore", 
                                     f"Are you sure you want to restore from:\n'{filename}'?\n\nThis will overwrite current data, but a pre-restore backup will be created if valid data exists.",
                                     QMessageBox.Yes | QMessageBox.No)
                                     
        if reply == QMessageBox.Yes:
            success, msg = restore_backup(backup_path)
            if success:
                ModernDialog("Success", msg, self).exec()
                main_window = self.window()
                if hasattr(main_window, 'refresh_all_views'):
                    main_window.refresh_all_views()
                self.refresh_data()
            else:
                ModernDialog("Error", msg, self, is_error=True).exec()

    def handle_restore_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File to Restore", "", "SQLite Database (*.db);;All Files (*)"
        )
        if not file_path:
            return
            
        info = get_backup_info(file_path)
        if not info['valid']:
            ModernDialog("Error", "The selected file is not a valid SQLite database.", self, is_error=True).exec()
            return
            
        reply = QMessageBox.question(
            self, "Confirm File Restore",
            f"Are you sure you want to restore from external file:\n{file_path}\n\n"
            f"Contains: {info['customers']} Customers, {info['transactions']} Transactions ({info['size_kb']} KB).\n\n"
            f"This will replace your current database.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, msg = restore_backup(file_path)
            if success:
                ModernDialog("Success", msg, self).exec()
                main_window = self.window()
                if hasattr(main_window, 'refresh_all_views'):
                    main_window.refresh_all_views()
                self.refresh_data()
            else:
                ModernDialog("Error", msg, self, is_error=True).exec()

