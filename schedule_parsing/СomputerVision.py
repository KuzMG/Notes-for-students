import cv2

import numpy as np

import pytesseract

from sqlalchemy.orm import Session
from database.Table_db import Schedule, DaysOfWeek, PairNumber, ParityOfWeek, Pair, engine


def main():
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\mikha\AppData\Local\Tesseract-OCR\tesseract.exe'

    img_original = cv2.imread('res/schedule/image_pdf/schedule_bgu_page-0001.jpg')
    img = cv2.imread('res/schedule/image_pdf/schedule_bgu_page-0001.jpg', cv2.IMREAD_GRAYSCALE)
    h_img, w_img = img.shape
    _, v = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(v, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > w_img // 2 and h > h_img // 2:
            rect = cv2.minAreaRect(contour)
            rotation_matrix = cv2.getRotationMatrix2D((w_img // 2, h_img // 2), -90 + rect[2], 1.0)
            rotated = cv2.warpAffine(img, rotation_matrix, (w_img, h_img),
                                     borderMode=cv2.BORDER_REPLICATE)  # BORDER_REPLICATE
            rotated_original = cv2.warpAffine(img_original, rotation_matrix, (w_img, h_img),
                                              borderMode=cv2.BORDER_REPLICATE)  # BORDER_REPLICATE
            break
    _, v = cv2.threshold(rotated, 240, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(v, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > w_img // 2 and h > h_img // 2:
            rightmost = tuple(contour[contour[:, :, 0].argmax()][0])
            bottommost = tuple(contour[contour[:, :, 1].argmax()][0])
            img_crop = rotated[y:y + h, x:x + w]
            img_crop_original = rotated_original[y:y + h, x:x + w]
            cv2.imwrite('crop.jpg', img_crop)
            break
    w, h = img_crop.shape
    img_vertic = img_crop[w // 2: w, ]
    _, v_ver = cv2.threshold(img_vertic, 240, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(v_ver, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w_1, h_1 = cv2.boundingRect(contour)
        if h_1 > h // 4:
            leftmost = tuple(contour[contour[:, :, 0].argmin()][0])
    img_horiz = img_crop[0:w, h // 2:h]
    _, v_hor = cv2.threshold(img_horiz, 240, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(v_hor, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w_1, h_1 = cv2.boundingRect(contour)
        if w_1 > w // 4:
            topmost = tuple(contour[contour[:, :, 1].argmin()][0])
            break
    img = img_crop[topmost[1]:bottommost[1], leftmost[0]:rightmost[0]]
    img_original = img_crop_original[topmost[1]:bottommost[1], leftmost[0]:rightmost[0]]
    (b_channel, g_channel, r_channel) = cv2.split(img_original)
    image_merged = cv2.merge((b_channel, g_channel, r_channel))
    img = cv2.cvtColor(image_merged, cv2.COLOR_BGRA2GRAY)
    _, v = cv2.threshold(img, 235, 255, cv2.THRESH_BINARY_INV)
    cv2.imshow('dd', v)
    cv2.waitKey(0)
    contours, hierarchy = cv2.findContours(v, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    kernel1 = np.ones((9, 9), 'uint8')
    _, v1 = cv2.threshold(img, 235, 255, cv2.THRESH_BINARY)
    dilate = cv2.dilate(v1, kernel1, iterations=1)
    dilate = cv2.bitwise_not(dilate)
    contours2, hierarchy = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    dayOfWeek = []
    w, h = img.shape

    for contour2 in contours2:
        x, y, w_1, h_1 = cv2.boundingRect(contour2)
        if w_1 > w // 2:
            dayOfWeek.append(y)
    last_h = 0
    last_y = 0
    img_item = []
    i = 0
    pair = 0
    day = ['СБ', 'Пт', 'ЧТ', 'СР', 'ВТ', 'ПН']
    date = ['09.00-10.35', '10.45-12.20', '13.00-14.35', '14.45-16.20']
    last_flag = True
    for contour in contours:
        x, y, w_1, h_1 = cv2.boundingRect(contour)
        if w_1 * h_1 > w * h * 0.0025 and h_1 < h * 0.5:
            if w_1 > w * 0.82:
                day.pop(i)
                pair = 0
                continue
            if dayOfWeek[i] >= y:
                pair = 0
                i += 1
            if x > w // 16 and w_1 > w // 4:
                flag = False
                pair += 1
                if (last_h * 0.9 > h_1 and last_y < y + 10) or (not last_flag and last_y > last_y_pair + 10):
                    pair -= 1
                    # d = cv2.rectangle(img_original, (x, y), (x + w_1, y + h_1), (0, 255, 0), 3)
                    # cv2.imshow('dd', d)
                    # cv2.waitKey(0)
                last_flag = False
                last_y_pair = y
            else:
                flag = True
                last_flag = True
                last_y = y
                last_h = h_1
            # print(day[i], pair, flag)
            # d = cv2.rectangle(img_original, (x, y), (x + w_1, y + h_1), (0, 255, 0), 3)
            # cv2.imshow('dd', d)
            # cv2.waitKey(0)
            img_item.append((cv2.boundingRect(contour), day[i], pair, flag))
    i = 0
    schedule = Schedule(group='группа 1', days_of_week=[])
    day = '-'
    # cv2.imshow('dd', im)
    # cv2.waitKey(0)
    pair_number_ = -1
    for item in reversed(img_item):
        x, y, w, h = item[0]
        # print(item[1], item[2], item[3])
        # d = cv2.rectangle(img_original, (x,y), (x+w,y+h), (0,255,0), 3)
        # cv2.imshow('dd', d)
        # cv2.waitKey(0)
        img = img_original[y:y + h, x:x + w]
        size = (img.shape[1] * 2, img.shape[0] * 2)
        resized = cv2.resize(img, size)
        img = cv2.bitwise_not(resized)
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        im = cv2.filter2D(img, -1, kernel)
        if item[3]:
            kernel1 = np.ones((1, 1), 'uint8')
        else:
            kernel1 = np.ones((1, 1), 'uint8')
        im = cv2.dilate(im, kernel1, iterations=1)
        im = cv2.rectangle(im, (0, 0), (im.shape[1], im.shape[0]), (0, 0, 0), 13)

        if item[1] != day:
            schedule.days_of_week.append(DaysOfWeek(day_of_week=item[1], pair_number=[]))
            pair_number = 0
            pair_number_date = 0
            pair_number_ = 0
        if item[3]:
            text = pytesseract.image_to_string(im,
                                               lang='rus', config='--psm 11 -c tessedit_char_whitelist=01234569.-')
            text = text.replace("\n", "")
            pair_number_date += 1
            for pair_date in date:
                similar = 0
                for symbol in range(len(pair_date)):
                    if len(pair_date) == len(text) and pair_date[symbol] == text[symbol]:
                        similar += 1
                if similar >= len(pair_date) - 1:
                    text = pair_date
            if len(schedule.days_of_week[-1].pair_number) < pair_number_date:
                schedule.days_of_week[-1].pair_number.append(PairNumber(date=text, parity=[]))
            else:
                schedule.days_of_week[-1].pair_number[-1].date = text
        else:
            if pair_number_ != item[2]:
                pair_number += 1
            text = pytesseract.image_to_string(im, lang='rus')
            text = text.replace("\n", " ")
            text = text.strip()
            occupation_ = ''
            name_of_the_teacher_ = ''
            if len(text) > 0 and (text[-1] == '.' or text[-1] == ','):
                text = text[:len(text) - 1]
                text = text.strip()
            if text.find('лекция') != -1:
                occupation_ = text[text.find('лекция'):text.find('лекция') + 6]
                text = text[:text.find('лекция')]
            elif text.find('семинар') != -1:
                occupation_ = text[text.find('семинар'):text.find('семинар') + 7]
                text = text[:text.find('семинар')]
            elif text.find('П/р') != -1:
                occupation_ = text[text.find('П/р'):text.find('П/р') + 3]
                text = text[:text.find('П/р')]
            elif text.find('Г/р') != -1:
                occupation_ = text[text.find('Г/р'):text.find('Г/р') + 3]
                text = text[:text.find('Г/р')]
            elif text.find('л/б') != -1:
                occupation_ = text[text.find('л/б'):text.find('л/б') + 3]
                text = text[:text.find('л/б')]
            if text.find('Учебная практика') != -1:
                discipline_ = text
                occupation_ = ''
                name_of_the_teacher_ = ''
            else:

                try:
                    name_of_the_teacher_ = text[text.rindex('(') + 1:text.rindex(')')]
                    discipline_ = text[:text.rindex('(')]
                except:
                    discipline_ = text
            if len(schedule.days_of_week[-1].pair_number) < pair_number:
                schedule.days_of_week[-1].pair_number.append(PairNumber(date=None, parity=[]))
            if pair_number_ == item[2]:
                schedule.days_of_week[-1].pair_number[-1].parity.append(ParityOfWeek(parity=False,
                                                                                     pair=[Pair(
                                                                                         discipline=discipline_,
                                                                                         occupation=occupation_,
                                                                                         name_of_the_teacher=name_of_the_teacher_,
                                                                                         number_of_cabinet='')]))
            else:
                schedule.days_of_week[-1].pair_number[-1].parity.append(ParityOfWeek(parity=True,
                                                                                     pair=[Pair(
                                                                                         discipline=discipline_,
                                                                                         occupation=occupation_,
                                                                                         name_of_the_teacher=name_of_the_teacher_,
                                                                                         number_of_cabinet='')]))
            pair_number_ = item[2]
        i += 1
        day = item[1]
        cv2.imwrite(F'res/schedule/image/item{i}.jpg', im)
    cv2.imwrite('result_orig.jpg', img_original)
    cv2.imwrite('rotation.jpg', rotated)
    cv2.imwrite('result.jpg', img)
    cv2.imwrite('threshold.jpg', v)
    with Session(bind=engine) as db:
        if db.query(Schedule).filter(Schedule.group == schedule.group).first() is None:
            db.add(schedule)
            print(F"group {schedule.group} add")
        else:
            group = db.query(Schedule).filter(Schedule.group == schedule.group).first()
            group.days_of_week = schedule.days_of_week
            print(F"group {group.group} update")
        db.commit()
