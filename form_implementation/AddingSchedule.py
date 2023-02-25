from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from qtpy import uic


class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.add_w1()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.show()

    def the_back_button_was_clicked(self):
        self.del_w(self.layout().itemAt(0).widget())
        self.add_w1()

    def the_mirea_schedule_button_was_clicked(self):
        self.add_w2()

    def add_w2(self):
        w2 = uic.loadUi("forms\Form2.ui")
        closeButton = w2.findChild(QPushButton, "closeButton")
        backButton = w2.findChild(QPushButton, "backButton")
        backButton.clicked.connect(self.the_back_button_was_clicked)
        closeButton.clicked.connect(self.close)
        self.layout().replaceWidget(self.layout().itemAt(0).widget(), w2)

    def add_w1(self):
        w1 = uic.loadUi("forms\Form1.ui")
        closeButton = w1.findChild(QPushButton, "closeButton")
        addXMLButton = w1.findChild(QPushButton, "addXMLButton")
        addXMLButton.clicked.connect(self.the_mirea_schedule_button_was_clicked)
        closeButton.clicked.connect(self.close)
        self.layout().addWidget(w1)

    def del_w(self, l):
        l.deleteLater()
