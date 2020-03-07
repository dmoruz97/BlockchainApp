import csv


# Function that reads the CSV file and return a list of the rows inside it
def read_csv():
    csv_file = "656211699_T_ONTIME_REPORTING.csv"
    rows = []

    with open(csv_file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        count_row = 0
        for row in csv_reader:
            if (count_row != 0):
                rows.append(row)
            count_row = count_row + 1

    print("Total rows in CSV: {}".format(len(rows)))
    return rows


if __name__ == "__main__":
    transactions = read_csv()

    for t in transactions:
        print()
        # invia transazione a interfaccia
