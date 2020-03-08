from flask import Flask, request
import requests
from node_server import Blockchain
import time
import json

# Initialize flask application
app = Flask(__name__)

# Initialize a blockchain object.
blockchain = Blockchain()


# Add a new transaction
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["TRANSACTION_ID", "YEAR", "DAY_OF_WEEK", "FL_DATE", "OP_CARRIER_AIRLINE_ID", "OP_CARRIER_FL_NUM",
                       "ORIGIN_AIRPORT_ID", "ORIGIN", "ORIGIN_CITY_NAME", "ORIGIN_STATE_NM", "DEST_AIRPORT_ID", "DEST",
                       "DEST_CITY_NAME", "DEST_STATE_NM", "DEP_TIME", "DEP_DELAY", "ARR_TIME", "ARR_DELAY", "CANCELLED",
                       "AIR_TIME"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)

    return "Success", 201


# Retrieve a transaction based on the transaction_id
@app.route('/get_transaction', methods=['GET'])
def get_transaction_by_id():
    t = {}
    for block in blockchain.chain:
        for transaction in block.transactions:
            if transaction["TRANSACTION_ID"] == request.args.get('id_transaction'):
                t = transaction
                break

    if t == {}:
        return "Transaction absent"
    else:
        return t


# Retrieve all the transaction of a block
@app.route('/get_all_transaction', methods=['GET'])
def get_all_transaction():
    transactions = []
    for block in blockchain.chain:
        if block.index == request.args.get('id_block'):
            transactions = block.transactions
            break

    return transactions


# Get a copy of the chain
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})


# Mine unconfirmed transactions
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    return "Block #{} is mined.".format(result)


@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)
