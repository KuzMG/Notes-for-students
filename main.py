import sys

from PyQt6.QtWidgets import QApplication

from form_implementation import AddingSchedule
from schedule_parsing.Parsing import schedule_of_groups_docx


def main():
    # app = QApplication(sys.argv)
    # w = AddingSchedule.Widget()
    # app.exec()
    schedule_of_groups_docx()

if __name__ == '__main__': main()
