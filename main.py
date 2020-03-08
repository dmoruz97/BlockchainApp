import csv


# Function that reads the CSV file and return a list of the rows inside it
def read_csv():
    csv_file = "656211699_T_ONTIME_REPORTING.csv"
    rows = []

    with open(csv_file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        count_row = 0
        for row in csv_reader:
            if (count_row == 0):
                header = row
            else:
                t = {}
                for i, value in enumerate(row):
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

    for t in transactions:
        print(t)
        break
        # invia transazione a interfaccia
