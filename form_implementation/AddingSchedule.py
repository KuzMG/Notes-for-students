from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from qtpy import uic
from sqlalchemy.orm import Session

import schedule_parsing.Parsing as parsing
from database.Table_db import engine, Schedule


class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.add_w1()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.show()

    def add_w1(self):
        main_widget = WidgetScheduleSelect()
        main_widget.addXlsButton.clicked.connect(self.the_add_xls_button_was_clicked)
        main_widget.addDocxButton.clicked.connect(self.the_add_docx_button_was_clicked)
        main_widget.closeButton.clicked.connect(self.close)
        self.layout().addWidget(main_widget)

    def add_w2(self):
        mirea_schedule = WidgetMireaSchedule()
        mirea_schedule.backButton.clicked.connect(self.the_back_button_was_clicked)
        mirea_schedule.closeButton.clicked.connect(self.close)
        self.layout().replaceWidget(self.layout().itemAt(0).widget(), mirea_schedule)

    def add_w3(self):
        bgu_schedule = WidgetAddBguScheduleDocx()
        bgu_schedule.backButton.clicked.connect(self.the_back_button_was_clicked)
        bgu_schedule.closeButton.clicked.connect(self.close)
        self.layout().replaceWidget(self.layout().itemAt(0).widget(), bgu_schedule)

    def add_w3(self):
        bgu_schedules = WidgetAddBguScheduleDocx()
        bgu_schedules.backButton.clicked.connect(self.the_back_button_was_clicked)
        bgu_schedules.closeButton.clicked.connect(self.close)
        bgu_schedules.uploadFile.clicked.connect(self.open_file)
        self.layout().replaceWidget(self.layout().itemAt(0).widget(), bgu_schedules)

    def add_w4(self, schedule):
        bgu_schedule = WidgetBguSchedule(schedule)
        bgu_schedule.backButton.clicked.connect(self.the_add_docx_button_was_clicked)
        bgu_schedule.closeButton.clicked.connect(self.close)
        self.layout().replaceWidget(self.layout().itemAt(0).widget(), bgu_schedule)

    def del_w(self, w):
        w.deleteLater()

    def the_back_button_was_clicked(self):
        self.del_w(self.layout().itemAt(0).widget())
        self.add_w1()

    def the_add_xls_button_was_clicked(self):
        self.del_w(self.layout().itemAt(0).widget())
        self.add_w2()

    def the_add_docx_button_was_clicked(self):
        self.del_w(self.layout().itemAt(0).widget())
        self.add_w3()

    def the_add_bgu_group_was_clicked(self, schedule):
        self.del_w(self.layout().itemAt(0).widget())
        self.add_w4(schedule)

    def open_file(self):
        path = QFileDialog.getOpenFileName(self, 'Open file', '/home', "Text files (*.docx)")[0]
        if path != '':
            print(path)
            schedule = parsing.schedule_of_groups_docx(path)
            if len(schedule) > 0:
                self.the_add_bgu_group_was_clicked(schedule)


class WidgetMireaSchedule(QWidget):
    def __init__(self):
        super().__init__()
        self.groups = None
        self.group = None
        uic.loadUi("forms\Form2.ui", self)
        self.schedule = parsing.get_schedule_xls()
        self.comboBoxQualif.setPlaceholderText("программа")
        self.comboBoxInst.setPlaceholderText("институт")
        self.comboBoxLocation.setPlaceholderText("корпус")
        self.comboBoxCourse.setPlaceholderText("курс")
        self.comboBoxGroup.setPlaceholderText("группа")
        self.okButton.clicked.connect(self.push_button_ok_signal)
        self.okButton.setEnabled(False)
        for qualif in self.schedule:
            self.comboBoxQualif.addItem(qualif.qualification)
        self.comboBoxQualif.activated.connect(self.combo_box_qualif_signal)
        self.comboBoxInst.activated.connect(self.combo_box_inst_signal)
        self.comboBoxLocation.activated.connect(self.combo_box_location_signal)
        self.comboBoxCourse.activated.connect(self.combo_box_course_signal)
        self.comboBoxGroup.activated.connect(self.combo_box_group_signal)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.show()

    def combo_box_qualif_signal(self, index):
        self.okButton.setEnabled(False)
        self.comboBoxInst.clear()
        for inst in self.schedule[index].institutes:
            self.comboBoxInst.addItem(inst.institute)
        self.comboBoxLocation.clear()
        self.comboBoxCourse.clear()
        self.comboBoxGroup.clear()

    def combo_box_inst_signal(self, index):
        self.okButton.setEnabled(False)
        self.comboBoxLocation.clear()
        for location in self.schedule[self.comboBoxQualif.currentIndex()].institutes[index].location:
            self.comboBoxLocation.addItem(location.location)
        self.comboBoxCourse.clear()
        self.comboBoxGroup.clear()

    def combo_box_location_signal(self, index):
        self.okButton.setEnabled(False)
        self.comboBoxCourse.clear()
        i = 1
        for course in \
                self.schedule[self.comboBoxQualif.currentIndex()].institutes[self.comboBoxInst.currentIndex()].location[
                    index].courses:
            self.comboBoxCourse.addItem(str(i))
            i += 1
        self.comboBoxGroup.clear()

    def combo_box_course_signal(self, index):
        self.okButton.setEnabled(False)
        self.groups = parsing.schedule_of_groups_xls(
            self.schedule[self.comboBoxQualif.currentIndex()].institutes[self.comboBoxInst.currentIndex()].location[
                self.comboBoxLocation.currentIndex()].courses[index])
        self.comboBoxGroup.clear()
        for i in range(0, len(self.groups) - 1):
            if self.groups[i].group is None:
                del self.groups[i]
            self.comboBoxGroup.addItem(self.groups[i].group)

    def combo_box_group_signal(self, index):
        self.okButton.setEnabled(True)
        self.group = self.groups[index]

    def push_button_ok_signal(self):
        with Session(bind=engine) as db:
            # if db.query(Schedule).filter(Schedule.group == self.group.group).first() is not None:
            #     group = db.query(Schedule).filter(Schedule.group == self.group.group).first()
            #     db.delete(group)
            if db.query(Schedule).filter(Schedule.group == self.group.group).first() is None:
                db.add(self.group)
                print(F"group {self.group.group} add")
            else:
                group = db.query(Schedule).filter(Schedule.group == self.group.group).first()
                db.delete(group)
                db.add(self.group)
                print(F"group {self.group.group} update")
            db.commit()


class WidgetScheduleSelect(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("forms\Form1.ui", self)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.show()


class WidgetAddBguScheduleDocx(QWidget):
    def __init__(self):
        super().__init__()
        self.schedule = None
        uic.loadUi("forms\Form3.ui", self)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.show()

        # with Session(bind=engine) as db:
        #     if db.query(Schedule).filter(Schedule.group == schedule[1].group).first() is None:
        #         db.add(schedule[1])
        #         print(F"group {schedule[1].group} add")
        #     else:
        #         group = db.query(Schedule).filter(Schedule.group == schedule.group).first()
        #         group.days_of_week = schedule.days_of_week
        #         print(F"group {group.group} update")
        #     db.commit()


class WidgetBguSchedule(QWidget):
    def __init__(self, schedule):
        super().__init__()
        self.group = None
        uic.loadUi("forms\Form4.ui", self)
        self.schedule = schedule
        self.comboBoxGroup.setPlaceholderText("группа")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        for group in self.schedule:
            self.comboBoxGroup.addItem(group.group)
        self.comboBoxGroup.activated.connect(self.combo_box_group_signal)
        self.okButton.setEnabled(False)
        self.okButton.clicked.connect(self.push_button_ok_signal)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.show()

    def combo_box_group_signal(self, index):
        self.okButton.setEnabled(True)
        self.group = self.schedule[index]

    def push_button_ok_signal(self):
        with Session(bind=engine) as db:
            # if db.query(Schedule).filter(Schedule.group == self.group.group).first() is not None:
            #     group = db.query(Schedule).filter(Schedule.group == self.group.group).first()
            #     db.delete(group)
            if db.query(Schedule).filter(Schedule.group == self.group.group).first() is None:
                db.add(self.group)
                print(F"group {self.group.group} add")
            else:
                group = db.query(Schedule).filter(Schedule.group == self.group.group).first()
                db.delete(group)
                db.add(self.group)
                print(F"group {self.group.group} update")
            db.commit()
