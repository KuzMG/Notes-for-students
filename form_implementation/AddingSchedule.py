import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QApplication
from qtpy import uic

from form_implementation import MireaSchedule


class Widget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("forms\Form1.ui", self)
        self.closeButton.clicked.connect(self.close)
        self.addXMLButton.clicked.connect(self.the_button_was_clicked)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.show()

    def the_button_was_clicked(self):
        #self.w = MireaSchedule.Widget()
        uic.loadUi("forms\Form2.ui", self)
        #self.close()
