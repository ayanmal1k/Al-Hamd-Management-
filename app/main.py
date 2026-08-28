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
    
    # Set App Icon
    icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.ico'))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Load stylesheet if it exists
    qss_path = os.path.join(os.path.dirname(__file__), 'styles.qss')
    if os.path.exists(qss_path):
        with open(qss_path, 'r') as f:
            app.setStyleSheet(f.read())
            
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
