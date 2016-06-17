#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from google.appengine.ext import vendor
vendor.add('libs')
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
app = Flask(__name__)

import util
import json
from datetime import datetime, timedelta

kutc_tt = open("timetable/kutc.json")
takatsuki_tt = open("timetable/takatsuki.json")
tonda_tt = open("timetable/tonda.json")

kutc = json.load(kutc_tt)
takatsuki = json.load(takatsuki_tt)
tonda = json.load(tonda_tt)

time_table = {"kutc": kutc["kutc"], "takatsuki": takatsuki["takatsuki"], "tonda": tonda["tonda"]}

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/to-kutc')
def to_kutc():
    return render_template("to-kutc.html")


@app.route('/from-kutc')
def from_kutc():
    return render_template("from-kutc.html")


@app.route('/next-bus/<string:word>')
def next_bus(word):
    current_time = datetime.now(tz=util.JST())
    formatted_time = util.format_datetime_as_array(current_time)
    orig_dest = word.split("-")
    html = word + ".html"

    if orig_dest[0] == "to":
        origin = "kutc"
        destination = orig_dest[1]
    elif orig_dest[0] == "from":
        origin = orig_dest[1]
        destination = "kutc"

    next_bus = util.get_next_bus(time_table, origin, destination, *formatted_time)
    return render_template(html, year = next_bus[0], month = next_bus[1], day = next_bus[2], hour = next_bus[3], minute = next_bus[4][0], dest = next_bus[4][1], stat = next_bus[4][2])


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
    current_time = util.get_current_time()
    next_bus = util.get_next_bus(time_table, origin, destination, current_time[0], current_time[1], current_time[2], current_time[3], current_time[4])
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
            next_bus_results["results"].append({'Error': err_msg})
            continue

        origin, destination = ["", ""]
        if query['from'] == 'kutc' or query['from'] == 'takatsuki' or query['from'] == 'tonda':
            origin      = query["from"]
        if query['to'] == 'kutc' or query['to'] == 'takatsuki' or query['to'] == 'tonda':
            destination = query["to"]

        if origin == destination:
            err_msg = '"from" and "to" parameters are same. These parameters should be different.'
            next_bus_results["results"].append({'Error': err_msg})
            continue

        if origin == "" or destination == "":
            err_msg = '"from" or "to" parameters may be invalid. Should be in "kutc" or "takatsuki", "tonda".'
            next_bus_results["results"].append({'Error': err_msg})
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
        dt = datetime.now(tz=util.JST()) + timedelta(days=after_days, hours=after_hours, minutes=after_minutes)
        formatted_time = util.format_datetime_as_array(dt)

        next_bus = util.get_multiple_time_info_for_next_bus(time_table, origin, destination, *formatted_time, counts=counts)

        next_bus_result = {}
        if next_bus is None:
            err_msg = 'Cannot fetch time information of next bus.'
            next_bus_result = {
                    'Counts': 0,
                    'From'  : "",
                    'To'    : "",
                    'Buses' : [],
                    'Error' : err_msg,
                    }
        else:
            next_bus_result = {
                    'Counts': len(next_bus),
                    'From'  : origin,
                    'To'    : destination,
                    'Buses' : [],
                    'Error' : None,
                    }

            for nb in next_bus:
                next_bus_result["Buses"].append({
                    'Year'       : nb[0],
                    'Month'      : nb[1],
                    'Day'        : nb[2],
                    'Hour'       : nb[3],
                    'Minute'     : nb[4][0],
                    'Destination': nb[4][1],
                    'Stat'       : nb[4][2],
                    })

        next_bus_results["results"].append(next_bus_result)

    return jsonify(next_bus_results)

@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.after_request
def add_header(response):
    response.cache_control.max_age = 3600
    return response
