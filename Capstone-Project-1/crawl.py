from database import start_connection, DB_NAME
import os
from datetime import datetime, timedelta
from time import sleep

RESTRICT_TO = ["Bengaluru", "Chennai", "Hyderabad", 'Kolkata', 'Delhi']
ORIGIN = "Mumbai"

def create_next_three_dates(dt):
    all_ = []
    for i in range(1, 4):
        dt_ = datetime.strptime(dt, "%d/%m/%Y") + timedelta(days=i)
        dt_str = datetime.strftime(dt_, "%d/%m/%Y")
        all_.append(dt_str)
    return all_


def start_crawl(dt):
    conn, cur = start_connection(DB_NAME)
    cur.execute("SELECT name from AIRPORTS")
    all_airport_codes = cur.fetchall()
    for name_origin in all_airport_codes:
        origin = name_origin[0]
        if origin != ORIGIN:
            continue
        for name_dest in all_airport_codes:
            dest = name_dest[0]
            if origin == dest:
                continue
            elif dest not in RESTRICT_TO:
                continue
                
            else:
                try:
                    print(f"Crawling started for origin:{origin} & destination:{dest}")
                    os.system(f"python main.py {origin} {dest} {dt}")
                    print(f"Crawling done for origin:{origin} & destination:{dest}")

                except:
                    import ipdb; ipdb.set_trace()
    conn.close()


def run():
    dt = datetime.strftime(datetime.now().date(), "%d/%m/%Y")
    list_ = create_next_three_dates(dt)
    print(list_)
    for dt_ in list_:
        print(f"Crawling for {dt_}")
        start_crawl(dt_)  



if __name__ == '__main__':
    run()