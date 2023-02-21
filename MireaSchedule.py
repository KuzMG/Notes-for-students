import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QPushButton
from qtpy import uic

import AddingSchedule
from AddingSchedule import *

app = QApplication(sys.argv)
ui = uic.loadUi("Form2.ui")
closeButton = ui.findChild(QPushButton, "closeButton")


def the_button_was_clicked():
    AddingSchedule.open_window()
    ui.close()


closeButton.clicked.connect(the_button_was_clicked)


def open_window():
    ui.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    ui.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    ui.show()


def close_window():
    ui.close()
