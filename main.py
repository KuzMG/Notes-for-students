import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6 import uic

from form_implementation import AddingSchedule, MainWindow


def main():
    app = QApplication(sys.argv)
    #w = AddingSchedule.Widget()
    w = MainWindow.HomeScreen()
    # cell = QWidget()
    # vbox = QVBoxLayout()
    # vbox.setSpacing(0)
    # vbox.setContentsMargins(0, 0, 0, 0)
    # vbox.addWidget(uic.loadUi("forms\Form6.ui"))
    # vbox.addWidget(uic.loadUi("forms\Form6.ui"))
    # vbox.addStretch()
    # cell.setLayout(vbox)
    #cell.show()
    app.exec()
    # schedule_of_groups_docx()


if __name__ == '__main__': main()
