##About

This project is based on crawling travel website, store the data in a sql database, Further use that data for tracking and extracting valuable insights about the travel rates in India.

##Steps followed in this project:

1. Created a setup which can able to crawl the data via Selenium and parsed the data using native json library

2. Data is stored in Sqlite3(python library) in two tables, one consists the Flight details and other contains the Flightfare details

3. Due to limited time given for Scraping the data, only one origin location and five destination locations are chosen for this project


*DataFlow*:

FLIGHTS:
            _id_ <unique-id>,
            _name_ <airplane-name>,
            _unique-id_ <airplane>,
            _origin_ <travel-origin>,
            _destination_ <travel-destination>,
            _travel_date_<travel-date>,
            _updated-at_<crawl-timestamp>

FLIGHTSFARE:
            _id_ <unique-id>,
            flight_id <foreign-key(FLIGHTS)>,
            fare_type <fare-type>,
            price <fare>,
            updated_at <crawl-timestamp>


##CONTROL_FLOW:

1. All databases are created by running the database.py file

2. List of airports are crawled from https://www.goindigo.in/airport-directory/india.html via selenium; store into the DB using airports_in.py file

3. Crawling for this project starts from crawl.py file which inturns runs the main.py which will initaite the crawling for a given origin, destination and travel date parameters

4. crawl.py will continously crawls and gets new data for every two hours

5. Inorder to query the DB and get some insights app.py is initated, which will prompt for required details and finally present you the top-five airplane with lowest fare on that particular route and historic data about a plane in the route




