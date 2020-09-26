import logging
import json
import math

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)


@app.route('/revisitgeometry', methods=['POST'])
def revisitgeometry():
    data = request.get_json()
    logging.info("revisitgeometry")
    logging.info(data)

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

    lineCoordinates = data["lineCoordinates"]
    line_slope, line_intercept = to_slope_intercept(lineCoordinates[0], lineCoordinates[1])
    logging.info(line_slope)
    logging.info(line_intercept)

    intersection_points = list()
    last_pt = data["shapeCoordinates"][-1]
    for pt in data["shapeCoordinates"]:

        shape_slope, shape_intercept = to_slope_intercept(pt, last_pt)
        intersect = get_intersection(line_slope, line_intercept, shape_slope, shape_intercept)
        if len(intersect) and check_inbound(pt, last_pt, intersect[0]):
            intersect[0]['x'] = round(intersect[0]['x'], 2)
            intersect[0]['y'] = round(intersect[0]['y'], 2)
            intersection_points += intersect

        logging.info("x")
        logging.info(pt)
        logging.info(last_pt)
        logging.info(shape_slope)
        logging.info(shape_intercept)
        logging.info(intersection_points)

        last_pt = pt

    return json.dumps(intersection_points)

