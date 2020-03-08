from hashlib import sha256
import json
import time

# BLOCK #
class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index  # Unique ID of the block
        self.transactions = transactions    # List of transactions
        self.timestamp = timestamp  # Time of generation of the block
        self.previous_hash = previous_hash  # Hash of the previous block
        self.nonce = 0  # Number that increases each time until we get a hash that satisfies our constraint

    # Returns the hash of the block
    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

# BLOCKCHAIN #
class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []  # data yet to get into Blockchain
        self.chain = []
        self.create_genesis_block()

    # Generates the Genesis Block (with index: 0, previuos_hash: 0 and a valid hash)
    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    # Get the last block (Blockchain has always at least one block, the genesis block)
    def last_block(self):
        return self.chain[-1]

    # Adds a block to the chain after some verifications:
    # check PoW and if the previuos_hash matches with the hash of the last block in the chain
    def add_block(self, block, proof):
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not self.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    # Checks if block_hash is a valid hash of the block and satisfies the difficult criteria
    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

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
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)

        self.unconfirmed_transactions = []
        return new_block.index
