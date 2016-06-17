#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import json
from datetime import date, datetime, timedelta, tzinfo

kutc_tt = open("timetable/kutc.json")
takatsuki_tt = open("timetable/takatsuki.json")
tonda_tt = open("timetable/tonda.json")

kutc = json.load(kutc_tt)
takatsuki = json.load(takatsuki_tt)
tonda = json.load(tonda_tt)

time_table = {"kutc": kutc["kutc"], "takatsuki": takatsuki["takatsuki"], "tonda": tonda["tonda"]}

# GAEでJSTを扱うためのクラス
class JST(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=9)


    def dst(self, dt):
        return timedelta(0)


    def tzname(self, dt):
        return 'JST'


def get_element(time_table, key):
    try:
        time_table[key]
        return time_table[key]
    except:
        pass


def get_next_bus(time_table, from_, to, year, month, day, hour, minute):
    re_list = []

    from_tt = get_element(time_table, from_)
    if from_tt is None:
        return None
    to_tt = get_element(from_tt, to)
    if to_tt is None:
        return None

    # 日付のタイプ(week, sat, sun)を取得
    daytype = get_day_type(year, month, day)
    if daytype == "":
        return None

    # 学休期間かどうか調べる
    in_vacation = date_is_in_vacation(year, month, day)

    day_tt = get_element(to_tt, daytype)
    if day_tt is None:
        return None

    hour_tt = get_element(day_tt, str(hour))

    # 次のバスが見つかるまで時刻表を読み込む
    while True:
        if hour_tt is not None:
            for bus in hour_tt:
                if bus[0] > minute:
                    bus_type = bus[2]
                    if not in_vacation and bus_type == 2:
                        # 通常日かつ学休日のみ運行バスのとき
                        continue
                    if in_vacation and (bus_type == 1 or bus_type == 3):
                        # 学休日かつ運休のバスの時
                        continue
                    re_list = [year, month, day, hour, bus]
                    return re_list

        # 時刻，日付の更新
        minute = 0
        if hour < 23:
            hour += 1
        else:
            day += 1
            hour = 0

            if not validate_date(year, month, day):
                if month < 12:
                    month += 1
                    day = 1
                else:
                    year += 1
                    month = day = 1

            in_vacation = date_is_in_vacation(year, month, day)
            daytype = get_day_type(year, month, day)
            day_tt = get_element(to_tt, daytype)
            if day_tt is None:
                return None

        hour_tt = get_element(day_tt, str(hour))


def get_multiple_time_info_for_next_bus(time_table, from_, to, year, month, day, hour, minute, counts=1):
    re_list = []

    from_tt = get_element(time_table, from_)
    if from_tt is None:
        return None
    to_tt = get_element(from_tt, to)
    if to_tt is None:
        return None

    # 日付のタイプ(week, sat, sun)を取得
    daytype = get_day_type(year, month, day)
    if daytype == "":
        return None

    # 学休期間かどうか調べる
    in_vacation = date_is_in_vacation(year, month, day)

    day_tt = get_element(to_tt, daytype)
    if day_tt is None:
        return None

    hour_tt = get_element(day_tt, str(hour))

    # 次のバスが見つかるまで時刻表を読み込む
    while True:
        if hour_tt is not None:
            for bus in hour_tt:
                if bus[0] > minute:
                    bus_type = bus[2]
                    if not in_vacation and bus_type == 2:
                        # 通常日かつ学休日のみ運行バスのとき
                        continue
                    if in_vacation and (bus_type == 1 or bus_type == 3):
                        # 学休日かつ運休のバスの時
                        continue

                    re_list.append((year, month, day, hour, bus))
                    if len(re_list) >= counts:
                        return re_list

        # 時刻，日付の更新
        minute = 0
        if hour < 23:
            hour += 1
        else:
            day += 1
            hour = 0

            if not validate_date(year, month, day):
                if month < 12:
                    month += 1
                    day = 1
                else:
                    year += 1
                    month = day = 1

            in_vacation = date_is_in_vacation(year, month, day)
            daytype = get_day_type(year, month, day)
            day_tt = get_element(to_tt, daytype)
            if day_tt is None:
                return None

        hour_tt = get_element(day_tt, str(hour))


def get_day_type(year, month, day):
    if not validate_date(year, month, day):
        return None

    week = date(year, month, day).weekday()
    daytype = ""

    if week == 5:
        daytype = "sat"
    elif week == 6:
        daytype = "sun"
    else:
        daytype = "week"

    return daytype


def date_is_in_vacation(year, month, day):
    if not validate_date(year, month, day):
        return None

    date_ = date(year, month, day)

    # 以下の学級期間は平成位28年度のもの，年度によって変更の必要あり
    springv_start = date(year, 1, 31)
    springv_end = date(year, 3, 31)
    summerv_start = date(year, 7, 30)
    summerv_end = date(year, 9, 20)
    winterv_start = date(year, 12, 25)
    winterv_end = date(year, 1, 6)

    # 学休期間ならばTrue
    if (springv_start <= date_ and date_ <= springv_end) or \
     (summerv_start <= date_ and date_ <= summerv_end) or \
     (winterv_start <= date_ and date_ <= winterv_end):
        return True
    else:
        return False


def validate_date(year, month, day):
    try:
        date(int(year), int(month), int(day))
        return True
    except:
        return False


def format_datetime_as_array(dt):
    return map(int, dt.strftime("%Y %-m %-d %H %M").split(" "))
