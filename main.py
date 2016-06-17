#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from google.appengine.ext import vendor
vendor.add('libs')
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
app = Flask(__name__)

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


def get_current_time():
    return map(int, datetime.now(tz=JST()).strftime("%Y %-m %-d %H %M").split(" "))

def format_datetime_as_array(dt):
    return map(int, dt.strftime("%Y %-m %-d %H %M").split(" "))

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/to-kutc')
def to_kutc():
    return render_template("to-kutc.html")


@app.route('/from-kutc')
def from_kutc():
    return render_template("from-kutc.html")


@app.route('/to-takatsuki')
def to_takatsuki():
    current_time = get_current_time()
    next_bus = get_next_bus(time_table, "kutc", "takatsuki", current_time[0], current_time[1], current_time[2], current_time[3], current_time[4])
    return render_template("to-takatsuki.html",  year = next_bus[0], month = next_bus[1], day = next_bus[2], hour = next_bus[3], minute = next_bus[4][0], dest = next_bus[4][1], stat = next_bus[4][2])


@app.route('/to-tonda')
def to_tonda():
    current_time = get_current_time()
    next_bus = get_next_bus(time_table, "kutc", "tonda", current_time[0], current_time[1], current_time[2], current_time[3], current_time[4])
    return render_template("to-tonda.html", year = next_bus[0], month = next_bus[1], day = next_bus[2], hour = next_bus[3], minute = next_bus[4][0], dest = next_bus[4][1], stat = next_bus[4][2])


@app.route('/from-takatsuki')
def from_takatsuki():
    current_time = get_current_time()
    next_bus = get_next_bus(time_table, "takatsuki", "kutc", current_time[0], current_time[1], current_time[2], current_time[3], current_time[4])
    return render_template("from-takatsuki.html", year = next_bus[0], month = next_bus[1], day = next_bus[2], hour = next_bus[3], minute = next_bus[4][0], dest = next_bus[4][1], stat = next_bus[4][2])


@app.route('/from-tonda')
def from_tonda():
    current_time = get_current_time()
    next_bus = get_next_bus(time_table, "tonda", "kutc", current_time[0], current_time[1], current_time[2], current_time[3], current_time[4])

    return render_template("from-tonda.html", year = next_bus[0], month = next_bus[1], day = next_bus[2], hour = next_bus[3], minute = next_bus[4][0], dest = next_bus[4][1], stat = next_bus[4][2])


@app.route('/api/v1/next-bus/<string:word>', methods=['GET'])
def api_get_next_bus(word):
    origin = ''
    destination = ''
    if word == 'to-takatsuki':
        origin = 'kutc'
        destination = 'takatsuki'
    elif word == 'to-tonda':
        origin = 'kutc'
        destination = 'tonda'
    elif word == 'from-takatsuki':
        origin = 'takatsuki'
        destination = 'kutc'
    elif word == 'from-tonda':
        origin = 'tonda'
        destination = 'kutc'
    else:
        return jsonify({'Error': 'Mismatch your request path'}), 400
    current_time = get_current_time()
    next_bus = get_next_bus(time_table, origin, destination, current_time[0], current_time[1], current_time[2], current_time[3], current_time[4])
    if next_bus is None:
        return jsonify({'Error': 'Cannot fetch time information of next bus.'}), 400

    return jsonify({'Year': next_bus[0], 'Month': next_bus[1], 'Day': next_bus[2], 'Hour': next_bus[3], 'Minute': next_bus[4][0], 'Destination': next_bus[4][1], 'Stat': next_bus[4][2]})

@app.route('/api/v1/next-bus/', methods=['POST'])
def api_get_next_bus_for_post_request():
    if 'CONTENT_TYPE' not in request.headers:
        err_msg = '"Content-Type" field in HTTP request header does not exist. Should set "application/json".'
        return jsonify({'Error': err_msg}), 400

    if request.headers['Content-Type'] != 'application/json':
        err_msg = 'Invalid Content-Type field of HTTP request header. Should be in "application/json".'
        return jsonify({'Error': err_msg}), 400

    req = request.get_json()
    if not req:
        err_msg = 'Cannot parse the request as JSON format.'
        return jsonify({'Error': err_msg}), 400

    if not req["queries"]:
        err_msg = 'Invalid JSON format.'
        return jsonify({'Error': err_msg}), 400

    next_bus_results = {"results": []}

    for query in req["queries"]:

        if not 'from' in query or not 'to' in query:
            err_msg = '"from" or "to" parameters does not exist.'
            next_bus = {'Error': err_msg}
            next_bus_results["results"].append(next_bus)
            continue

        origin, destination = ["", ""]
        if query['from'] == 'kutc' or query['from'] == 'takatsuki' or query['from'] == 'tonda':
            origin      = query["from"]
        if query['to'] == 'kutc' or query['to'] == 'takatsuki' or query['to'] == 'tonda':
            destination = query["to"]

        if origin == "" or destination == "":
            err_msg = '"from" or "to" parameters may be invalid. Should be in "kutc" or "takatsuki", "tonda".'
            next_bus = {'Error': err_msg}
            next_bus_results["results"].append(next_bus)
            continue

        after_days, after_hours, after_minutes = [0, 0, 0]
        if 'days' in query:
            try:
                after_days = int(query['days'])
            except:
                pass
        if 'hours' in query:
            try:
                after_hours = int(query['hours'])
            except:
                pass
        if 'minutes' in query:
            try:
                after_minutes = int(query['minutes'])
            except:
                pass

        counts = 0
        if 'counts' in query:
            try:
                counts = int(query['counts'])
            except:
                pass

        # Calculate the elapsed time you specify from the current time.
        dt = datetime.now(tz=JST()) + timedelta(days=after_days, hours=after_hours, minutes=after_minutes)
        formatted_time = format_datetime_as_array(dt)

        next_bus = get_next_bus(time_table, origin, destination, *formatted_time)
        if next_bus is None:
            err_msg = 'Cannot fetch time information of next bus.'
            next_bus = {'Error': err_msg}
        else:
            next_bus = {
                    'From'       : origin,
                    'To'         : destination,
                    'Year'       : next_bus[0],
                    'Month'      : next_bus[1],
                    'Day'        : next_bus[2],
                    'Hour'       : next_bus[3],
                    'Minute'     : next_bus[4][0],
                    'Destination': next_bus[4][1],
                    'Stat'       : next_bus[4][2],
                    'Error'      : None
                    }

        next_bus_results["results"].append(next_bus)

    return jsonify(next_bus_results)

@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.after_request
def add_header(response):
    response.cache_control.max_age = 3600
    return response
