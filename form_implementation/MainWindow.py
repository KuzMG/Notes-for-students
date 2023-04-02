import typing

from PyQt6 import uic
from PyQt6.QtCore import Qt, QPropertyAnimation, QAbstractListModel, QModelIndex, QObject
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGridLayout, QGroupBox, QFrame, QListWidgetItem
from PyQt6.uic.properties import QtGui
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from datetime import datetime, date, time, timedelta
from database.Table_db import engine, Schedule, Pair
from calendar import monthrange

from form_implementation import AddingSchedule


class HomeScreen(QMainWindow):
    # group = 'Направление 48.03.01 Теология'  # "Направление 48.03.01 Теология"
    Month = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь",
             "Декабрь"]
    Week = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']

    def __init__(self, openAddingSchedule):
        super().__init__()
        self.openAddingSchedule = openAddingSchedule
        self.lastDateCell = None
        self.nowCol = None
        self.nowRow = None
        self.lastCol = None
        self.lastRow = None
        self.lastCalendarDate = None
        uic.loadUi("forms\Form5.ui", self)
        with Session(bind=engine) as db:
            self.group = db.query(Schedule.group).first()[0]
            self.StartParity = db.query(Schedule.num_parity).first()[0]

        self.parity = self.StartParity
        self.clickPosition = None
        self.moveMonth = 0
        self.date()
        self.closeButton.clicked.connect(self.close)
        self.collapseButton.clicked.connect(self.showMinimized)
        self.sidePanelButton.clicked.connect(self.slideLeft)
        self.lastMonthButton.clicked.connect(self.lastMonth)
        self.nextMonthButton.clicked.connect(self.nextMonth)
        self.changeParityButton.clicked.connect(self.changeParity)
        self.changeParityButton.setToolTip("изменить четность")
        self.save.clicked.connect(self.saveChange)
        self.listPair.itemClicked.connect(self.list_widget_was_clicked)
        self.addListPair()
        for row in range(6):
            for column in range(7):
                self.newCellCalendar(row, column)
        self.pairVisualization(self.nowRow,
                               self.nowCol)
        self.addListGroup()
        self.showMaximized()
        self.widget_3.setMaximumWidth(self.screen().geometry().width() // 2)
        self.frame_9.setMaximumWidth(self.screen().geometry().width() // 4)
        self.frame_9.setMinimumWidth(self.screen().geometry().width() // 4)
        self.widget_9.setMaximumWidth(self.screen().geometry().width() // 4)
        self.widget_9.setMinimumWidth(self.screen().geometry().width() // 4)
        self.widget_4.layout().setContentsMargins(0, self.widget_4.height() // 2 - self.frame_9.height() // 2, 0, 0)
        self.widget_4.setMinimumHeight(self.widget_7.height() // 2)
        self.widget_9.setVisible(False)
        self.addGroup.clicked.connect(self.add_group_was_clicked)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.show()

    def add_group_was_clicked(self):
        self.openAddingSchedule()

    def list_widget_was_clicked(self, item):
        self.infoPairVisualization(item.text())

    def addListPair(self):
        self.listPair.clear()
        set_ = set()
        with Session(bind=engine) as db:
            schedule = db.query(Schedule).filter(Schedule.group == self.group).first()
            for day in schedule.days_of_week:
                for pair in day.pair_number:
                    for p in pair.parity:
                        if p.pair[0].discipline != '':
                            set_.add(p.pair[0].discipline)
        for i in set_:
            self.listPair.addItem(i)

    def addListGroup(self):
        for i in range(self.listGroup.count()):
            self.listGroup.removeWidget(self.listGroup.itemAt(0).widget())
        with Session(bind=engine) as db:
            groups = db.query(Schedule.group).all()
            for group in groups:
                w = Group(group[0], self.deleteGroup, self.selectGroup)
                if group[0] == self.group:
                    w.widget.setStyleSheet("""QWidget#widget{
                    background-color: rgb(234, 234, 234);
                    }""")
                self.listGroup.addWidget(w)

    def selectGroup(self, groupName):
        self.group = groupName
        self.addListPair()
        for row in range(6):
            for column in range(7):
                self.setCellCalendar(row, column)
        self.pairVisualization(self.nowRow,
                               self.nowCol)
        self.addListGroup()

    def deleteGroup(self, groupName):
        with Session(bind=engine) as db:
            groupsDB = db.query(Schedule).all()
            if len(groupsDB) == 1:
                db.delete(groupsDB[0])
                db.commit()
                self.openAddingSchedule()
            else:
                for groupDB in groupsDB:
                    if groupDB.group == groupName:
                        db.delete(groupDB)
                        db.commit()
                        self.addListGroup()
                    if self.group == groupName:
                        self.group = groupDB.group
                        self.addListPair()
                        for row in range(6):
                            for column in range(7):
                                self.setCellCalendar(row, column)
                        self.pairVisualization(self.nowRow,
                                               self.nowCol)
                        self.addListGroup()

    def saveChange(self):
        with Session(bind=engine) as db:
            for i in range(self.infoOccupLayout.count()):
                w = self.infoOccupLayout.itemAt(i).widget()
                pair = db.query(Pair).filter(
                    Pair.discipline == self.pairName.text(), Pair.occupation == w.occup.text()).all()
                for p in pair:
                    p.visibility = w.checkBox.isChecked()
                    p.name_of_the_teacher_notes = w.notes.text()
                    p.discipline_notes = self.notes.text()
            db.commit()
        for row in range(6):
            for column in range(7):
                self.setCellCalendar(row, column)
        self.pairVisualization(self.lastRow, self.lastCol)

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
        self.weekDay.setText(F"{self.Week[self.lastCol]} {self.calendarDays[self.lastRow * 7 + self.lastCol]}")
        with Session(bind=engine) as db:
            schedule = db.query(Schedule).filter(Schedule.group == self.group).first()
            if self.StartParity == 0:
                schedule.num_parity = 1
            else:
                schedule.num_parity = 0
            db.commit()
            if self.lastCol < len(schedule.days_of_week):
                for pair in schedule.days_of_week[self.lastCol].pair_number:
                    cell = uic.loadUi("forms\Form6.ui")
                    cell.pairTime.setText(pair.date.replace("-", "\n"))
                    if pair.parity[self.parityOfWeek(self.lastRow * 7)].pair[0].discipline != '':
                        cell.discipline.setText(pair.parity[self.parityOfWeek(self.lastRow * 7)].pair[0].discipline)
                        cell.teacher.setText(
                            pair.parity[self.parityOfWeek(self.lastRow * 7)].pair[0].name_of_the_teacher)
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
                    self.nowRow = i // 7
                    self.nowCol = i % 7
                self.calendarDays.append(numDay)
                continue
            else:
                numDay = 1
                self.calendarDays.append(numDay)

    def setCellCalendar(self, row, col):
        cell = self.gridLayout.itemAt(row * 7 + col).widget()
        cell.frame.setStyleSheet("""QFrame#frame{
                background-color: rgb(234, 234, 234);
                border: 0px solid rgb(255, 0, 0);
            }
            QListWidget#listWidget{
                background-color: rgb(234, 234, 234);
            }
            """)
        if self.lastDateCell.year == self.calendarDate.year and self.lastDateCell.month == self.calendarDate.month and self.lastDateCell.day == \
                self.calendarDays[row * 7 + col] and self.lastRow == row and self.lastCol == col:
            cell.frame.setStyleSheet("""QFrame#frame{
                                             background-color: rgb(234, 234, 234);
                                             border: 1px solid rgb(255, 0, 0);
                                             padding: -1px;
                                             }
                                             QListWidget#listWidget{
                                                     background-color: rgb(234, 234, 234);
                                                 }
                                             """)
        if self.calendarDate.year == date.today().year and self.calendarDate.month == date.today().month and self.nowCol == col and self.nowRow == row:
            cell.frame.setStyleSheet("""QFrame#frame{
                                background-color: rgba(255, 144, 144);
                                border: 1px solid rgb(255, 0, 0);
                                padding: -1px;
                                }
                                QListWidget#listWidget{
                                        background-color: rgba(255, 144, 144);
                                    }
                                """)

        cell.label.setText(str(self.calendarDays[row * 7 + col]))
        cell.listWidget.clear()
        with Session(bind=engine) as db:
            schedule = db.query(Schedule).filter(Schedule.group == self.group).first()
            if col < len(schedule.days_of_week):
                for pair in schedule.days_of_week[col].pair_number:
                    if pair.parity[self.parityOfWeek(row * 7)].pair[0].discipline != "" and \
                            pair.parity[self.parityOfWeek(row * 7)].pair[0].visibility:
                        cell.listWidget.addItem(pair.parity[self.parityOfWeek(row * 7)].pair[0].discipline)

    def newCellCalendar(self, row, col):
        cell = Cell(row, col, self.pairVisualization)
        cell.setMaximumSize(self.screen().geometry().width() // 15, self.screen().geometry().width() // 15)
        cell.setMinimumSize(self.screen().geometry().width() // 15, self.screen().geometry().width() // 15)
        cell.label.setText(str(self.calendarDays[row * 7 + col]))
        with Session(bind=engine) as db:
            schedule = db.query(Schedule).filter(Schedule.group == self.group).first()
            if col < len(schedule.days_of_week):
                for pair in schedule.days_of_week[col].pair_number:
                    if pair.parity[self.parityOfWeek(row * 7)].pair[0].discipline != "" and \
                            pair.parity[self.parityOfWeek(row * 7)].pair[0].visibility:
                        item = QListWidgetItem(pair.parity[self.parityOfWeek(row * 7)].pair[0].discipline)
                        cell.listWidget.addItem(item)
        self.gridLayout.addWidget(cell, row, col)

    def infoPairVisualization(self, discipline_):

        if discipline_ == "":
            return
        self.widget_9.setVisible(True)
        for i in range(self.infoOccupLayout.count()):
            self.infoOccupLayout.removeWidget(self.infoOccupLayout.itemAt(0).widget())
        self.pairName.setText(discipline_)
        with Session(bind=engine) as db:
            pair = db.query(Pair.occupation, Pair.name_of_the_teacher, Pair.discipline_notes,
                            Pair.name_of_the_teacher_notes, Pair.visibility).filter(
                Pair.discipline == discipline_).group_by(Pair.occupation, Pair.name_of_the_teacher,
                                                         Pair.discipline_notes, Pair.name_of_the_teacher_notes,
                                                         Pair.visibility).all()
            self.notes.setText(pair[0][2])
            for line in pair:
                if line[1] != '':
                    w = uic.loadUi("forms\Form8.ui")
                    if line[0] == "ПР":
                        w.widget.setStyleSheet("""#widget{
                        background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(85, 85, 255,255), stop:1 rgba(255, 255, 255, 0));
                        border-top-left-radius: 5px;
                        border-bottom-left-radius: 5px;
                        }""")
                    elif line[0] == "ЛК":
                        w.widget.setStyleSheet("""#widget{
                        background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(170, 85, 127, 255), stop:1 rgba(255, 255, 255, 0));
                        border-top-left-radius: 5px;
                        border-bottom-left-radius: 5px;
                        }""")
                    else:
                        w.widget.setStyleSheet("""#widget{
                        background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(255, 0, 255, 255), stop:1 rgba(255, 255, 255, 0));
                        border-top-left-radius: 5px;
                        border-bottom-left-radius: 5px;
                        }""")

                    w.checkBox.setChecked(line[4])
                    w.occup.setText(line[0])
                    w.teacher.setText(line[1])
                    w.notes.setText(line[3])
                    self.infoOccupLayout.addWidget(w)

    def pairVisualization(self, row, col):
        if row * 7 + col < 7 and self.calendarDays[row * 7 + col] > 20:
            if self.calendarDate.month == 1:
                selectDate = date(self.calendarDate.year - 1, 12, self.calendarDays[row * 7 + col])
            else:
                selectDate = date(self.calendarDate.year, self.calendarDate.month - 1, self.calendarDays[row * 7 + col])
        elif row * 7 + col > 27 and self.calendarDays[row * 7 + col] < 20:
            if self.calendarDate.month == 12:
                selectDate = date(self.calendarDate.year + 1, 1, self.calendarDays[row * 7 + col])
            else:
                selectDate = date(self.calendarDate.year, self.calendarDate.month + 1, self.calendarDays[row * 7 + col])
        else:
            selectDate = date(self.calendarDate.year, self.calendarDate.month, self.calendarDays[row * 7 + col])
        if self.lastDateCell is not None and (self.lastDateCell != selectDate and (
                row != self.lastRow or col != self.lastCol)):
            SelectCell = self.gridLayout.itemAtPosition(self.lastRow, self.lastCol).widget()
            SelectCell.frame.setStyleSheet("""QFrame#frame{
                background-color: rgb(234, 234, 234);
                border: 0px solid rgb(255, 0, 0);
            }
            QListWidget#listWidget{
                background-color: rgb(234, 234, 234);
            }
            """)
        else:
            SelectCell = self.gridLayout.itemAtPosition(row, col).widget()
            SelectCell.frame.setStyleSheet("""QFrame#frame{
                    background-color: rgb(234, 234, 234);
                    border: 1px solid rgb(255, 0, 0);
                    padding: -1px;
                    }
                    QListWidget#listWidget{
                            background-color: rgb(234, 234, 234);
                        }
                    """)
        if self.calendarDate.year == date.today().year and self.calendarDate.month == date.today().month:
            SelectCell = self.gridLayout.itemAtPosition(self.nowRow, self.nowCol).widget()
            SelectCell.frame.setStyleSheet("""QFrame#frame{
                                background-color: rgba(255, 144, 144);
                                border: 1px solid rgb(255, 0, 0);
                                padding: -1px;
                                }
                                QListWidget#listWidget{
                                        background-color: rgba(255, 144, 144);
                                    }
                                """)

        for i in range(self.pairLayout.count()):
            self.pairLayout.removeWidget(self.pairLayout.itemAt(0).widget())
        self.weekDay.setText(F"{self.Week[col]} {self.calendarDays[row * 7 + col]}")
        with Session(bind=engine) as db:
            schedule = db.query(Schedule).filter(Schedule.group == self.group).first()
            if col < len(schedule.days_of_week):
                for pair in schedule.days_of_week[col].pair_number:
                    cell = Line(pair.parity[self.parityOfWeek(row * 7)].pair[0].discipline, self.infoPairVisualization)
                    cell.pairTime.setText(pair.date.replace("-", "\n"))
                    if pair.parity[self.parityOfWeek(row * 7)].pair[0].discipline != '':
                        if not pair.parity[self.parityOfWeek(row * 7)].pair[0].visibility:
                            cell.frame.setStyleSheet("""QFrame#frame{
                                                background-color: rgba(255, 170, 127, 100);
                                                border-radius: 20px;
                                                }""")
                        else:
                            cell.frame.setStyleSheet("""QFrame#frame{
                                                background-color: rgb(255, 170, 0);
                                                border-radius: 20px;
                                                }""")
                        cell.discipline.setText(pair.parity[self.parityOfWeek(row * 7)].pair[0].discipline)
                        cell.teacher.setText(pair.parity[self.parityOfWeek(row * 7)].pair[0].name_of_the_teacher)
                        if pair.parity[self.parityOfWeek(row * 7)].pair[0].occupation == "ЛК":

                            cell.widget_3.setStyleSheet("""QWidget#widget_3
                            {
                            border-bottom-left-radius: 15px;
                            border-top-right-radius: 15px;
                            background-color: rgb(170, 85, 127);
                            }""")
                        elif pair.parity[self.parityOfWeek(row * 7)].pair[0].occupation == "ПР":
                            cell.widget_3.setStyleSheet("""QWidget#widget_3
                            {
                            border-bottom-left-radius: 15px;
                            border-top-right-radius: 15px;
                            background-color: rgb(85, 85, 255);
                            }""")
                        elif pair.parity[self.parityOfWeek(row * 7)].pair[0].occupation != "":
                            cell.widget_3.setStyleSheet("""QWidget#widget_3
                                                        {
                                                        border-bottom-left-radius: 15px;
                                                        border-top-right-radius: 15px;
                                                        background-color: rgb(255, 85, 85);
                                                        }""")
                        else:
                            cell.widget_3.setStyleSheet("""QWidget#widget_3
                                                                                    {
                                                                                    background-color: rgba(255, 0, 255,0);
                                                                                    }""")
                        cell.occupation.setText(pair.parity[self.parityOfWeek(row * 7)].pair[0].occupation)
                    else:
                        cell.discipline.setText("------------------")
                        cell.teacher.setText("----")
                        cell.widget_3.setStyleSheet("background-color: rgba(255, 255, 255,0);")
                        cell.occupation.setText("")
                    self.pairLayout.addWidget(cell)
            else:
                for i in range(len(schedule.days_of_week[0].pair_number)):
                    cell = uic.loadUi("forms\Form6.ui")
                    cell.pairTime.setText(schedule.days_of_week[0].pair_number[i].date.replace("-", "\n"))
                    cell.discipline.setText("------------------")
                    cell.teacher.setText("----")
                    cell.widget_3.setStyleSheet("background-color: rgba(255, 255, 255,0);")
                    cell.occupation.setText("")
                    self.pairLayout.addWidget(cell)
        self.lastDateCell = selectDate
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
        if self.lastCalendarDate is None or len(self.lastCalendarDate) == 0:
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

    def slideLeft(self):
        width = self.widget_18.width()
        if width == 0:
            # self.frame_3.setMinimumWidth(300)
            newWidth = 300
        else:
            newWidth = 0
        self.animation = QPropertyAnimation(self.widget_18, b'minimumWidth')
        self.animation.setDuration(200)
        self.animation.setStartValue(width)
        self.animation.setEndValue(newWidth)
        self.animation.start()


class Group(QWidget):
    def __init__(self, group, delete, select):
        super().__init__()
        self.delete = delete
        self.group = group
        self.select = select
        uic.loadUi("forms\Form9.ui", self)
        self.label.setText(self.group)
        self.deleteButton.clicked.connect(self.deleteGroup)
        self.addButton.clicked.connect(self.selectGroup)

    def deleteGroup(self):
        self.delete(self.group)

    def selectGroup(self):
        self.select(self.group)


class Cell(QWidget):
    def __init__(self, row, col, select):
        super().__init__()
        self.select = select
        self.row = row
        self.col = col
        uic.loadUi("forms\Form7.ui", self)
        self.listWidget.mousePressEvent = self.mousePressEvent

    def mousePressEvent(self, event):
        self.frame.setStyleSheet("""QFrame#frame{
        background-color: rgb(234, 234, 234);
        border: 1px solid rgb(255, 0, 0);
        padding: -1px;
        }
        QListWidget#listWidget{
                background-color: rgb(234, 234, 234);
            }
        """)
        self.select(self.row, self.col)


class Line(QWidget):
    def __init__(self, discipline, select):
        super().__init__()
        self.discipline_ = discipline
        self.select = select
        uic.loadUi("forms\Form6.ui", self)

    def mousePressEvent(self, event):
        self.select(self.discipline_)
