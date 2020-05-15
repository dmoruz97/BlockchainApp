import datetime
import json
import const

import requests
from flask import render_template, redirect, request

from app import app

# Node in the blockchain network that our application will communicate with to fetch and add data.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

transactions = []
blocks = []


def get_k_blocks_from_blockchain(start,k):
    get_blocks_address = "{}/get_k_blocks".format(CONNECTED_NODE_ADDRESS)
    values = {'start': start, 'k': k}
    data = json.dumps(values)
    headers = {'Content-type': 'application/json',
               'Cache-Control': 'no-cache'}
    response = requests.post(get_blocks_address, headers=headers, data=data)

    if response.status_code == 200:
        return response.content


def get_chain_and_k_length():
    get_len_address = "{}/get_chain_length".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_len_address)
    data = json.loads(response.content)
    return data['chain_length'], data['k']


def dict_to_list(d):
    lst = []
    d = json.loads(d)
    for k, v in d.items():
        lst += [json.loads(v)]
    return lst


# Fetch the blockchain and store all the transactions in a global variable.
def fetch_blockchain():
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        chain = json.loads(response.content)

    global transactions
    global blocks

    for block in chain["chain"]:
        # "blocks" is a global variable
        blocks.append({"index": block["index"], "nonce": block["nonce"], "previous_hash": block["previous_hash"],
                       "hash": block["hash"], "timestamp": block["timestamp"], "#transactions": len(block["transactions"])})

        for t in block["transactions"]:
            t["index"] = block["index"]
            t["hash"] = block["hash"]
            transactions.append(t)

    transactions = sorted(transactions, key=lambda k: k["timestamp"], reverse=True)
    return chain["chain"], len(chain["chain"])


# Main endpoint
@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def index():
    chain, length = fetch_blockchain()
    global blocks

    return render_template('index.html',
                           title='Blockchain',
                           node_address=CONNECTED_NODE_ADDRESS,
                           genesis_block=chain[0],
                           number_of_blocks=length,
                           blocks=blocks
                           )


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
            success = 'Record successfuly added!'
            #response = requests.get('http://127.0.0.1:5000/add_record', params=params)
        else:
            success = 'Record NOT added!'
            #response = requests.get('http://127.0.0.1:5000/add_record', params=params)
        return render_template('add_record.html',
                               title='Add new record',
                               success=success)
        #return response.text


# Endpoint to get the status
# @params:
# - date
# - OP_CARRIER_FL_NUM

def query_status_aux(blocks_list, date, op_carrier_fl_num):
    for transaction in blocks_list:
        if transaction['FL_DATE'] == date and transaction['OP_CARRIER_FL_NUM'] == op_carrier_fl_num:
            return str(transaction)
    return const.no_matches


@app.route('/query_status', methods=['GET', 'POST'])
def query_status():
    if request.method == "POST":
        # date with the schema: yyyy-mm-dd
        print(request.form)
        date = request.form["date"]
        op_carrier_fl_num = request.form["op_carrier_fl_num"]
        op_carrier_fl_num=op_carrier_fl_num[0:len(op_carrier_fl_num)-1]
        # search status
        global transactions

        status = query_status_aux(transactions, date, op_carrier_fl_num)

        # if flight not found in the first k blocks...
        if status == const.no_matches:
            len_chain, k = get_chain_and_k_length();

            i = 1
            seen = k
            # ... search in the previous i*k blocks, with i which increments (1, 2, 3, ...)
            while len_chain - seen > 0 and status == const.no_matches:
                blocks_temp = get_k_blocks_from_blockchain(len_chain - seen, k * i)
                blocks_temp = dict_to_list(blocks_temp)
                seen += k*i
                i += 1

                j = 0
                while status == const.no_matches and j < len(blocks_temp):
                    block = blocks_temp[j]
                    j += 1
                    status = query_status_aux(block['transactions'], date, op_carrier_fl_num)
        else:
            print("Status found in cache")

        return render_template('query_status.html', title='Query status of a flight', result=status)

    if request.method == "GET":
        return render_template('query_status.html', title='Query status of a flight')


# Query the average delay of a flight carrier in a certain interval of time (point 4.3 of the assignment)
def query_delay_aux(blocks_list, carrier, start_time, end_time):
    count = 0
    total_delay = 0

    for transaction in blocks_list:
        if (transaction['OP_CARRIER_FL_NUM'] == carrier) and (start_time <= transaction['FL_DATE'] <= end_time):
            arr_delay = int(float(transaction["ARR_DELAY"]))
            if arr_delay > 0:  # There are also ARR_DELAY negative (flights arrived in advance)
                count = count + 1
                total_delay = total_delay + arr_delay  # Considered only the arrival delay

    return count, total_delay


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

        global transactions
        count, total_delay = query_delay_aux(transactions, carrier, start_time, end_time)

        # Then search in the rest of the blockchain...
        # (possible heuristic: we could stop when "start_time" is greater than a start_time in blockchain)
        len_chain, k = get_chain_and_k_length();

        i = 1
        seen = k
        # ... search in the previous i*k blocks, with i which increments (1, 2, 3, ...)
        while len_chain - seen > 0:
            blocks_temp = get_k_blocks_from_blockchain(len_chain - seen, k * i)
            blocks_temp = dict_to_list(blocks_temp)
            seen += k * i
            i += 1

            j = 0
            while j < len(blocks_temp):
                block = blocks_temp[j]
                j += 1
                count_2, total_delay_2 = query_delay_aux(block['transactions'], carrier, start_time, end_time)

            count = count + count_2
            total_delay = total_delay + total_delay_2

        if count != 0:
            average_delay = total_delay / count
            info = 'Average delay: {0:.2f} seconds'.format(average_delay)
        else:
            info = 'No matches!'
        #response = requests.get('http://127.0.0.1:5000/query_delay', params=params)
        return render_template('query_delay.html',
                               title='Query delay',
                               delay=info)
        #return response.text


# Endpoint to get the number of flight connecting A to B
# @params:
# - first date
# - second date
# - first city
# - second city

def count_flights_aux(blocks_list, first_date, second_date, first_city, second_city):
    count = 0

    for transaction in blocks_list:
        if first_date <= transaction['FL_DATE'] <= second_date and transaction['DEST_CITY_NAME'] == second_city and \
                transaction['ORIGIN_CITY_NAME'] == first_city:
            count += 1

    return count


@app.route('/count_flight', methods=['GET', 'POST'])
def count_flights():
    if request.method == "POST":
        # date with the schema: yyyy-mm-dd
        status = const.no_matches
        first_date = request.form["first_date"]
        second_date = request.form["second_date"]
        first_city = request.form["first_city"]
        second_city = request.form["second_city"]

        # search status
        """copy_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
        response = requests.get(copy_chain_address)
        blockchain = response.json()

        for block in blockchain['chain']:
            for transaction in block['transactions']:
        """

        global transactions
        count = count_flights_aux(transactions, first_date, second_date, first_city, second_city)

        # Then search in the rest of the blockchain...
        # (possible heuristic: we could stop when "start_time" is greater than a start_time in blockchain)
        len_chain, k = get_chain_and_k_length();

        i = 1
        seen = k
        # ... search in the previous i*k blocks, with i which increments (1, 2, 3, ...)
        while len_chain - seen > 0:
            blocks_temp = get_k_blocks_from_blockchain(len_chain - seen, k * i)
            blocks_temp = dict_to_list(blocks_temp)
            seen += k * i
            i += 1

            j = 0
            while j < len(blocks_temp):
                block = blocks_temp[j]
                j += 1
                count_2 = count_flights_aux(block['transactions'], first_date, second_date, first_city, second_city)

            count = count + count_2

        status = "Number of flights: {}".format(count)

        return render_template('count_fights.html', title='Flights connecting city A to city B', result=status)

    if request.method == "GET":
        return render_template('count_fights.html', title='Flights connecting city A to city B')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%d/%m/%Y %H:%M:%S')


chain, length = fetch_blockchain()
