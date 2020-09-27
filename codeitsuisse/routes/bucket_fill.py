import logging
import json
import math

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)

from lxml import etree
import cv2
import numpy as np

def isBucketInBucket(bucket, polylines):
    bx1 = bucket["points"][0][0]
    by1 = bucket["points"][0][1]
    bx2 = bucket["points"][2][0]
    by2 = bucket["points"][2][1]

    for polyline in polylines:
        if polyline["type"] == "pipe":
            continue

        x1 = polyline["points"][0][0]
        y1 = polyline["points"][0][1]
        x2 = polyline["points"][2][0]
        y2 = polyline["points"][2][1]

        if (bx1 >= x1) and (bx2 <= x2) and (by1 > y1) and (by2 < y2):
            bucket["volume"] = 0

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
    polylines = list()
    for element in svg.getchildren():
        if element.tag.replace("{http://www.w3.org/2000/svg}", "") == "circle":
            water = dict()
            for item in element.items():
                tag, v = item
                water[tag] = v

            del water["fill"]
            del water["stroke"]

            for key in water.keys():
                water[key] = int(water[key])
            water["end_y"] = water["cy"] + 1

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

            polyline["intersect_y"] = 1000000
            polyline["watered"] = False
            polyline["derived_water"] = list()

            if len(polyline["points"]) == 4:
                # bucket
                polyline["type"] = "bucket"
                polyline["volume"] = (polyline["points"][0][0] - polyline["points"][2][0]) * (polyline["points"][0][1] - polyline["points"][2][1])
                polyline["volume"] = abs(polyline["volume"])
            else:
                polyline["type"] = "pipe"

            polylines.append(polyline)

    for polyline in polylines:
        if polyline["type"] == "pipe":
            continue
        isBucketInBucket(polyline, polylines)

    return width, height, water_sources, polylines

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

def intersect_polyline(water, polyline):
    polyline["intersect_y"] = 1000000
    polyline["derived_water"] = list()

    if polyline["type"] == "pipe":
        x1 = polyline["points"][0][0]
        y1 = polyline["points"][0][1]
        x2 = polyline["points"][1][0]
        y2 = polyline["points"][1][1]
    else: # use the bottom line
        x1 = polyline["points"][1][0]
        y1 = polyline["points"][1][1]
        x2 = polyline["points"][2][0]
        y2 = polyline["points"][2][1]

    water_slope, water_intercept = to_slope_intercept({"x": water["cx"], "y": water["cy"]}, {"x": water["cx"], "y": water["cy"]+2})
    polyline_slope, polyline_intercept = to_slope_intercept({"x": x1, "y": y1}, {"x": x2, "y": y2})
    intersect = get_intersection(water_slope, water_intercept, polyline_slope, polyline_intercept)
    if len(intersect) == 0: # no intercept point
        return
    inbound = check_inbound({"x": x1, "y": y1}, {"x": x2, "y": y2}, intersect[0])
    if not inbound: # intercept point outside
        return
    if intersect[0]["y"] < water["cy"]:
        return

    polyline["intersect_y"] = intersect[0]["y"]
    if polyline["type"] == "pipe":
        if y2 > y1:
            if x1 > x2:
                polyline["derived_water"] = [{"cx": x2-1, "cy": y2}]
            else:
                polyline["derived_water"] = [{"cx": x2+1, "cy": y2}]
        else:
            if x1 > x2:
                polyline["derived_water"] = [{"cx": x1+1, "cy": y1}]
            else:
                polyline["derived_water"] = [{"cx": x1-1, "cy": y1}]
    else:
        if x1 > x2:
            polyline["derived_water"] = [{"cx": x2-1, "cy": y2}, {"cx": x1+1, "cy": y1}]
        else:
            polyline["derived_water"] = [{"cx": x2+1, "cy": y2}, {"cx": x1-1, "cy": y1}]
    for water in polyline["derived_water"]:
        water["end_y"] = 1000000

    # print("intersect", polyline)

count = 0
@app.route('/bucket-fill', methods=['POST'])
def bucket_fill():
    # print()
    # print()
    # print()

    input = request.get_data()
    # print(input)

    # input = b'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="153" height="306"><circle cx="76" cy="0" r="1" fill="none" stroke="blue" /><polyline fill="none" stroke="black" points="0,88 0,137 31,137 31,88" /><polyline fill="none" stroke="black" points="2,77 7,82" /><polyline fill="none" stroke="black" points="15,182 15,234 18,234 18,182" /><polyline fill="none" stroke="black" points="76,3 4,75" /><polyline fill="none" stroke="black" points="18,142 18,178 38,178 38,142" /><polyline fill="none" stroke="black" points="88,177 88,206 107,206 107,177" /></svg>'

    width, height, water_sources, polylines = parseData(input)
    
    has_bucket = False
    for polyline in polylines:
        if polyline["type"] == "bucket":
            has_bucket = True
    if not has_bucket:
        return json.dumps({"result": 0})

    # print(width, height, water_sources, polylines)

    polylines.append({'points': [[0, height], [width, height]], 'intersect_y': 1000000, 'watered': False, 'derived_water': [], 'type': 'pipe'})
    draw_water_sources = list()
    # calc
    global count
    count += 1
    local_count = 0
    while len(water_sources):
        # print("in loop")

        water = water_sources.pop()
        draw_water_sources.append(water)

        for polyline in polylines:
            intersect_polyline(water, polyline)
        polylines.sort(key=lambda x: x["intersect_y"])

        # print("polylines", polylines[0])
        # print(water_sources)
        # print()

        if not polylines[0]["watered"]:
            polylines[0]["watered"] = True
            water_sources += polylines[0]["derived_water"]
            water["end_y"] = polylines[0]["intersect_y"]

        # print("draw")
        # draw
        img = np.zeros((height,width,3), np.uint8)
        img += 255
        def draw(points, color=(255,0,0), line=1):
            for i in range(len(points) - 1):
                a = tuple(points[i])
                b = tuple(points[i+1])
                cv2.line(img, a, b,color,line)
        for water in draw_water_sources:
            points = [[water["cx"], water["cy"]], [water["cx"], int(water["end_y"])]]
            draw(points, (0,0,255), 1)
        for polyline in polylines:
            if polyline["type"] == "bucket" and polyline["volume"] == 0:
                draw(polyline["points"], (0, 0, 0))
            else:
                draw(polyline["points"], (0, 255, 255) if polyline["watered"] else (0,255,0))
        # print("draw_done")

        local_count += 1
        cv2.imwrite("w" + str(count) + "_" + str(local_count) + ".jpg", img)
        # cv2.imshow("w" + str(count), img)

    # print("loop done")

    volume = 0
    for polyline in polylines:
        if polyline["type"] == "bucket" and polyline["watered"]:
            volume += polyline["volume"]
    print("end", count, " ", volume)

    return json.dumps({"result": volume})