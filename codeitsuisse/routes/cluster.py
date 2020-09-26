import logging
import json
from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)

count = 0
@app.route('/cluster', methods=['POST'])
def cluster():
    global count
    area = request.get_json()
    logging.info("cluster")

    # replace all target by replacement
    def area_setter(area, x, y, replacement, target):
        hit = False
        h = len(area)
        w = len(area[0])

        if x != 0:
            if y != 0 and area[y-1][x-1] == target:
                hit = True
                area[y-1][x-1] = replacement
            if area[y][x-1] == target:
                hit = True
                area[y][x-1] = replacement
            if y != h-1 and area[y+1][x-1] == target:
                hit = True
                area[y+1][x-1] = replacement

        if y != 0 and area[y-1][x] == target:
            hit = True
            area[y-1][x] = replacement
        if y != h-1 and area[y+1][x] == target:
            hit = True
            area[y+1][x] = replacement

        if x != w-1:
            if y != 0 and area[y-1][x+1] == target:
                hit = True
                area[y-1][x+1] = replacement
            if area[y][x+1] == target:
                hit = True
                area[y][x+1] = replacement
            if y != h-1 and area[y+1][x+1] == target:
                hit = True
                area[y+1][x+1] = replacement
        return hit

    # spread virus
    def spread_virus(area, replacement, target):
        is_spreading = True
        while is_spreading:
            is_spreading = False
            for y in range(len(area)):
                for x in range(len(area[0])):
                    if area[y][x] == replacement:
                        hit = area_setter(area, x, y, replacement, target)
                        is_spreading = is_spreading or hit
            
    # identify cluster
    def identify_cluster(area):
        need_cluster = True
        no_cluster = 0
        while need_cluster:
            need_cluster = False
            for y in range(len(area)):
                for x in range(len(area[0])):
                    if area[y][x] == '1':
                        area[y][x] = no_cluster
                        spread_virus(area, no_cluster, '1')
                        no_cluster += 1
        return no_cluster

    spread_virus(area, '1', '0')
    answer = identify_cluster(area)

    with open(str(count) + "_" + str(answer) + '.json', 'w') as outfile:
        json.dump(area, outfile)
    count += 1

    return json.dumps({"answer": answer})