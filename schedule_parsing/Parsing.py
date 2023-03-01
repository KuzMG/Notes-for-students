import os
import re
import requests
from bs4 import BeautifulSoup
from openpyxl.reader.excel import load_workbook

from database.Table_db import Schedule, DaysOfWeek, PairNumber, ParityOfWeek, Pair
from dto.DataClasses import ScheduleXls, Location, Institute


def get_schedule_xls():
    URL = "https://www.mirea.ru/schedule/"
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")
    scheduleMirea = soup.find('ul', id='tab-content').find_all('li', )
    schedule = []

    qualification = ["Бакалавриат/Специалитет", "Магистратура"]
    a = 0
    for qualif in scheduleMirea:
        if a == 2:
            break
        a += 1
        schedule.append(ScheduleXls(qualification[len(schedule)], []))
        for inst in qualif.find().find_all(recursive=False):
            if (not inst.find(class_="uk-text-bold")) or inst.find(
                    class_="uk-text-bold").text == "Филиал в городе Ставрополе":
                continue
            schedule[-1].institutes.append(Institute(inst.find(class_="uk-text-bold").text.strip(), []))
            for course in inst.find(class_=re.compile("uk-width-1-1 uk-grid-small")).find_all("div"):
                if course['class'][0] != "uk-width-expand@m" and course['class'][0] != "uk-width-1-2":
                    continue
                if course['class'][0] == "uk-width-expand@m":
                    schedule[-1].institutes[-1].location.append(Location(course.text.strip(), []))
                    continue
                schedule[-1].institutes[-1].location[-1].courses.append(
                    course.find(class_='uk-link-toggle').get("href"))
    return schedule


def schedule_of_groups(schedule_xls):
    req = requests.get(schedule_xls)
    file = open("res/schedule/schedule.xlsx", "wb")
    file.write(req.content)
    wb = load_workbook('res/schedule/schedule.xlsx')
    daysOfWeek = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    scheduleOfTheGroups = []
    for ws in wb:
        for i in range(0, ws.max_column // 5):
            if (i + 1) % 3 == 0:
                continue
            scheduleOfTheGroups.append(Schedule(group='', days_of_week=[]))
            a = 1
            day = 0
            pairNumber = 1
            for row in ws.iter_rows(min_row=2, max_row=87, min_col=6 + 5 * i, max_col=9 + 5 * i, values_only=True):
                if a == 1:
                    scheduleOfTheGroups[-1].group = row[0]
                    a += 1
                    continue
                if a == 2:
                    a += 1
                    continue
                if (a - 3) % 14 == 0:
                    pairNumber = 1
                    scheduleOfTheGroups[-1].days_of_week.append(DaysOfWeek(day_of_week=daysOfWeek[day], pair_number=[]))
                    day += 1
                if (a - 3) % 2 == 0:
                    scheduleOfTheGroups[-1].days_of_week[-1].pair_number.append(
                        PairNumber(pair_number=pairNumber, parity=[]))
                    scheduleOfTheGroups[-1].days_of_week[-1].pair_number[-1].parity.append(
                        ParityOfWeek(parity=True,
                                     pair=[Pair(discipline=row[0], occupation=row[1], name_of_the_teacher=row[2],
                                               number_of_cabinet=row[3])]))
                    pairNumber += 1
                else:
                    scheduleOfTheGroups[-1].days_of_week[-1].pair_number[-1].parity.append(
                        ParityOfWeek(parity=False,
                                     pair=[Pair(discipline=row[0], occupation=row[1], name_of_the_teacher=row[2],
                                               number_of_cabinet=row[3])]))
                a += 1
    return scheduleOfTheGroups
