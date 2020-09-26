import logging
import json

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)

count = 0
@app.route('/optimizedportfolio', methods=['POST'])
def optimizedportfolio():
    input = request.get_json()
    global count
    count += 1
    with open('in' + str(count) + '.json', 'w') as outfile:
        json.dump(input, outfile)

    outputs = list()
    for case in input["inputs"]:
        portfolio = case["Portfolio"]
        index_futures = case["IndexFutures"]
        case_output = list()
        for index in index_futures:
            ratio = 1.0 * index["CoRelationCoefficient"] * portfolio["SpotPrcVol"] / index["FuturePrcVol"]
            num = 1.0 * round(ratio, 3) * portfolio["Value"] / (index["IndexFuturePrice"] * index["Notional"])
            case_output.append({
                "FuturePrcVol": index["FuturePrcVol"],
                "HedgePositionName": index["Name"],
                "OptimalHedgeRatio": round(ratio, 3),
                "NumFuturesContract": round(num)
            })

        case_output.sort(key=lambda x: x["NumFuturesContract"])
        case_output.sort(key=lambda x: x["FuturePrcVol"])
        case_output.sort(key=lambda x: x["OptimalHedgeRatio"])

        # for index in case_output:
            # print(index)

        outputs.append(case_output[0])
    # print(outputs)

    return json.dumps({"outputs": outputs})