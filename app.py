import flask 
import jsonify
import requests
from dotenv import load_dotenv
import os
from flask_cors import CORS
from ebay_oauth_token import OAuthToken 

app = flask.Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

load_dotenv()

client_id = os.getenv("EBAY_APP_ID")
client_secret = os.getenv("EBAY_CERT_ID")
oauth_utility = OAuthToken(client_id, client_secret)
application_token = oauth_utility.getApplicationToken()

@app.route('/'):
def index():
    return "Hello World"

@app.route('/get-orders/<keywords>/<int:min_price>/<int:max_price>/<condition>/<if_returns>/<if_free_ship>/<if_exp_ship>/<sort>')
def get_orders(keywords, min_price, max_price, condition, if_returns, if_free_ship, if_exp_ship, sort):
    if flask.request.method == "OPTIONS":
        return flask.make_response("", 204)

    if flask.request.method == 'GET':
        # Get all orders from database
        order_list = requests.get(find_order_url(
            keywords, min_price, max_price, condition, if_returns, if_free_ship, if_exp_ship, sort
        ))
        return flask.jsonify(order_list.json())

def find_order_url(keywords, min_price, max_price, conditions, if_returns, \
                   if_free_ship, if_exp_ship, sort):
    url = "https://svcs.ebay.com/services/search/FindingService/v1?" + \
        "OPERATION-NAME=findItemsAdvanced&" + \
        "SERVICE-VERSION=1.0.0&" + \
        "SECURITY-APPNAME=" + str(os.getenv("EBAY_APP_ID")) + "&" \
        "RESPONSE-DATA-FORMAT=JSON&" + \
        "REST-PAYLOAD&" + \
        "keywords=" + keywords + "&" + \
        "sortOrder=" + sort + "&" + \
        "itemFilter(0).name=Currency&itemFilter(0).value=USD&" + \
        "itemFilter(1).name=MinPrice&itemFilter(1).value=" + str(min_price) + "&" + \
        "itemFilter(2).name=MaxPrice&itemFilter(2).value=" + str(max_price) + "&" + \
        "itemFilter(3).name=ReturnsAcceptedOnly&itemFilter(3).value=" + str(if_returns).lower() + "&" + \
        "itemFilter(4).name=FreeShippingOnly&itemFilter(4).value=" + str(if_free_ship).lower() + "&" +\
        "itemFilter(5).name=Condition&" \

        
    conditions = conditions.split(",")
    for ind, condition in enumerate(conditions):
        cond_num = 0
        if condition == "new":
            cond_num = 1000
        elif condition == "used":
            cond_num = 3000
        elif condition == "very-good":
            cond_num = 4000
        elif condition == "good":
            cond_num = 5000
        elif condition == "acceptable":
            cond_num = 6000
        else:
            continue
        url += f"itemFilter(5).value({ind})={cond_num}&"

        # not being tested according to piazza post https://piazza.com/class/lkyn4sr3nlj3/post/121
    # if if_exp_ship == "true":
    #     url += f"itemFilter(6).name=ExpeditedShippingType&itemFilter(6).value=Expedited&"

    return url[:-1]



@app.route("/get-single-item/<int:id>")
def get_order_info(id):
    if flask.request.method == "GET":
        headers = {
            "X-EBAY-API-IAF-TOKEN": oauth_utility.getApplicationToken()
        }

        url = "https://open.api.ebay.com/shopping?" + \
                "callname=GetSingleItem&" + \
                "responseencoding=JSON&" + \
                "appid="+os.getenv("EBAY_APP_ID") + "&" + \
                "siteid=0&" + \
                "version=967&" + \
                "ItemID=" + str(id) + "&" + \
                "IncludeSelector=Description,Details,ItemSpecifics"

        item_info = requests.get(url, headers=headers)

        return flask.jsonify(item_info.json())


if __name__ == "__main__":
    app.run(debug=True, port=5010)

