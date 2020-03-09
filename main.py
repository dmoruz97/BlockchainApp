import json
import requests
import time
import threading
import csv
from app import app


# Add transaction to blockchain
def add_transaction_to_blockchain():
    headers = {'Content-type': 'application/json'}

    # Read transaction from CSV file (Each transaction is in JSON form (key => value))
    transactions = read_csv()

    for t in transactions:
        data = json.dumps(t)
        print(data)

        response = requests.post('http://127.0.0.1:8000/new_transaction', headers=headers, data=data)
        print(response)

        break

    r = requests.get('http://127.0.0.1:8000/mine')
    print(r.text)

# Function that reads the CSV file and return a list of the rows inside it
def read_csv():
    csv_file = "656211699_T_ONTIME_REPORTING.csv"
    rows = []

    with open(csv_file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        count_row = 0
        for row in csv_reader:
            if count_row == 0:
                header = row
                del header[-1]  # due to an empty column read at the last of each row
            else:
                transaction = {"TRANSACTION_ID": count_row}
                for i, value in enumerate(row[:-1], 0):
                    transaction[header[i]] = value
                rows.append(transaction)
            count_row = count_row + 1

    print("Total rows in CSV: {}".format(len(rows)))
    return rows


# Thread that mines every minute
def mine():
    while True:
        print("Mining")
        r = requests.get('http://127.0.0.1:8000/mine')
        print(r.text)
        time.sleep(1)


# *** START OF MAIN *** #
app.run(debug=True)

# Start thread to mine
t = threading.Thread(target=mine)
t.start()

add_transaction_to_blockchain()


time.sleep(1)

# Get transaction by id
params = {'id_transaction': '1'}
response = requests.get('http://127.0.0.1:8000/get_transaction', params=params)
print(response.url)
print(response.text)
print(response.status_code)

# Get all transaction of a block (given id)
params = {'id_block': '1'}
response = requests.get('http://127.0.0.1:8000/get_all_transaction_in_block', params=params)
print(response.text)


# TO RUN BLOCKCHAIN ON PORT 8000
# python node_server.py

# TO RUN APP (from another terminal):
# python main.py

# CTRL+C to suspend view of Flask and to see messages from our main

"""TO RUN BLOCKCHAIN ON PORT 8000 (OLD METHOD)
export FLASK_APP=node_server.py
flask run --port 8000"""