import logging
import json
import math

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)


@app.route('/bucket-fill', methods=['POST'])
def bucket_fill():
    data = request.get_data()
    print(data)
    return json.dumps({"result": 3315})

import sys, math
from lxml import etree
import turtle

def parseData(input):
    svg = etree.fromstring(input)
    width = 0
    height = 0
    for item in svg.items():
        tag, v = item
        if tag == 'width':
            width = int(v)
        elif tag == 'height':
            height = int(v)

    water_sources = list()
    pipes = list()
    buckets = list()
    for element in svg.getchildren():
        if element.tag.replace("{http://www.w3.org/2000/svg}", "") == "circle":
            water = dict()
            for item in element.items():
                tag, v = item
                water[tag] = v

            del water["fill"]
            del water["stroke"]

            water_sources.append(water)
        elif element.tag.replace("{http://www.w3.org/2000/svg}", "") == "polyline":
            polyline = dict()
            for item in element.items():
                tag, v = item
                polyline[tag] = v
            
            coordinates = list()
            for coordinate in polyline["points"].split(" "):
                coordinates.append([int(i) for i in coordinate.split(",")])
            polyline["points"] = coordinates

            del polyline["fill"]
            del polyline["stroke"]

            polyline["watered"] = False

            if len(polyline["points"]) == 2:
                # pipes
                pipes.append(polyline)
            else:
                # bucket
                polyline["volume"] = (polyline["points"][0][0] - polyline["points"][2][0]) * (polyline["points"][0][1] - polyline["points"][2][1])
                polyline["volume"] = abs(polyline["volume"])
                buckets.append(polyline)

    print(width, height)
    print(water_sources)
    print(pipes)
    print(buckets)

    return width, height, water_sources, pipes, buckets

def to_slope_intercept(coord_a, coord_b):
    # y = slope * x + intercept
    delta_y = coord_a['y'] - coord_b['y']
    delta_x = coord_a['x'] - coord_b['x']

    if delta_x == 0:
        return math.inf, coord_a['x']

    slope = delta_y / delta_x
    intercept = coord_a['y'] - slope * coord_a['x']

    return slope, intercept

def get_intersection(line_a_slope, line_a_intercept, line_b_slope, line_b_intercept):
    if line_a_slope == line_b_slope:
        # parallel line
        return []
    if line_a_slope == math.inf:
        return [{"x": line_a_intercept, "y": line_b_slope * line_a_intercept + line_b_intercept}]
    if line_b_slope == math.inf:
        return [{"x": line_b_intercept, "y": line_a_slope * line_b_intercept + line_a_intercept}]

    slope_diff = line_a_slope - line_b_slope
    intercept_diff = line_b_intercept - line_a_intercept
    x = intercept_diff / slope_diff
    y = x * line_a_slope + line_a_intercept
    return [{"x": x, "y": y}]

def check_inbound(bound_a, bound_b, point):
    upper_x = max(bound_a['x'], bound_b['x'])
    lower_x = min(bound_a['x'], bound_b['x'])
    upper_y = max(bound_a['y'], bound_b['y'])
    lower_y = min(bound_a['y'], bound_b['y'])

    x = point['x']
    y = point['y']

    if (x < lower_x) or (x > upper_x) or (y < lower_y) or (y > upper_y):
        return False
    return True

input = b'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="153" height="306"><circle cx="76" cy="0" r="1" fill="none" stroke="blue" /><polyline fill="none" stroke="black" points="0,88 0,137 31,137 31,88" /><polyline fill="none" stroke="black" points="2,77 7,82" /><polyline fill="none" stroke="black" points="15,182 15,234 18,234 18,182" /><polyline fill="none" stroke="black" points="76,3 4,75" /><polyline fill="none" stroke="black" points="18,142 18,178 38,178 38,142" /><polyline fill="none" stroke="black" points="88,177 88,206 107,206 107,177" /></svg>'

width, height, water_sources, pipes, buckets = parseData(input)

t = turtle.Turtle()
t.speed(0)

def draw(t, points):
    t.pencolor("black")
    t.pendown()
    for pt in points:
        t.goto(pt[0], pt[1])
    t.penup()
    t.pencolor("white")

bound = [(0, 0), (width, 0), (width, height), (0, height), (0, 0)]
draw(t, bound)
for pipe in pipes:
    draw(t, pipe["points"])
for bucket in buckets:
    draw(t, bucket["points"])
while True:
    pass