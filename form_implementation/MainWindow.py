import typing

from PyQt6 import uic
from PyQt6.QtCore import Qt, QPropertyAnimation, QAbstractListModel, QModelIndex, QObject
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGridLayout, QGroupBox, QFrame
from PyQt6.uic.properties import QtGui
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from datetime import datetime, date, time, timedelta
from database.Table_db import engine, Schedule
from calendar import monthrange


class HomeScreen(QMainWindow):
    Month = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь",
             "Декабрь"]
    Week = ['ПН','ВТ','СР','ЧТ','ПТ','СБ','ВС']

    def __init__(self):
        super().__init__()
        self.lastDateCell = None
        self.nowCol = None
        self.nowRow = None
        self.lastCol = None
        self.lastRow = None
        self.lastCalendarDate = None
        uic.loadUi("forms\Form5.ui", self)
        self.parity = 0
        self.clickPosition = None
        self.moveMonth = 0
        self.date()
        self.closeButton.clicked.connect(self.close)
        self.collapseExpandButton.clicked.connect(self.collapse_expand_window)
        self.collapseButton.clicked.connect(self.showMinimized)
        self.sidePanelButton.clicked.connect(self.slideLeft)
        self.frame_11.mouseMoveEvent = self.moveWindow
        self.frame_11.mouseReleaseEvent = self.releaseButton
        self.lastMonthButton.clicked.connect(self.lastMonth)
        self.nextMonthButton.clicked.connect(self.nextMonth)
        self.changeParityButton.clicked.connect(self.changeParity)
        self.changeParityButton.setToolTip("изменить четность")
        for row in range(6):
            for column in range(7):
                self.newCellCalendar(row, column)

        self.pairVisualization(self.nowRow,
                               self.nowCol)
        self.showMaximized()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.show()

    def changeParity(self):
        if self.calendarDays[0] > 20:
            if self.calendarDate.month > 1:
                dictDate = date(self.calendarDate.year, self.calendarDate.month - 1, self.calendarDays[0])
            else:
                dictDate = date(self.calendarDate.year - 1, 12, self.calendarDays[0])
        else:
            dictDate = date(self.calendarDate.year, self.calendarDate.month, self.calendarDays[0])
        if self.lastCalendarDate.get(dictDate) == 0:
            self.parity = 1
        else:
            self.parity = 0
        self.lastCalendarDate.clear()
        for row in range(6):
            for column in range(7):
                self.setCellCalendar(row, column)
        for i in range(self.pairLayout.count()):
            self.pairLayout.removeWidget(self.pairLayout.itemAt(0).widget())
        self.weekDay.setText(F"{self.Week[self.lastCol]} {self.calendarDays[self.lastRow*7+self.lastCol]}")
        with Session(bind=engine) as db:
            schedule = db.query(Schedule).filter(Schedule.group == "БСБО-05-21").first()
            if self.lastCol < len(schedule.days_of_week):
                for pair in schedule.days_of_week[self.lastCol].pair_number:
                    cell = uic.loadUi("forms\Form6.ui")
                    cell.pairTime.setText(pair.date)
                    if pair.parity[self.parityOfWeek(self.lastRow * 7)].pair[0].discipline != '':
                        cell.discipline.setText(pair.parity[self.parityOfWeek(self.lastRow * 7)].pair[0].discipline)
                        cell.teacher.setText(pair.parity[self.parityOfWeek(self.lastRow * 7)].pair[0].name_of_the_teacher)
                        cell.occupation.setText(pair.parity[self.parityOfWeek(self.lastRow * 7)].pair[0].occupation)
                    else:
                        cell.discipline.setText("------------------")
                        cell.teacher.setText("----")
                        cell.widget_3.setStyleSheet("background-color: rgba(255, 255, 255,0);")
                        cell.occupation.setText("")
                    self.pairLayout.addWidget(cell)

    def nextMonth(self):
        self.moveMonth = 1
        self.date()
        for row in range(6):
            for column in range(7):
                self.setCellCalendar(row, column)

    def lastMonth(self):
        self.moveMonth = -1
        self.date()
        for row in range(6):
            for column in range(7):
                self.setCellCalendar(row, column)

    def date(self):
        if self.moveMonth == 0:
            self.calendarDate = date.today()
        elif self.moveMonth < 0:
            self.calendarDate = self.calendarDate + relativedelta(months=-1)
        elif self.moveMonth > 0:
            self.calendarDate = self.calendarDate + relativedelta(months=1)
        lastDate = self.calendarDate + relativedelta(months=-1)
        year = self.calendarDate.year
        month = self.calendarDate.month
        self.monthYear.setText(F"{self.Month[month - 1]} {year}")
        print(self.calendarDate)
        self.calendarDays = []
        days = monthrange(year, month)[1]
        lastDays = monthrange(lastDate.year, lastDate.month)[1]
        firstDay = datetime(year, month, 1).weekday()
        numDay = 0
        for i in range(42):
            if i < firstDay:
                self.calendarDays.append(lastDays - firstDay + 1 + i)
                continue
            if numDay != days:
                numDay += 1
                if numDay == date.today().day and self.calendarDate == date.today():
                    self.nowRow = i//7
                    self.nowCol = i%7
                self.calendarDays.append(numDay)
                continue
            else:
                numDay = 1
                self.calendarDays.append(numDay)

    def setCellCalendar(self, row, col):
        cell = self.gridLayout.itemAt(row * 7 + col).widget()
        cell.frame.setStyleSheet("""QFrame#frame{
                background-color: rgb(222, 222, 222);
                border: 0px solid rgb(255, 0, 0);
            }
            QListWidget#listWidget{
                background-color: rgb(222, 222, 222);
            }
            """)
        if self.calendarDate.year == date.today().year and self.calendarDate.month == date.today().month and self.nowCol ==col and self.nowRow == row:
            cell.frame.setStyleSheet("""QFrame#frame{
                                background-color: rgb(222, 222, 222);
                                border: 1px solid rgb(255, 0, 0);
                                }
                                QListWidget#listWidget{
                                        background-color: rgb(222, 222, 222);
                                    }
                                """)

        if self.lastDateCell.year == self.calendarDate.year and self.lastDateCell.month == self.calendarDate.month and self.lastDateCell.day == self.calendarDays[row*7+col] and self.lastRow == row and self.lastCol ==col:
            cell.frame.setStyleSheet("""QFrame#frame{
                                            background-color: rgb(222, 222, 222);
                                            border: 1px solid rgb(255, 0, 0);
                                            }
                                            QListWidget#listWidget{
                                                    background-color: rgb(222, 222, 222);
                                                }
                                            """)
        cell.label.setText(str(self.calendarDays[row * 7 + col]))
        cell.listWidget.clear()
        with Session(bind=engine) as db:
            schedule = db.query(Schedule).filter(Schedule.group == "БСБО-05-21").first()
            if col < len(schedule.days_of_week):
                for pair in schedule.days_of_week[col].pair_number:
                    if not pair.parity[self.parityOfWeek(row * 7)].pair[0].discipline == "":
                        cell.listWidget.addItem(pair.parity[self.parityOfWeek(row * 7)].pair[0].discipline)

    def newCellCalendar(self, row, col):
        cell = Cell(row,col,self.pairVisualization)

        cell.label.setText(str(self.calendarDays[row * 7 + col]))
        with Session(bind=engine) as db:
            schedule = db.query(Schedule).filter(Schedule.group == "БСБО-05-21").first()
            if col < len(schedule.days_of_week):
                for pair in schedule.days_of_week[col].pair_number:
                    if not pair.parity[self.parityOfWeek(row * 7)].pair[0].discipline == "":
                        cell.listWidget.addItem(pair.parity[self.parityOfWeek(row * 7)].pair[0].discipline)
        self.gridLayout.addWidget(cell, row, col)

    def pairVisualization(self,row,col):
        print(self.lastDateCell,date(self.calendarDate.year,self.calendarDate.month, self.calendarDays[row*7+col]))
        if self.lastDateCell is not None and (self.lastDateCell!= date(self.calendarDate.year,self.calendarDate.month, self.calendarDays[row*7+col]) and (row != self.lastRow or col != self.lastCol)):
            SelectCell = self.gridLayout.itemAtPosition(self.lastRow,self.lastCol).widget()
            SelectCell.frame.setStyleSheet("""QFrame#frame{
                background-color: rgb(222, 222, 222);
                border: 0px solid rgb(255, 0, 0);
            }
            QListWidget#listWidget{
                background-color: rgb(222, 222, 222);
            }
            """)
        else:
            SelectCell = self.gridLayout.itemAtPosition(row, col).widget()
            SelectCell.frame.setStyleSheet("""QFrame#frame{
                    background-color: rgb(222, 222, 222);
                    border: 1px solid rgb(255, 0, 0);
                    }
                    QListWidget#listWidget{
                            background-color: rgb(222, 222, 222);
                        }
                    """)
        if self.calendarDate.year == date.today().year and self.calendarDate.month == date.today().month:
            SelectCell = self.gridLayout.itemAtPosition(self.nowRow, self.nowCol).widget()
            SelectCell.frame.setStyleSheet("""QFrame#frame{
                                background-color: rgb(222, 222, 222);
                                border: 1px solid rgb(255, 0, 0);
                                }
                                QListWidget#listWidget{
                                        background-color: rgb(222, 222, 222);
                                    }
                                """)

        for i in range(self.pairLayout.count()):
            self.pairLayout.removeWidget(self.pairLayout.itemAt(0).widget())
        self.weekDay.setText(F"{self.Week[col]} {self.calendarDays[row*7+col]}")
        with Session(bind=engine) as db:
            schedule = db.query(Schedule).filter(Schedule.group == "БСБО-05-21").first()
            if col < len(schedule.days_of_week):
                for pair in schedule.days_of_week[col].pair_number:
                    cell = uic.loadUi("forms\Form6.ui")
                    cell.pairTime.setText(pair.date)
                    if pair.parity[self.parityOfWeek(row * 7)].pair[0].discipline != '':
                        cell.discipline.setText(pair.parity[self.parityOfWeek(row * 7)].pair[0].discipline)
                        cell.teacher.setText(pair.parity[self.parityOfWeek(row * 7)].pair[0].name_of_the_teacher)
                        cell.occupation.setText(pair.parity[self.parityOfWeek(row * 7)].pair[0].occupation)
                    else:
                        cell.discipline.setText("------------------")
                        cell.teacher.setText("----")
                        cell.widget_3.setStyleSheet("background-color: rgba(255, 255, 255,0);")
                        cell.occupation.setText("")
                    self.pairLayout.addWidget(cell)
        self.lastDateCell = date(self.calendarDate.year,self.calendarDate.month, self.calendarDays[row*7+col])
        self.lastRow = row
        self.lastCol = col

    def parityOfWeek(self, row):
        if row < 7 and self.calendarDays[row] > 20:
            if self.calendarDate.month > 1:
                dictDate = date(self.calendarDate.year, self.calendarDate.month - 1, self.calendarDays[row])
            else:
                dictDate = date(self.calendarDate.year - 1, 12, self.calendarDays[row])
        elif row > 28 and self.calendarDays[row] < 20:
            if self.calendarDate.month < 12:
                dictDate = date(self.calendarDate.year, self.calendarDate.month + 1, self.calendarDays[row])
            else:
                dictDate = date(self.calendarDate.year + 1, 1, self.calendarDays[row])
        else:
            dictDate = date(self.calendarDate.year, self.calendarDate.month, self.calendarDays[row])
        if self.lastCalendarDate is None or len(self.lastCalendarDate)==0:
            self.lastCalendarDate = {dictDate: self.parity}
            return self.parity
        else:
            if self.lastCalendarDate.get(dictDate) is None:
                if self.lastCalendarDate.get(list(self.lastCalendarDate)[-1]) == 0:
                    self.parity = 1
                else:
                    self.parity = 0
                self.lastCalendarDate.update(
                    {dictDate: self.parity})

                return self.parity
            else:
                return self.lastCalendarDate.get(dictDate)

    def releaseButton(self, e):
        if not self.isMaximized() and e.button() == Qt.MouseButton.LeftButton and e.globalPosition().toPoint().y() == 0:
            self.showMaximized()
            self.centralwidget.setStyleSheet('background-color: rgba(255, 255, 255,255);')

    def slideLeft(self):
        width = self.frame_3.width()
        if width == 0:
            newWidth = 300
        else:
            newWidth = 0
        self.animation = QPropertyAnimation(self.frame_3, b'minimumWidth')
        self.animation.setDuration(200)
        self.animation.setStartValue(width)
        self.animation.setEndValue(newWidth)
        self.animation.start()

    def moveWindow(self, e):
        if not self.isMaximized():
            if e.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() - self.clickPosition + e.globalPosition().toPoint())
                # self.pos() + e.globalPosition().toPoint() - self.clickPosition
                self.clickPosition = e.globalPosition().toPoint()
                e.accept()
                if e.globalPosition().toPoint().y() == 0:
                    # print(e.globalPosition().toPoint().y())
                    self.centralwidget.setStyleSheet('background-color: rgba(255, 255, 255,80);')
                else:
                    self.centralwidget.setStyleSheet('background-color: rgba(255, 255, 255,255);')
        else:
            if e.buttons() == Qt.MouseButton.LeftButton:
                w1 = self.width()
                self.showNormal()
                w2 = self.width()
                self.move(e.globalPosition().toPoint() - self.clickPosition * (w2 / w1))

    def mousePressEvent(self, event):
        # print(self.grabMouse())
        self.clickPosition = event.globalPosition().toPoint()

    def collapse_expand_window(self):
        if self.isMaximized():
            self.showNormal()
            self.collapseExpandButton.setText("")
        else:
            self.collapseExpandButton.setText("")
            self.showMaximized()

class Cell(QWidget):
    def __init__(self,row,col,select):
        super().__init__()
        self.select = select
        self.row = row
        self.col = col
        uic.loadUi("forms\Form7.ui", self)
        self.listWidget.mousePressEvent = self.mousePressEvent

    def mousePressEvent(self, event):
        self.frame.setStyleSheet("""QFrame#frame{
        background-color: rgb(222, 222, 222);
        border: 1px solid rgb(255, 0, 0);
        }
        QListWidget#listWidget{
                background-color: rgb(222, 222, 222);
            }
        """)
        self.select(self.row,self.col)