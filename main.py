import sys

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QPushButton

app = QApplication(sys.argv)

ui = uic.loadUi("Form1.ui")
closeButton = ui.findChild(QPushButton, "closeButton")
closeButton.clicked.connect(app.quit)

ui.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
ui.setWindowFlags(Qt.WindowType.FramelessWindowHint)

ui.show()
app.exec()
