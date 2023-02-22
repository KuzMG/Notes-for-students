import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QPushButton
from qtpy import uic

from form_implementation import MireaSchedule

app = QApplication(sys.argv)
ui = uic.loadUi("forms\Form1.ui")
closeButton = ui.findChild(QPushButton, "closeButton")
mireaButton = ui.findChild(QPushButton, "addXMLButton")
manuallyButton = ui.findChild(QPushButton, "addManuallyButton")


def the_button_was_clicked():
    MireaSchedule.open_window()
    ui.close()


closeButton.clicked.connect(ui.close)
mireaButton.clicked.connect(the_button_was_clicked)


def open_window():
    ui.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    ui.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    ui.show()


def close_window():
    ui.close()
