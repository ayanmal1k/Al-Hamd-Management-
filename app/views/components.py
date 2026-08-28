from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QStackedWidget, QGraphicsOpacityEffect)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from icons import get_svg_icon, SVG_CHECK

class ModernDialog(QDialog):
    def __init__(self, title, message, parent=None, is_error=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(350)
        self.setup_ui(title, message, is_error)
        
    def setup_ui(self, title, message, is_error):
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 12px;
            }
            QLabel#title {
                font-size: 18px;
                font-weight: bold;
                color: #1d1d1f;
            }
            QLabel#message {
                font-size: 14px;
                color: #515154;
            }
            QPushButton {
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton.primary {
                background-color: #8b0000;
                color: white;
                border: none;
            }
            QPushButton.primary:hover {
                background-color: #6b0000;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        lbl_title = QLabel(title)
        lbl_title.setObjectName("title")
        if is_error:
            lbl_title.setStyleSheet("color: #8b0000;")
        layout.addWidget(lbl_title)
        
        lbl_message = QLabel(message)
        lbl_message.setObjectName("message")
        lbl_message.setWordWrap(True)
        layout.addWidget(lbl_message)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_ok = QPushButton("OK")
        btn_ok.setProperty("class", "primary")
        btn_ok.clicked.connect(self.accept)
        btn_layout.addWidget(btn_ok)
        
        layout.addLayout(btn_layout)


class FadingStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fade_duration = 200
        
    def setCurrentIndex(self, index):
        if index == self.currentIndex():
            return
            
        current_widget = self.currentWidget()
        if current_widget:
            # Create opacity effect for the current widget
            self.effect = QGraphicsOpacityEffect(current_widget)
            current_widget.setGraphicsEffect(self.effect)
            
            # Fade out
            self.anim_out = QPropertyAnimation(self.effect, b"opacity")
            self.anim_out.setDuration(self.fade_duration)
            self.anim_out.setStartValue(1.0)
            self.anim_out.setEndValue(0.0)
            self.anim_out.setEasingCurve(QEasingCurve.InOutQuad)
            
            # When fade out finishes, change index and fade in
            self.anim_out.finished.connect(lambda: self._on_fade_out_finished(index))
            self.anim_out.start()
        else:
            super().setCurrentIndex(index)
            
    def _on_fade_out_finished(self, index):
        current_widget = self.currentWidget()
        if current_widget:
            current_widget.setGraphicsEffect(None)
            
        super().setCurrentIndex(index)
        
        new_widget = self.currentWidget()
        if new_widget:
            self.effect_in = QGraphicsOpacityEffect(new_widget)
            new_widget.setGraphicsEffect(self.effect_in)
            
            self.anim_in = QPropertyAnimation(self.effect_in, b"opacity")
            self.anim_in.setDuration(self.fade_duration)
            self.anim_in.setStartValue(0.0)
            self.anim_in.setEndValue(1.0)
            self.anim_in.setEasingCurve(QEasingCurve.InOutQuad)
            
            # Clean up effect after fade in
            self.anim_in.finished.connect(lambda: new_widget.setGraphicsEffect(None))
            self.anim_in.start()
