from bs4 import BeautifulSoup as bs
from selenium import webdriver
from time import sleep
from database import insert_data, start_connection, DB_NAME
import re

CSV_HEADERS = ("name", "code")
HEADERS = {
    "User-Agent" : "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Connection": "keep-alive",
    "Retry-After": "5"
}

conn, cur = start_connection(DB_NAME)


def get_soup(url):
    driver = webdriver.Chrome()
    driver.get(url)
    sleep(5)
    ps = driver.page_source
    driver.close()
    if ps:
        soup = bs(ps, 'html.parser')
        return soup
    else:
        return {}



def insert_airports_data(airports):
    for airport in airports:
        airport = re.sub("NEW$", "", airport)
        airport = airport.strip()
        list_ = airport.split(" ")
        name = " ".join(list_[:-1])
        code = list_[-1].strip("()")
        dict_ = dict(zip(CSV_HEADERS,(name,code)))
        insert_data(cur,dict_, "AIRPORTS")
    conn.commit()


def populate_international_airports(soup):
    listing = soup.find_all("div", "airportlisting section")[2]
    airports = [each.text.strip() for each in listing.find_all("li")]
    insert_airports_data(airports)
    print("Data Inserted")

def populate_data():
    url = "https://www.goindigo.in/airport-directory/india.html"
    soup = get_soup(url)
    if soup:
        populate_international_airports(soup)

        
if __name__ == '__main__':
    populate_data()
    
    





