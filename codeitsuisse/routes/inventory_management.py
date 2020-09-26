import logging
import json
import math

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)


@app.route('/inventory-management', methods=['POST'])
def inventory_management():
    data = request.get_json()
    logging.info("inventory-management")
    logging.info(data)

    found = list()
    def diverge(remaining_search_item, remaining_item, constructed="", no_operation=0):
        # print(remaining_search_item, remaining_item, constructed, no_operation)

        if len(remaining_search_item) == 0 and len(remaining_item) == 0:
            # terminating case
            found.append([remaining_search_item, remaining_item, constructed, no_operation])
        
        elif len(remaining_search_item) > 0 and len(remaining_item) == 0:
            # only remaining_search_item left
            diverge(
                remaining_search_item[1:], 
                remaining_item, 
                constructed + "-" + remaining_search_item[0], 
                no_operation + 1
            )
            
        elif len(remaining_search_item) == 0 and len(remaining_item) > 0:
            # only remaining_item left
            diverge(
                remaining_search_item, 
                remaining_item[1:], 
                constructed + "+" + remaining_item[0],
                no_operation + 1
            )
            
        elif remaining_item[0].lower() == remaining_search_item[0].lower():
            # exact match
            # print("3", remaining_search_item, remaining_item, constructed, no_operation)
            diverge(
                remaining_search_item[1:], 
                remaining_item[1:], 
                constructed + remaining_item[0],
                no_operation
            )
        
        elif len(remaining_item) > 1 and remaining_item[1].lower() == remaining_search_item[0].lower():
            # try insertion
            # print("4.1", remaining_search_item, remaining_item[1:], constructed + '+' + remaining_item[0], no_operation+1)
            diverge(
                remaining_search_item,
                remaining_item[1:],
                constructed + '+' + remaining_item[0],
                no_operation + 1
            )

        elif len(remaining_search_item) > 1 and remaining_item[0].lower() == remaining_search_item[1].lower():
            # try deletion
            # print("6", remaining_search_item[1:], remaining_item, constructed + "-" + remaining_search_item[0], no_operation+1)
            diverge(
                remaining_search_item[1:],
                remaining_item,
                constructed + "-" + remaining_search_item[0],
                no_operation + 1
            )

        elif len(remaining_search_item) > 1 and len(remaining_item) > 1 and remaining_item[1].lower() == remaining_search_item[1].lower():
            # try substitution
            # print("5.1", remaining_search_item[1:], remaining_item[1:], constructed + remaining_item[0], no_operation+1)
            diverge(
                remaining_search_item[1:],
                remaining_item[1:],
                constructed + remaining_item[0],
                no_operation + 1
            )

        else:
            # try insertion
            # print("4.1", remaining_search_item, remaining_item[1:], constructed + '+' + remaining_item[0], no_operation+1)
            diverge(
                remaining_search_item,
                remaining_item[1:],
                constructed + '+' + remaining_item[0],
                no_operation + 1
            )

            # try substitution
            # print("5", remaining_search_item[1:], remaining_item[1:], constructed + remaining_item[0], no_operation+1)
            diverge(
                remaining_search_item[1:],
                remaining_item[1:],
                constructed + remaining_item[0],
                no_operation + 1
            )

            # try deletion
            # print("6", remaining_search_item[1:], remaining_item, constructed + "-" + remaining_search_item[0], no_operation+1)
            diverge(
                remaining_search_item[1:],
                remaining_item,
                constructed + "-" + remaining_search_item[0],
                no_operation + 1
            )

    data = data[0]
    result_found = list()
    search_item = data["searchItemName"]
    for item in data["items"]:
        found = list()
        search_item = search_item.lower()
        item = item.lower()
        diverge(search_item, item)
        found.sort(key=lambda x: x[3])
        result_found.append(found[0][2:])
    result_found.sort(key=lambda x: x[0]) # sort by alphatic
    result_found.sort(key=lambda x: x[1]) # sort by operation
    result_found = [result[0] for result in result_found]
    if len(result_found) > 10:
        result_found = result_found[:10]
    return json.dumps(result_found)