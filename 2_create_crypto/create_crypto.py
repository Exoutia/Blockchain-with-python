# Here we are going to use same blockchain we created to make a cyptocurrency on it 
# Decentralising Blockchain
#TODO Make a vive crypto currency(Yes thats the name i have given to my crypto)
# first we installed flask==0.12.2
# and now we are installing api builder i guess, a app called postman(people give great name in developer community)
# requests==2.18.4 library install

from crypt import methods
import datetime
from email import message
import hashlib
import json
from urllib import response
from flask import Flask, jsonify, request
import requests 
from uuid import uuid4
from urllib.parse import urlparse

from sqlalchemy import false

#* Part 1 - Building a Blockchain
class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, prev_hash = '0')
        self.nodes = set()
        
    def create_block(self, proof, prev_hash):
        block = {'index': (len(self.chain) + 1),
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'prev_hash': prev_hash,
                 'transaction': self.transactions}
        del self.transactions[:]
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
     
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender':sender,
                                  'receiver':receiver,
                                  'amount':amount})
        previous_block = self.get_prev_block()
        return(previous_block['index'] + 1)
    
    def add_node(self, node_address):
        parsed_url = urlparse(node_address)
        self.nodes.add(parsed_url.netloc)
   
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f"http://{node}/get_chain")
            if response.status_code == 200:
                length = response.json()['Number of blocks']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return false

#* Part 2 - Mining Our Blockchain

# Creating a Web App
app = Flask(__name__)


# creating an address for the node on port 5000
node_address = str(uuid4()).replace('-', '')


# Creating a Blockchain
blockchain = Blockchain()

# MIning a new blockchain
@app.route('/mine_block', methods= ['GET'])
def mine_block():
    previous_block = blockchain.get_prev_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address, receiver='Hunter', amount=1)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': "Congratulation, you just mined a block!", 
                'index':block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'prev_hash': block['prev_hash'],
                'transactions': block['transactions'],
                }
    
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
    
# Adding a new transaction to the blockchain
@app.route('/add_transanction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transanction is missing.', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to block {index}'}
    return jsonify(response), 201
    
    
#* Part 3 - Decentralising our blockchain 

# Connecting new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('node')
    if nodes is None:
        return 'No node', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are connected. The vivecoin Blockchain now contains the following nodes:',
                'total_nodes':list(blockchain.nodes)}
    return jsonify(response), 201
        

# Running the app
app.run(host ='0.0.0.0', port=5000)

















