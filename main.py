import sys

from PyQt6.QtWidgets import QApplication
from AddingSchedule import open_window as openAddingSchedule


def main():
    app = QApplication(sys.argv)
    openAddingSchedule()
    app.exec()


if __name__ == '__main__': main()
