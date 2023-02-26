from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qtpy import uic
import schedule_parsing.parsing as parsing


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

    def add_w2(self):
        SecondWidget = WidgetMireaSchedule()
        SecondWidget.backButton.clicked.connect(self.the_back_button_was_clicked)
        SecondWidget.closeButton.clicked.connect(self.close)
        self.layout().replaceWidget(self.layout().itemAt(0).widget(), SecondWidget)

    def add_w1(self):
        MainWidget = WidgetScheduleSelect()
        MainWidget.addXMLButton.clicked.connect(self.the_add_xsl_button_was_clicked)
        MainWidget.closeButton.clicked.connect(self.close)
        self.layout().addWidget(MainWidget)

    def the_add_xsl_button_was_clicked(self):
        self.del_w(self.layout().itemAt(0).widget())
        self.add_w2()

    def del_w(self, w):
        w.deleteLater()


class WidgetMireaSchedule(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("forms\Form2.ui", self)
        schedule = parsing.get_schedule_xls()
        for qualif in schedule:
            self.comboBox.addItem(qualif.qualification)
        for inst in schedule[self.comboBox.currentIndex()].institutes:
            self.comboBox_2.addItem(inst.institute)
        for location in schedule[self.comboBox.currentIndex()].institutes[self.comboBox_2.currentIndex()].location:
            self.comboBox_3.addItem(location.location.lstrip())
        i = 1
        for course in schedule[self.comboBox.currentIndex()].institutes[self.comboBox_2.currentIndex()].location[
            self.comboBox_3.currentIndex()].courses:
            self.comboBox_4.addItem(str(i))
            i += 1
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.show()


class WidgetScheduleSelect(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("forms\Form1.ui", self)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.show()
