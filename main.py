import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow
from PyQt6 import uic
from sqlalchemy.orm import Session

from database.Table_db import Schedule, engine
from dto import DataClasses
from form_implementation import AddingSchedule, MainWindow

class MainWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        with Session(bind=engine) as db:
            if len(db.query(Schedule).all()) == 0:
               self.w1 = AddingSchedule.Widget(self.openHomeScreen)
            else:
                self.w2 = MainWindow.HomeScreen(self.openAddingSchedule)

    def openAddingSchedule(self):
        self.w2.close()
        self.w1 = AddingSchedule.Widget(self.openHomeScreen)

    def openHomeScreen(self):
        self.w1.close()
        self.w2 =  MainWindow.HomeScreen(self.openAddingSchedule)
def main():
    app = QApplication(sys.argv)
    w = MainWidget()
    app.exec()

if __name__ == '__main__': main()
