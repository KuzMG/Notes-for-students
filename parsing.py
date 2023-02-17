import os
import re
import requests
from bs4 import BeautifulSoup
from openpyxl.reader.excel import load_workbook

from DataClasses import Schedule, Location, Institute

if not os.path.exists("schedule.xlsx"):
    URL = "https://www.mirea.ru/schedule/"
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")
    scheduleMirea = soup.find('ul', id='tab-content').find_all('li', )
    schedule = []

    qualification = ["бакалавриат/специалитет", "магистратура", "аспирантура", "", ""]
    a = 0
    for qualif in scheduleMirea:
        if (a == 3):
            break
        a += 1
        schedule.append(Schedule(qualification[len(schedule)], []))
        for inst in qualif.find().find_all(recursive=False):
            if (not inst.find(class_="uk-text-bold")) or inst.find(
                    class_="uk-text-bold").text == "Филиал в городе Ставрополе":
                continue
            schedule[-1].institutes.append(Institute(inst.find(class_="uk-text-bold").text, []))
            for course in inst.find(class_=re.compile("uk-width-1-1 uk-grid-small")).find_all("div"):
                if course['class'][0] != "uk-width-expand@m" and course['class'][0] != "uk-width-1-2":
                    continue
                if course['class'][0] == "uk-width-expand@m":
                    schedule[-1].institutes[-1].location.append(Location(course.text, []))
                    continue
                schedule[-1].institutes[-1].location[-1].courses.append(
                    course.find(class_='uk-link-toggle').get("href"))
    req = requests.get(schedule[0].institutes[0].location[0].courses[0])
    file = open("schedule.xlsx", "wb")
    file.write(req.content)

wb = load_workbook('schedule.xlsx')
ws = wb[wb.sheetnames[0]]
for row in ws.values:
    for value in row:
        print(value)
