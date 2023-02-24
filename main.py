import sys

from PyQt6.QtWidgets import QApplication

from form_implementation import AddingSchedule


def main():
    app = QApplication(sys.argv)
    w = AddingSchedule.Widget()
    app.exec()


if __name__ == '__main__': main()
