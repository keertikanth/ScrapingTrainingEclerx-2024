
## About 

This project is based on crawling travel website, store the data in a sql database, Further use that data for tracking and extracting valuable insights about the travel rates in India.

## Steps followed in this project:

Created a setup which can able to crawl the data via Selenium and parsed the data using native json library

Data is stored in Sqlite3(python library) in two tables, one consists the Flight details and other contains the Flightfare details

Due to limited time given for Scraping the data, only one origin location and five destination locations are chosen for this project

## DataFlow:

### FLIGHTS: 
    id              (unique id)
    name            (flight name)
    unique-id       (flight id)
    origin          (flight-origin)
    destination     (flight-destination)
    travel_date     (flight-travel-date)
    updated-at      (crawled-timestamp)

### FLIGHTSFARE: 
    id              (unique id)
    flight_id       (foreign-key(FLIGHTS))
    fare_type       (fare-type)
    price           (flight-fare)
    updated_at      (crawled-timestamp)

## Control flow:

All databases are created by running the database.py file

List of airports are crawled from https://www.goindigo.in/airport-directory/india.html via selenium; store into the DB using airports_in.py file

Crawling for this project starts from crawl.py file which inturns runs the main.py which will initaite the crawling for a given origin, destination and travel date parameters

crawl.py will continously crawls and gets new data for every two hours

Inorder to query the DB and get some insights app.py is initated, which will prompt for required details and finally present you the top-five airplane with lowest fare on that particular route and historic data about a plane in the route