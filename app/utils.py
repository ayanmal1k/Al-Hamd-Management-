from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

def format_currency(amount_in_paisa: int) -> str:
    """Formats an amount in paisa to PKR string (Rs. X,XXX)"""
    if amount_in_paisa == 0:
        return "NIL"
    amount_rs = amount_in_paisa / 100.0
    return f"Rs. {amount_rs:,.0f}"

def parse_currency(amount_str: str) -> int:
    """Parses a string amount to paisa integer"""
    # Remove 'Rs.', commas and spaces
    clean_str = amount_str.replace('Rs.', '').replace(',', '').strip()
    try:
        if clean_str.upper() == 'NIL' or not clean_str:
            return 0
        return int(float(clean_str) * 100)
    except ValueError:
        return 0

def add_shadow(widget):
    """Adds a subtle drop shadow to a widget for the Apple-inspired look."""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(15)
    shadow.setXOffset(0)
    shadow.setYOffset(2)
    shadow.setColor(QColor(0, 0, 0, 30))
    widget.setGraphicsEffect(shadow)
