import logging
import json
import math

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)


def solve(search_item, item):
    # simplfy
    def simplify(search_item, item_with_symbol):
        symbols = dict()

        # dummy start
        symbol = str(len(symbols.keys()))
        symbols[symbol] = ""
        search_item_with_symbol = symbol
        item_with_symbol = symbol + item_with_symbol

        common_string = search_item[0]
        search_item = search_item[1:] if len(search_item) > 1 else ""
        while len(search_item) or len(common_string):
            # print(common_string, "|", search_item, "|", search_item_with_symbol, "|", item_with_symbol)
            if len(search_item) and item_with_symbol.find(common_string + search_item[0]) != -1:
                common_string += search_item[0]
                search_item = search_item[1:] if len(search_item) > 1 else ""
                continue

            if len(common_string) > 2:
                symbol = str(len(symbols.keys()))
                symbols[symbol] = common_string
                search_item_with_symbol += symbol
                item_with_symbol = item_with_symbol.replace(common_string, symbol)
                common_string = search_item[0] if len(search_item) > 0 else ""
                search_item = search_item[1:] if len(search_item) > 1 else ""
                continue

            search_item_with_symbol += common_string
            common_string = search_item[0] if len(search_item) > 0 else ""
            search_item = search_item[1:] if len(search_item) > 1 else ""

        # dummy end
        symbol = str(len(symbols.keys()))
        symbols[symbol] = ""
        search_item_with_symbol += symbol
        item_with_symbol += symbol

        # print("search_item_with_symbol", search_item_with_symbol)
        # print("item_with_symbol", item_with_symbol)
        # print("symbols", symbols)

        return search_item_with_symbol, item_with_symbol, symbols

    def compare(search_item, item):
        basket = [(search_item, item, "", 0)]
        found = list()
        while (len(basket)):
            search_item, item, result, no_operation = basket.pop()
            if len(search_item) == 0 and len(item) == 0:
                found.append([result, no_operation])
                continue
            if len(search_item) > 0 and len(item) == 0:
                for c in search_item:
                    result += '-' + c
                    no_operation += 1
                found.append([result, no_operation])
                continue
            if len(search_item) == 0 and len(item) > 0:
                for c in item:
                    result += '+' + c
                    no_operation += 1
                found.append([result, no_operation])
                continue
            if search_item[0].lower() == item[0].lower():
                basket.append((search_item[1:], item[1:], result+item[0], no_operation))
                continue
            
            # insertion
            basket.append((search_item, item[1:], result + '+' + item[0], no_operation+1))

            # substitution
            basket.append((search_item[1:], item[1:], result + item[0], no_operation+1))

            # remove
            basket.append((search_item[1:], item, result + '-' + search_item[0], no_operation+1))

        found.sort(key=lambda x: x[0], reverse=True)
        found.sort(key=lambda x: x[1])
        # print("found", found)
        return found[0]

    search_item_with_symbol, item_with_symbol, symbols = simplify(search_item, item)

    item_out_with_symbol = ""
    no_operation = 0
    for i in range(len(symbols.keys()) - 1):
        search_item_left = search_item_with_symbol.find(str(i)) + 1
        search_item_right = search_item_with_symbol.find(str(i+1))
        sub_search_item = search_item_with_symbol[search_item_left:search_item_right]

        item_left = item_with_symbol.find(str(i)) + 1
        item_right = item_with_symbol.find(str(i+1))
        sub_item = item_with_symbol[item_left:item_right]

        # print("sub_search_item", sub_search_item)
        # print("sub_item", sub_item)

        # last character is intended lost
        found = compare(sub_search_item, sub_item)
        item_out_with_symbol += str(i) + found[0]
        no_operation += found[1]
        # print(found)

    # print(search_item_with_symbol)
    # print(item_with_symbol)
    # print(item_out_with_symbol)

    item_out = ""
    for c in item_out_with_symbol:
        if c.isdigit():
            item_out += symbols[c]
        else:
            item_out += c
    # print(item_out, item, no_operation)
    return item_out, item, no_operation

# search_item = "atrgdzoqswycqqwqfpidvexvewjjesgeupawmruvxorcnicdmri"
# item = "atrgzoqsycvfwvqfpidvexavewrjjesgeupamruvxornicdmri"

# item_out, item, no_operation = solve(search_item, item)

@app.route('/inventory-management', methods=['POST'])
def inventory_management():
    data = request.get_json()

    with open("in" + '.json', 'w') as outfile:
        json.dump(data, outfile)

    outAll = list()
    for input in data:        
        result_found = list()
        search_item = input["searchItemName"]

        with open(search_item + '.json', 'w') as outfile:
            json.dump(input, outfile)

        for item in input["items"]:
            item_out, item, no_operation = solve(search_item, item)
            result_found.append([item_out, item, no_operation])

        result_found.sort(key=lambda x: x[1], reverse=False) # sort by item
        result_found.sort(key=lambda x: x[2], reverse=False) # sort by operation
        original_item = [result[1] for result in result_found]
        no_operation = [result[2] for result in result_found]
        result_found = [result[0] for result in result_found]

        if len(result_found) > 10:
            result_found = result_found[:10]
            no_operation = no_operation[:10]
            original_item = original_item[:10]
        outAll.append({"searchItemName": search_item, "searchResult":result_found, "no_operation": no_operation, "original_item": original_item})

        with open(search_item  + "_out" + '.json', 'w') as outfile:
            json.dump(outAll, outfile)

    with open("out" + '.json', 'w') as outfile:
        json.dump(outAll, outfile)

    return json.dumps(outAll)
