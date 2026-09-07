import sys
import os
from views.main_window import MainWindow
from database import init_db

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    # Ensure database is initialized before starting
    init_db()
    
    app = QApplication(sys.argv)
    
    from paths import get_asset_path, get_resource_path
    
    # Set App Icon
    icon_path = get_asset_path('icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Load stylesheet if it exists
    qss_path = get_resource_path('styles.qss')
    if os.path.exists(qss_path):
        with open(qss_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
            
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
