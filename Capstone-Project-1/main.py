import requests
import pandas as pd
from selenium import webdriver
from uuid import uuid4
import time
import sys
from params import search
from database import insert_data, DB_NAME, start_connection
TABLE_FLIGHTS = "FLIGHTS"
TABLE_FLIGHTS_FARE ="FLIGHTSFARE"

# origin: BOM
# "destination": "IXC"
# flight_depart_date: 01/06/2024
import json
domain_url = "https://flight.yatra.com/air-search-ui/dom2/trigger?"

def get_airports_data():
    df_airports = pd.read_csv("./International-Airports.csv")
    return df_airports
    

def create_url():
    params_str = '&'.join([f'{key}={value}'for key,value in search.items()])
    url = domain_url + params_str
    return url



def get_data(url):
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)    
    print('driver started')
    driver.get(url)
    time.sleep(7)
    try:
        data = driver.execute_script("return mainData;")
        driver.close()
    except Exception as e:
        print(e)
        print("No data available")
        driver.close()
        data = {}
    print('driver closed')
    return data


def get_all_flights(data, payload):
    conn, cur = start_connection(DB_NAME)
    results_data = data.get("resultData")
    unique_ = []
    date_ = ''.join(payload.get('flight_depart_date', '').split("/")[::-1])
    schedule_id = f"{payload.get('origin')}{payload.get('destination')}{date_}"
    for res in results_data:
        all_scheduled_flights = res.get('fltSchedule', {}).get(schedule_id)
        if all_scheduled_flights:
            for each in all_scheduled_flights:
                try:
                    data = {
                        'name': each.get('airline'),
                        'unique_id': each.get('flno').get('fldisp'),
                        'id':str(uuid4()),
                        'origin': origin,
                        'destination': destination,
                        'travel_date': travel_date,
                        'updated_at':int(time.time())
                    }
                    unq_name = data.get("name","") + data.get("unique_id","")
                    if unq_name not in unique_:
                        insert_data(cur, data, TABLE_FLIGHTS)
                        unique_.append(unq_name)
                except:
                    # import ipdb; ipdb.set_trace()
                    pass
                
            conn.commit()
    conn.close()


def get_unique_flight(cur, data):
    cur.execute(f"""SELECT id, updated_at from FLIGHTS WHERE unique_id='{data.get("unique_id")}' AND name='{data.get("name")}' ORDER BY updated_at DESC""")
    for each in cur.fetchall():
        return each
    


def create_fare_details_data(data, payload):
    conn, cur = start_connection(DB_NAME)
    results_data = data.get("resultData", [{}])
    date_ = ''.join(payload.get('flight_depart_date', '').split("/")[::-1])
    schedule_id = f"{payload.get('origin')}{payload.get('destination')}{date_}"
    for res in results_data:
        all_scheduled_flights = res.get('fltSchedule', {}).get(schedule_id, "")
        if all_scheduled_flights:
            for each in all_scheduled_flights:
                try:
                    data = {
                        'name': each.get('airline'),
                        'unique_id': each.get('flno').get('fldisp'),
                        'travel_date': travel_date,
            
                    }
                    flight_id, updated_at = get_unique_flight(cur,data)
                    if flight_id:
                        fd_data = {
                            "id": str(uuid4()),
                            "flight_id":flight_id,
                            "fare_type": each.get("fareId"),
                            "price":each.get("fareD").get("O", {}).get("ADT").get("tf"),
                            "updated_at":updated_at
                        }
                        insert_data(cur, fd_data, TABLE_FLIGHTS_FARE)
                except:
                    pass
        conn.commit()
    conn.close()

def get_codes(origin, destination):
    codes = {}
    conn, cur = start_connection(DB_NAME)
    cur.execute(f"SELECT * FROM AIRPORTS WHERE name='{origin}' OR name='{destination}'")
    for each in cur.fetchall():
        if each[1] == origin:
            codes.update({"origin":each[2]})
        elif each[1] == destination:
            codes.update({"destination": each[2]})
    conn.close()
    return codes



                

if __name__ == '__main__':
    origin = sys.argv[1]
    destination = sys.argv[2]
    travel_date = sys.argv[3]
    codes = get_codes(origin, destination)
    origin_code = codes.get("origin")
    destination_code = codes.get("destination")
    if origin_code and destination_code:
        payload = {
            'origin':origin_code,
            'destination':destination_code,
            'flight_depart_date':travel_date
        }
        search.update(payload)
        url = create_url()
        data = get_data(url)
        if data:
            get_all_flights(data, payload)
            create_fare_details_data(data, payload)