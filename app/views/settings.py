from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QFrame, QMessageBox, QListWidget)
from PySide6.QtCore import Qt
from services.backup_service import create_backup, get_available_backups, restore_backup
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
        
        self.lbl_available = QLabel("Available Backups:")
        self.lbl_available.setStyleSheet("font-weight: 500;")
        self.backup_layout.addWidget(self.lbl_available)
        
        self.backup_list = QListWidget()
        self.backup_layout.addWidget(self.backup_list)
        
        self.btn_restore = QPushButton(" Restore Selected Backup")
        self.btn_restore.setIcon(get_svg_icon(SVG_RESTORE, color="#1d1d1f"))
        self.btn_restore.setFixedWidth(200)
        self.btn_restore.clicked.connect(self.handle_restore_backup)
        self.backup_layout.addWidget(self.btn_restore)
        
        self.layout.addWidget(self.backup_card)
        self.layout.addStretch()
        
    def refresh_data(self):
        self.backup_list.clear()
        backups = get_available_backups()
        if backups:
            self.backup_list.addItems(backups)
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
        if not selected or selected.text() == "No backups available.":
            ModernDialog("Warning", "Please select a backup to restore.", self, is_error=True).exec()
            return
            
        filename = selected.text()
        
        reply = QMessageBox.question(self, "Confirm Restore", 
                                     f"Are you sure you want to restore from '{filename}'?\nThis will overwrite current data, but a pre-restore backup will be created.",
                                     QMessageBox.Yes | QMessageBox.No)
                                     
        if reply == QMessageBox.Yes:
            if restore_backup(filename):
                ModernDialog("Success", "Database restored successfully. Please restart the application.", self).exec()
            else:
                ModernDialog("Error", "Failed to restore backup.", self, is_error=True).exec()
