import datetime
import json

import requests
from flask import render_template, redirect, request

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


# Main endpoint
@app.route('/', methods=['GET'])
def index():
    chain, length = fetch_blockchain()
    return render_template('index.html',
                           title='Blockchain',
                           number_of_block=length,
                           genesis_block=chain[0],
                           node_address=CONNECTED_NODE_ADDRESS)


# Main endpoint
@app.route('/old', methods=['GET'])
def index_old():
    fetch_posts()
    return render_template('index2.html',
                           title='Blockchain index',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)

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
