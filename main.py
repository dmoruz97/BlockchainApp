import csv
import json
from urllib.parse import urlencode
import requests

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
                t = {}
                t["TRANSACTION_ID"] = count_row
                for i, value in enumerate(row[:-1], 0):
                    t[header[i]] = value
                rows.append(t)
            count_row = count_row + 1

    print("Total rows in CSV: {}".format(len(rows)))
    return rows


# FROM TERMINAL:
# export FLASK_APP=bc_interface.py
# flask run

if __name__ == "__main__":
    transactions = read_csv()   # Each transaction is in JSON form (key => value)

    # Add transaction to blockchain
    headers = {'Content-type': 'application/json'}
    for t in transactions:
        data = json.dumps(t)
        response = requests.post('http://127.0.0.1:5000/new_transaction', headers=headers, data=data)
        break

    # Get transaction by id
    params = {'id_transaction': '1'}
    response = requests.get('http://127.0.0.1:5000/get_transaction', params=params)
    print(response.url)
    print(response.text)
    print(response.status_code)
