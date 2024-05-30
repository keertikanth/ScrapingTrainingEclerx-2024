import sqlite3

DB_NAME ="ajio.db"

def start_connection(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    return conn, cursor


def create_table(cursor, table_name, schema):
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    table = f"""CREATE TABLE {table_name} {schema}"""
    cursor.execute(table)
    print(f"created Table {table_name}")



def create_products_table():
    table_nm = 'PRODUCTS'
    conn, cursor = start_connection(DB_NAME)
    schema = '''
        (id VARCHAR(255) NOT NULL,
        ajio_id VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        website_url VARCHAR(255) NOT NULL,
        brand VARCHAR(100) NOT NULL,
        category VARCHAR(50) NOT NULL,
        segment VARCHAR(50) NOT NULL,
        product_image VARCHAR(300) NOT NULL,
        price INTEGER,
        actual_price INTEGER,
        offer_price INTEGER,
        option_code VARCHAR(100),
        option_url VARCHAR(255))
    '''
    create_table(cursor, table_nm, schema)
    conn.close()
    print(f"{table_nm} created...")



def create_product_table():
    table_nm = 'PRODUCT'
    conn, cursor = start_connection(DB_NAME)
    schema = '''(id VARCHAR(255) NOT NULL,
        ajio_id VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        status VARCHAR(50),
        instock_quantity INTEGER,
        avg_rating DECIMAL(4, 2),
        ratings_count INTEGER,
        FOREIGN KEY (id) REFERENCES FLIGHT(id),
        FOREIGN KEY (ajio_id) REFERENCES FLIGHT(ajio_id))'''
    create_table(cursor, table_nm, schema)
    conn.close()
    print(f"{table_nm} created...")




def insert_data(cursor, data, table_nm):
    keys = ','.join([each for each in data.keys()])
    values = str(tuple([each for each in data.values()]))
    stmnt = f"INSERT INTO {table_nm} ({keys}) VALUES {values}"
    cursor.execute(stmnt)
    



if __name__ == '__main__':
    create_products_table()
    create_product_table()
