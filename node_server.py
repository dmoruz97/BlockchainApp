from hashlib import sha256
import json
import time
import os

from flask import Flask, request


# BLOCK #
class Block:
    def __init__(self, index, transactions=[], timestamp=time.time(), previous_hash=""):
        self.index = index  # Unique ID of the block
        self.transactions = transactions    # List of transactions
        self.timestamp = timestamp  # Time of generation of the block
        self.previous_hash = previous_hash  # Hash of the previous block
        self.nonce = 0  # Number that increases each time until we get a hash that satisfies our constraint

    def check_genesis(self):
        return self.transactions == [] and self.index == 0 and self.previous_hash == "0"

    # Returns the hash of the block
    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

    # Saves to file the block
    def save_to_file(self):
        json_block = self.to_json()
        with open("blocks/block{}.json".format(self.index), 'w+') as f:
            json.dump(json_block, f, sort_keys=True)
        print("Block #{} saved to file".format(self.index))

    # Loads from file the block
    def load_from_file(self):
        if os.path.isfile("blocks/block{}.json".format(self.index)):
            with open("blocks/block{}.json".format(self.index), 'r') as f:
                d = json.load(f)
                self.__dict__ = d 
                return True
            return False
        else:
            print("File {} with block not found!".format(self.index))
            return False

    # Returns block in JSON format
    def to_json(self):
        return {
            "index": self.index, 
            "transactions": self.transactions, 
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }


# BLOCKCHAIN #
class Blockchain:

    difficulty = 2  # difficulty of our PoW algorithm
    MAX_TRANSACTIONS_PER_BLOCK = 1000
    MAX_K = 100

    def __init__(self):
        self.unconfirmed_transactions = []  # data yet to get into Blockchain
        self.chain = []
        self.load_blockchain(self.MAX_K)

    # K iniziale 100 leggi solo 100 e quando mini togli la prima, metodo per leggere k blocchi da disco
    def load_blockchain(self, k):
        i = 0
        nblocks = 0
        found = True
        while found:
            if os.path.isfile("blocks/block{}.json".format(i)):
                nblocks += 1
            else:
                if i == 0:
                    self.create_genesis_block()
                found = False
            i = i+1

        print("Found {} blocks".format(i))
        for i in range(nblocks-k, nblocks):
            print(i)
            block = Block(i)
            block.load_from_file()
            if i == 0:
                if block.check_genesis():
                    print("Found genesis")
                    block.hash = block.compute_hash()
                    self.chain.append(block)
                else:
                    break;
            else:
                res = self.add_block(block, block.compute_hash())
                if not res : break
        print("Loaded {} blocks".format(len(self.chain)))

    # Generates the Genesis Block (with index: 0, previous_hash: 0 and a valid hash)
    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.save_to_file()
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    # Get the last block (Blockchain has always at least one block, the genesis block)
    def last_block(self):
        return self.chain[-1]

    # Adds a block to the chain after some verifications:
    # check PoW and if the previuos_hash matches with the hash of the last block in the chain
    def add_block(self, block, proof):
        if len(self.chain) > 0:
            last_hash = self.last_block.hash
            if last_hash != block.previous_hash:
                return False

        if not self.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        print("added block{} with {} transactions".format(block.index, len(block.transactions)))

        return True

    # Checks if block_hash is a valid hash of the block and satisfies the difficult criteria
    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and block_hash == block.compute_hash())

    # Functions that tries different values of nonce to get a hash which satisfies the difficulty criteria
    def proof_of_work(self, block):
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    # Interfaces to add the pending transaction to the Blockchain, by adding them to the block and compute the PoW
    def mine(self):
        if not self.unconfirmed_transactions:   # There are no transactions to be mined
            return False

        if len(self.unconfirmed_transactions) > self.MAX_TRANSACTIONS_PER_BLOCK:   # There too much transactions to be mined for a block
            transactions_temp = self.unconfirmed_transactions[:self.MAX_TRANSACTIONS_PER_BLOCK]
        else:
            transactions_temp = self.unconfirmed_transactions

        last_block = self.last_block
        print("Last index{}".format(last_block.index))

        new_block = Block(index=last_block.index + 1,
                          transactions=transactions_temp,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        new_block.save_to_file()
        self.add_block(new_block, proof)
        if len(self.chain)>blockchain.MAX_K:
            self.chain.pop(0)

        if len(self.unconfirmed_transactions) > self.MAX_TRANSACTIONS_PER_BLOCK:
            self.unconfirmed_transactions = self.unconfirmed_transactions[self.MAX_TRANSACTIONS_PER_BLOCK+1:]
        else:
            self.unconfirmed_transactions = []

        return new_block.index


def load_blocks(start, k):
    blocks=[]
    end = start-k if start-k >= 0 else 0
    for i in range(end, start):
        if os.path.isfile("blocks/block{}.json".format(i)):
            block = Block(i)
            block.load_from_file()
            blocks.append(block)
    return blocks


def get_blockchain():
    return blockchain

if __name__ == '__main__':

    global blockchain
    # Initialize the Blockchain object
    blockchain = Blockchain()

# Initialize flask application
app = Flask(__name__)

### ENDPOINTS ###

# Get a copy of the blockchain
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data), "chain": chain_data})


# Mine unconfirmed transactions
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    return "Block #{} is mined.".format(result)


# Retrieve a transaction with id_transaction
@app.route('/get_transaction', methods=['GET'])
def get_transaction_by_id():
    t = {}
    t_id = request.args.get('id_transaction')

    for block in blockchain.chain:
        for transaction in block.transactions:
            if transaction["TRANSACTION_ID"] == int(t_id):
                t = transaction
    if t == {}:
        return "Transaction absent"
    else:
        return t


# Retrieve all the transactions of a block with id_block
@app.route('/get_all_transaction_in_block', methods=['GET'])
def get_all_transaction():
    transactions = []

    for block in blockchain.chain:
        if int(block.index) == int(request.args.get('id_block')):
            transactions = block.transactions
            break

    if transactions == []:
        return "No transactions in this block"
    else:
        return {"res" : transactions}


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


# FOR PEERS [not yet implemented] #

# the address to other participating members of the network
peers = set()


# endpoint to add new peers to the network.
@app.route('/add_nodes', methods=['POST'])
def register_new_peers():
    nodes = request.get_json()
    if not nodes:
        return "Invalid data", 400
    for node in nodes:
        peers.add(node)

    return "Success", 201


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def validate_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],block_data["transactions"],block_data["timestamp"],block_data["previous_hash"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


app.run(debug=False, port=8000)
