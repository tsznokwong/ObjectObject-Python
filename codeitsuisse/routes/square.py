import logging
import json

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)

@app.route('/square', methods=['POST'])
def evaluate():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    inputValue = data.get("input")
    result = inputValue * inputValue
    logging.info("My result :{}".format(result))
    return json.dumps(result)

@app.route('/revisitgeometry', methods=['POST'])
def revisitgeometry():
    data = request.get_json()
    logging.info("revisitgeometry")
    logging.info(data)

    shape_lines = list()
    last_pt = data["shapeCoordinates"][-1]
    for pt in data["shapeCoordinates"]:
        shape_lines.append([pt, last_pt])
        last_pt = pt

    logging.info(shape_lines)

    return json.dumps(data)

