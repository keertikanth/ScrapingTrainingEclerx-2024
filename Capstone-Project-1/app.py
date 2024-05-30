from database import start_connection, DB_NAME
import pandas as pd
from datetime import datetime
from pprint import pprint


airlineNames = {
            "AI": "Air India",
            "SG": "Spicejet",
            "9W": "Jet Airways",
            "6E": "Indigo",
            "G8": "Go Air",
            "88": "Go Air Business",
            "69": "Vistara Premium Economy",
            "S2": "JetKonnect",
            "77": "JetKonnect",
            "100": "Multiple Airlines",
            "LB": "Air Costa",
            "IX": "AirIndia Express",
            "I5": "Air Asia",
            "UK": "Vistara",
            "OP": "AirPegasus",
            "2T": "TruJet",
            "61": "Jet Airways Business",
            "62": "Air India Business"
        }
ORIGIN_OPTIONS = {
    "1" : "Mumbai"
}

DEST_OPTIONS = {
    "1": "Bengaluru",
    "2" : "Chennai",
    "3": "Hyderabad", 
    "4" : "Kolkata",
    "5" : "Delhi"
}



def start_app():
    origin_opt, dest_opt, date_opt, fare_type = prompt_for_input()
    data = get_top_five_flights(origin_opt, dest_opt, date_opt, fare_type)
    all_ = parse_top_five(data)
    df = pd.DataFrame(all_, index = range(1,len(all_)+1))
    print(df)
    airline_opt = get_airline_opt(df)
    show_historic_data(origin_opt, dest_opt, date_opt, fare_type, airline_opt)
    print("New shell is created".center(50, "#") )
    start_app()

def get_airline_opt(df):
    list_ = df["airline_id"].values
    options = dict([(str(key), value) for key, value in enumerate(list_, start=1)])
    print_prompt_options(options)
    str_ = "These are available flights, Please enter a valid flight option from the above options to get the historic data:"
    airline = input(str_)    
    airline_opt = options.get(airline)
    if not airline_opt:
        airline_opt = persist_for_input(options=options, prompt_str=str_)
        return airline_opt
    else:
        return airline_opt


def get_options(key, cond, table_name):
    conn, cur = start_connection(DB_NAME)
    cur.execute(f"SELECT DISTINCT {key} FROM {table_name} "+ cond)
    options = {}
    [options.update({str(key):value[0]}) for key, value in enumerate(cur.fetchall(),start=1) if value[0]]
    conn.close()
    return options

def get_travel_date_options(origin, dest):
    condition = f"WHERE origin='{origin}' AND destination='{dest}'"
    key = 'travel_date'
    table_name = 'FLIGHTS'
    options = get_options(key, condition, table_name)
    return options


def get_fare_type_options(origin, dest, travel_date):
    condition = f"JOIN FLIGHTSFARE ON FLIGHTSFARE.flight_id=FLIGHTS.id WHERE origin='{origin}' AND destination='{dest}' AND travel_date='{travel_date}'"
    key = 'fare_type'
    table_name = 'FLIGHTS'
    options = get_options(key, condition, table_name)
    return options
    


def parse_top_five(data):
    all_ = []
    for each in data:
        parsed_data = {
        "airline_name" : airlineNames.get(each[1]),
        "airline_id" : each[2],
        "fare_type" : each[3],
        "price" : each[4],
        "avg_price" : int(each[5]),
        "max_price" : each[6],
        "min_price" : each[7]
        }
        all_.append(parsed_data)
    return all_
        
        
def get_top_five_flights(origin, dest, date, fare_type):
    conn, cur = start_connection(DB_NAME)
    cur.execute(f"SELECT id, name, id_, fare_type,price, AVG(price), max(price), min(price) FROM (SELECT *,FLIGHTS.unique_id as id_ FROM FLIGHTS JOIN FLIGHTSFARE ON FLIGHTSFARE.flight_id=FLIGHTS.id WHERE origin='{origin}' AND destination='{dest}' AND travel_date='{date}' AND fare_type='{fare_type}' ORDER BY FLIGHTS.updated_at DESC) GROUP BY id_ ORDER BY price LIMIT 5")
    return cur.fetchall()

def print_prompt_options(options):
    str_ = ""
    for key,value in options.items():
        str_ += f'{value.upper()} -----> {key}'
        str_ += "\n"
    print(str_)

def persist_for_input(prompt="", options={}, prompt_str = ""):
    while True:
        print(" Enter a valid option or press ctrl+c to exit... ")
        if not options:
            val = eval(f'{prompt}'.upper()+"_OPTIONS")
        else:
            val = options
        print_prompt_options(val)
        if not prompt_str:
            input_ = input(f"Please enter a valid {prompt} option from the above options:")
        else:
            input_ = input(prompt_str)
        input_opt = val.get(input_)
        if input_opt:
            return input_opt

            
def prompt_for_input():
    print_prompt_options(ORIGIN_OPTIONS)
    origin = input("Please enter a valid origin option from the above options:")
    origin_opt = ORIGIN_OPTIONS.get(origin)
    if not origin_opt:
        persist_for_input(prompt="origin")
    

    print_prompt_options(DEST_OPTIONS)
    dest = input("Please enter a valid destination option from the above options:")
    dest_opt = DEST_OPTIONS.get(dest)
    if not dest_opt:
        persist_for_input(prompt="destination")
    travel_options = get_travel_date_options(origin_opt, dest_opt)

    print_prompt_options(travel_options)
    prompt_str = "These are available dates, Please enter a valid travel date option from the above options:"
    travel = input(prompt_str)
    travel_opt = travel_options.get(travel)
    if not travel_opt:
        persist_for_input(prompt_str=prompt_str, options=travel_options)


    faretype_options = get_fare_type_options(origin_opt, dest_opt, travel_opt)
    print_prompt_options(faretype_options)
    prompt_str = "These are available faretype options, Please enter a valid faretype option from the above options:"
    faretype = input(prompt_str)
    faretype_opt = faretype_options.get(faretype)
    if not faretype_opt:
        persist_for_input(prompt_str=prompt_str, options=faretype_options)

    return origin_opt, dest_opt, travel_opt, faretype_opt

def parse_historic_data(list_):
    all_ = []
    for data in list_:
        parsed_data = {
            "airline_name":airlineNames.get(data[0]),
            "airline_id": data[1],
            "updated_at": datetime.fromtimestamp(data[2]),
            "price": data[3],
            "fare_type": data[4]
        }
        parsed_data["updated_at"] = parsed_data.get("updated_at").strftime("%d-%m-%Y-%H:%M")
        all_.append(parsed_data)
    df = pd.DataFrame(all_, index=range(1, len(all_)+1))
    print(df)


def show_historic_data( origin, dest, date, fare_type, flight_unique_id):
    print(flight_unique_id)
    conn, cur = start_connection(DB_NAME)
    q_str = f"SELECT name, unique_id, FLIGHTS.updated_at, price, fare_type FROM FLIGHTS JOIN FLIGHTSFARE ON FLIGHTS.id=FLIGHTSFARE.flight_id WHERE origin='{origin}' AND destination='{dest}' AND travel_date='{date}' AND fare_type='{fare_type}' AND unique_id='{flight_unique_id}' ORDER BY FLIGHTS.updated_at"
    cur.execute(q_str)
    list_ = cur.fetchall()
    parse_historic_data(list_)
    conn.close()


if __name__ == '__main__':
    try:
        start_app()
    except:
        print("You are logged off...")