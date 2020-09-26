import logging
import json

from flask import request, jsonify
from mknapsack.algorithms import mtm
from codeitsuisse import app

logger = logging.getLogger(__name__)


@app.route('/olympiad-of-babylon', methods=['POST'])
def olympiadOfBabylon():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    numberOfBooks = data.get("numberOfBooks")
    numberOfDays = data.get("numberOfDays")
    books = data.get("books")
    days = data.get("days")
    profits = [1 for _ in range(numberOfBooks)]
    result, _, _, _ = mtm(profits, books, days)
    result = {
        "optimalNumberOfBooks": result
    }

    logging.info("My result :{}".format(result))
    return json.dumps(result)
