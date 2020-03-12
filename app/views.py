import datetime
import json

import requests
from flask import render_template, redirect, request, url_for

from app import app


# Node in the blockchain network that our application will communicate with to fetch and add data.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []


# Fetch the chain from a blockchain node, parse the data, and store it locally.
def fetch_posts():
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'], reverse=True)


def fetch_blockchain():
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        chain = json.loads(response.content)
        return chain["chain"], chain["length"]


# Recap of Blockchain endpoint
@app.route('/about', methods=['GET'])
def index_old():
    fetch_posts()
    """return render_template('about_blockchain.html',
                           title='Blockchain',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)"""


# Main endpoint
@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def index():
    chain, length = fetch_blockchain()
    return render_template('index.html',
                           title='Blockchain',
                           number_of_block=length,
                           genesis_block=chain[0],
                           node_address=CONNECTED_NODE_ADDRESS)


# Add new record to the chain (point 4.1 of the assignment)
@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    if request.method == 'GET':
        if 'success' in request.args:
            success = request.args.get('success')
        else:
            success = ""

        return render_template('add_record.html',
                               title='Add new record',
                               success=success)

    if request.method == 'POST':
        tran = {"TRANSACTION_ID": request.form.get('transaction_id'),
                "YEAR": request.form.get('year'),
                "DAY_OF_WEEK": request.form.get('day_of_week'),
                "FL_DATE": request.form.get('flight_date'),
                "OP_CARRIER_AIRLINE_ID": request.form.get('op_carrier_airline_id'),
                "OP_CARRIER_FL_NUM": request.form.get('op_carrier_fl_num'),
                "ORIGIN_AIRPORT_ID": request.form.get('original_airport_id'),
                "ORIGIN": request.form.get('origin'),
                "ORIGIN_CITY_NAME": request.form.get('origin_city_name'),
                "ORIGIN_STATE_NM": request.form.get('origin_state_nm'),
                "DEST_AIRPORT_ID": request.form.get('dest_airport_id'),
                "DEST": request.form.get('dest'),
                "DEST_CITY_NAME": request.form.get('dest_city_name'),
                "DEST_STATE_NM": request.form.get('dest_state_nm'),
                "DEP_TIME": request.form.get('dep_time'),
                "DEP_DELAY": request.form.get('dep_delay'),
                "ARR_TIME": request.form.get('arr_time'),
                "ARR_DELAY": request.form.get('arr_delay'),
                "CANCELLED": request.form.get('cancelled'),
                "AIR_TIME": request.form.get('air_time')
                }

        data = json.dumps(tran)
        headers = {'Content-type': 'application/json'}
        address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)
        response = requests.post(address, headers=headers, data=data)

        if response.status_code == 201:
            params = {'success': 'Record successfuly added!'}
            response = requests.get('http://127.0.0.1:5000/add_record', params=params)
        else:
            params = {'success': 'Record NOT added!'}
            response = requests.get('http://127.0.0.1:5000/add_record', params=params)

        return response.text


# Query the average delay of a flight carrier in a certain interval of time (point 4.3 of the assignment)
@app.route('/query_delay', methods=['GET', 'POST'])
def query_delay():
    if request.method == 'GET':
        if 'delay' in request.args:
            delay = request.args.get('delay')
        else:
            delay = ""

        return render_template('query_delay.html',
                               title='Query delay',
                               delay=delay)

    if request.method == 'POST':
        carrier = request.form.get("op_carrier_fl_num")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")

        copy_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
        response = requests.get(copy_chain_address)
        blockchain = response.json()

        count: int = 0
        total_delay = 0

        for block in blockchain['chain']:
            for transaction in block['transactions']:
                if (transaction['OP_CARRIER_FL_NUM'] == carrier) and (start_time <= transaction['FL_DATE'] <= end_time):
                    if transaction["ARR_DELAY"] > 0:    # There are also ARR_DELAY negative (flight arrived in advance)
                        count = count+1
                        total_delay = total_delay + transaction["ARR_DELAY"]    # Considered only the arrival delay

        if count != 0:
            average_delay = total_delay/count
            info = 'Average delay: {} seconds'.format(average_delay)
        else:
            info = 'No matches!'

        params = {'delay': info}
        response = requests.get('http://127.0.0.1:5000/query_delay', params=params)

        return response.text


# Route for query status (point 4.2 of the assignment)
@app.route('/query_status', methods=['GET'])
def query_status():
    return render_template('query_status.html',
                           title='Query status of a flight'
                          )


# Endpoint to get the status
# @params:
# - date
# - op_carrier_airline_id
@app.route('/get_status_from_airline_and_date', methods=['POST'])
def get_status_from_airline_and_date():

    # date with the schema: yyyy-mm-dd
    global status
    date = request.form["date"]
    op_carrier_airline_id = request.form["op_carrier_airline_id"]

    # search status
    copy_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(copy_chain_address)
    blockchain = response.json()

    print(blockchain)

    find = False

    for block in blockchain['chain']:
        for transaction in block['transactions']:
            if transaction['date'] == date and transaction['op_carrier_airline_id']:
                status = transaction.status
                find = True

    if find:
        return status
    else:
        return "null"


# Endpoint to create a new transaction via our application
@app.route('/submit', methods=['POST'])
def submit_textarea():
    post_content = request.form["content"]

    post_object = {
        'content': post_content
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address, json=post_object, headers={'Content-type': 'application/json'})

    # Return to the homepage
    return redirect('/')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
