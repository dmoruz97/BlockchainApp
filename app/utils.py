import pandas as pd


# ORIGIN_CITY_NAME
# DEST_CITY_NAME


class City:
    def __init__(self, id, name, flights):
        self.id = id  # the id coincides with the array index
        self.name = name  # Name of the city
        self.flights = flights  # List of flight's indexes

    def add_flight(self, f):
        self.flights += f


class Flight:
    def __init__(self, id, origin_city, destination_city, dep_time, arr_time):
        self.id = id  # the id coincides with the array index (is the position in 'flights' list)
        self.origin_city = origin_city
        self.destination_city = destination_city
        self.dep_time = dep_time
        self.arr_time = arr_time


def get_number_of_flights(first_date, second_date, first_city, second_city, blockchain):
    cities = []
    flights = []
    count_cities = 0  # index of the origin city
    count_flights = 0  # index of the destination city
    id_first_city = None
    id_second_city = None

    for block in blockchain['chain']:
        for transaction in block['transactions']:
            if first_date <= transaction['FL_DATE'] <= second_date and transaction['CANCELLED'] == 0:

                dep_timestamp = pd.Timestamp(year=int(transaction['FL_DATE'][0:4]),
                                             month=int(transaction['FL_DATE'][4:6]),
                                             day=int(transaction['FL_DATE'][6:8]),
                                             hour=int(transaction['DET_TIME'][0:2]),
                                             minute=int(transaction['DET_TIME'][2:4]))

                arr_timestamp = pd.Timestamp(year=int(transaction['FL_DATE'][0:4]),
                                             month=int(transaction['FL_DATE'][4:6]),
                                             day=int(transaction['FL_DATE'][6:8]),
                                             hour=int(transaction['ARR_TIME'][0:2]),
                                             minute=int(transaction['ARR_TIME'][2:4]))

                dep_timestamp += pd.Timedelta(minutes=float(transaction['DEP_DELAY']))
                arr_timestamp += pd.Timedelta(minutes=float(transaction['ARR_DELAY']))

                flights += [
                    Flight(count_flights, transaction['ORIGIN_CITY_NAME'], transaction['DEST_CITY_NAME'], dep_timestamp,
                           arr_timestamp)]

                find_origin = False
                find_destination = False

                for x in cities:
                    if x.name == transaction['ORIGIN_CITY_NAME']:
                        x.add_flight(count_flights)
                        find_origin = True
                    if x.name == transaction['DEST_CITY_NAME']:
                        find_destination = True

                if not find_origin:
                    cities += [City(count_cities, transaction['ORIGIN_CITY_NAME'], [count_flights])]
                    if transaction['ORIGIN_CITY_NAME'] == first_city:
                        id_first_city = count_cities
                    if transaction['ORIGIN_CITY_NAME'] == second_city:
                        id_second_city = count_cities
                    count_cities += 1

                if not find_destination:
                    cities += [City(count_cities, transaction['DEST_CITY_NAME'], [])]
                    if transaction['DEST_CITY_NAME'] == first_city:
                        id_first_city = count_cities
                    if transaction['DEST_CITY_NAME'] == second_city:
                        id_second_city = count_cities
                    count_cities += 1

                count_flights += 1

    if id_first_city is None or id_second_city is None:
        return 0

    # a questo punto la lista cities contiene tutte le città, ognuna di esse ha una lista 'flights' contenente gli indici (della lista flights di questo metodo) dei voli che partono da lì
    # la lista flights contiene tutti i voli con timestamp di partenza e timestamp di arrivo (così sarà più facile confrontarli durante la ricerca)
