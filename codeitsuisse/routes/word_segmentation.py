import logging
import json

from flask import request, jsonify

from codeitsuisse import app
from wordsegment import load, segment
load()
logger = logging.getLogger(__name__)

@app.route('/word_segmentation', methods=['POST'])
def word_segmentation():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    s = data.get("s")
    result = ' '.join(segment(s)).strip()
    logging.info("My result :{}".format(result))
    return json.dumps(result)