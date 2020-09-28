import logging
import json

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)


@app.route('/xerox', methods=['POST'])
def xerox():
    data = request.get_json()
    result = {}
    logging.info("data sent for evaluation {}".format(data))
    num_of_a3_copiers = data.get("num_of_a3_copiers")
    num_of_a4_copiers = data.get("num_of_a3_copiers")
    documents = data.get("documents")
    a3_copier_tracking = []
    a4_copier_tracking = []
    for i in range(num_of_a3_copiers):
        a3_copier_tracking.append(0)
    for i in range(num_of_a4_copiers):
        a4_copier_tracking.append(0)
    for documentId in documents.keys():
        if documents[documentId]["page_format"] == "A3":
            idx = a3_copier_tracking.index(min(a3_copier_tracking))
            a3CopierId = 'M' + str(idx)
            a3_copier_tracking[idx] += int(documents[documentId]["num_of_pages"]) * 5
            result[documentId] = {
                "from": 1,
                "to": documents[documentId]["num_of_pages"],
                "copier": a3CopierId
            }
        else:
            idx = a4_copier_tracking.index(min(a4_copier_tracking))
            a4CopierId = 'N' + str(idx)
            a4_copier_tracking[idx] += int(documents[documentId]["num_of_pages"]) * 3
            result[documentId] = {
                "from": 1,
                "to": documents[documentId]["num_of_pages"],
                "copier": a4CopierId
            }

    logging.info("My result :{}".format(result))
    return json.dumps(result)
