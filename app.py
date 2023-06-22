# Before execution, do --> source /scratch-local/testenv/env/bin/activate
from data_process import selectData, getMetaParam
from delay import delay

import sys

import base64
from io import BytesIO
import pandas as pd
import numpy as np

import flask
from flask_cors import CORS
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import requests
from multiprocessing import Process, Value
import os, signal

def test_delay():
    print("I'm running!")
    delay()
    print("I finished running!")
    process_status.value = 0
    os.kill(os.getpid(),signal.SIGTERM)

process_status = Value('i')
process_status.value = 0

APP = flask.Flask(__name__)
CORS(APP)

@APP.route("/getdomain", methods=["POST"])
def getdomain():
    req = flask.request.form.to_dict()
    return flask.jsonify(parameters=getMetaParam(req["x_axis"], req["y_axis"]))


@APP.route("/getalldata", methods=["POST", "GET"])
def getalldata():
    if flask.request.method == "POST":
        req = flask.request.form.to_dict()
        old_keylist = req.keys()
        new_dict = dict()
        # TODO remove the "[]" in some element and put it into new one
        for old_key in old_keylist:
            tmp = req[old_key]
            new_key = old_key

            if old_key[-2:] == "[]":
                tmp = flask.request.form.getlist(old_key)
                new_key = old_key[:-2]

            new_dict[new_key] = tmp
        retVal = selectData(new_dict)
        return flask.jsonify(response=retVal)
    else:
        retVal = selectData({})
        return flask.jsonify(response=retVal)

@APP.route("/test_thread")
def test_thread():
    p = Process(target=test_delay)
    p.daemon = True
    p.start()
    process_status.value = 1
    return "Process Started"

@APP.route("/track_status")
def track_status():
    return str(process_status.value)

@APP.route("/ping")
def ping():
    return "Pong!"


@APP.route("/")
def index():
    return flask.render_template("index.html")


@APP.errorhandler(404)
def page_not_found(e):
    return flask.render_template("404.html"), 404


if __name__ == "__main__":
    APP.debug = True
    APP.run(port=8080,host='0.0.0.0')
