from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtCore import QByteArray, Qt
from PySide6.QtSvg import QSvgRenderer
import sys
from PySide6.QtWidgets import QApplication

app = QApplication(sys.argv)
svg = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"><circle cx="12" cy="12" r="10" fill="red"/></svg>'
renderer = QSvgRenderer(QByteArray(svg.encode('utf-8')))
print("Renderer valid:", renderer.isValid())
pixmap = QPixmap(24, 24)
pixmap.fill(Qt.transparent)
painter = QPainter(pixmap)
renderer.render(painter)
painter.end()
i = QIcon(pixmap)
print('Icon is null:', i.isNull())
