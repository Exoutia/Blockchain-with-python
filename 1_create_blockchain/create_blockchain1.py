# Module 1: create a blockchain AZ blockchain
# first we installed flask==0.12.2
# and now we are installing api builder i guess, a app called postman(people give great name in developer community)

import datetime
import hashlib
import json
from flask import Flask, jsonify

# Part 1 - Building a Blockchain
class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, prev_hash = '0')
        
    def create_block(self, proof, prev_hash):
        block = {'index': (len(self.chain) + 1),
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'prev_hash': prev_hash}
        self.chain.append(block)
        return block
    
    def get_prev_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, prev_proof):
        new_proof = 1;
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**3 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] == "0000":
                check_proof = True
            else: 
                new_proof +=1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys= True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
         prev_block = chain[0]
         block_index = 1
         while block_index < len(chain):
             block = chain[block_index]
             if block['prev_hash'] != self.hash(prev_block):
                 return False
             prev_proof = prev_block['proof']
             proof = block['proof']
             hash_operation = hashlib.sha256(str(proof**3 - prev_proof**2).encode()).hexdigest()
             if hash_operation[:4] != '0000':
                 return False
             prev_block= block
             block_index += 1
         return True

# Part 2 - Mining Our Blockchain

# Creating a Web App
app = Flask(__name__)

# Creating a Blockchain
blockchain = Blockchain()

# MIning a new blockchain
@app.route('/mine_block', methods= ['GET'])
def mine_block():
    previous_block = blockchain.get_prev_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': "Congratulation, you just mined a block!", 
                'index':block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'prev_hash': block['prev_hash']}
    return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods= ['GET'])
def get_chain():
    response = {'chain': blockchain.chain, 
                'Number of blocks': len(blockchain.chain)}
    return jsonify(response), 200

# Checking if the blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houton, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200

# Running the app
app.run(host ='0.0.0.0', port=5000)


















