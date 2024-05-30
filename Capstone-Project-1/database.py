import sqlite3

DB_NAME ="yatra.db"

def start_connection(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    return conn, cursor


def create_table(cursor, table_name, schema):
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    table = f"""CREATE TABLE {table_name} {schema}"""
    cursor.execute(table)
    print(f"created Table {table_name}")

def create_airports_table():
    table_nm = 'AIRPORTS'
    conn, cursor = start_connection(DB_NAME)
    schema = '''
            (id INTEGER PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            code VARCHAR(10) NOT NULL);
            '''
    create_table(cursor, table_nm, schema)
    conn.close()


def create_flights_table():
    table_nm = 'FLIGHTS'
    conn, cursor = start_connection(DB_NAME)
    schema = '''
            (id VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            unique_id VARCHAR(100) NOT NULL,
            origin VARCHAR(100) NOT NULL,
            destination VARCHAR(100) NOT NULL,
            travel_date VARCHAR(20) NOT NULL,
            updated_at INTEGER NOT NULL);
            '''
    create_table(cursor, table_nm, schema)
    conn.close()


def create_flight_fare_table():
    table_nm = 'FLIGHTSFARE'
    conn, cursor = start_connection(DB_NAME)
    schema = '''
            (id VARCHAR(255) NOT NULL,
            flight_id VARCHAR(255) NOT NULL,
            fare_type VARCHAR(100) NOT NULL,
            price INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            FOREIGN KEY (flight_id) REFERENCES FLIGHT(id));
            '''
    create_table(cursor, table_nm, schema)
    conn.close()



def insert_data(cursor, data, table_nm):
    keys = ','.join([each for each in data.keys()])
    values = str(tuple([each for each in data.values()]))
    stmnt = f"INSERT INTO {table_nm} ({keys}) VALUES {values}"
    cursor.execute(stmnt)
    



if __name__ == '__main__':
    create_airports_table()
    create_flights_table()
    create_flight_fare_table()
