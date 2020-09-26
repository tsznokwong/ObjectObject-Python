import logging
import json
import operator as op

from functools import reduce
from flask import request

from codeitsuisse import app

logger = logging.getLogger(__name__)


def ncr(n, r):
    r = min(r, n - r)
    numer = reduce(op.mul, range(n, n - r, -1), 1)
    denom = reduce(op.mul, range(1, r + 1), 1)
    return int(numer / denom)


def combination(seats, people, spaces):
    seats_remaining = seats - people - (people - 1) * spaces
    return ncr(seats_remaining + people, seats_remaining)


@app.route('/social_distancing', methods=['POST'])
def social_distancing():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    tests = data.get("tests")
    answers = {}
    for test in tests.keys():
        answers[test] = combination(tests[test]["seats"], tests[test]["people"], tests[test]["spaces"])
    result = {
        "answers": answers
    }
    logging.info("My result :{}".format(result))
    return json.dumps(result)
