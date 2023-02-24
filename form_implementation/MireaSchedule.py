
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget
from qtpy import uic

from form_implementation import AddingSchedule


class Widget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("forms\Form2.ui", self)
        self.closeButton.clicked.connect(self.the_closeButton_was_clicked)
        self.backButton.clicked.connect(self.the_backButton_was_clicked)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.show()

    def the_backButton_was_clicked(self):
        self.w = AddingSchedule.Widget()
        self.close()

    def the_closeButton_was_clicked(self):
        self.close()
