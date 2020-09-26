import logging
import json
import numpy
from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)

count = 0
data_to_save = list()
@app.route('/swaphedge', methods=['POST'])
def swaphedge():
    input = request.get_json()
    global count
    count += 1
    with open('in' + str(count) + '.json', 'w') as outfile:
        json.dump(input, outfile)

    t = input["time"]
    bid = input["bid"]
    ask = input["ask"]
    accu_order = input["accu_order"]
    our_position = input["our_position"]
    balance = input["balance"]
    client_balance = input["client_balance"]
    client_order = input["order"]

    # for debug
    O2 = 0.29
    P2 = 0.61
    our_order = -int(-client_order*O2+(accu_order-our_position)*P2)
    if our_order < 8:
        our_order = 0

    global data_to_save
    data_to_save.append([t, bid, ask, accu_order, our_position, balance, client_balance, client_order, our_order])

    if t == 30:
        data_to_save = numpy.asarray(data_to_save)
        numpy.savetxt("out.txt", data_to_save, delimiter=",")
        data_to_save = list()

    return json.dumps({'order': our_order})
