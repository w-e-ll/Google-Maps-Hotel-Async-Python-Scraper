# Hotel data scraper from Google Maps service

Google Maps Hotel Async Python Scraper

Spider that scrapes from Google Maps hotels data: name, phone, address, website, direction,
description, rating, reviews_count, reviews_rating, reviews_link, review,
location_highlights, location_things_to_do, location_getting_around, nearby_hotels,
earby_things_to_do, nearby_airports, nearby_transit_stops, mapped_urls, photos, ets.
Makes a list of queries (need a list of towns, places in country you want to scrape) to be able
to make a Google search request. Collects data and stores it to Postgres.

## To install requirements and start the application:

- virtualenv -p python3.6 google_maps_scraper
- cd google_maps_scraper
- activate it (source bin/activate)
- git clone https://github.com/w-e-ll/Google-Maps-Hotel-Async-Python-Scraper.git
- cd google-maps-async-python-scraper
- pip install -r requirements.txt

## Configure PostgreSQL:

- sudo apt-get install postgresql libpq-dev postgresql-client postgresql-client-common
- sudo su postgres
- psql
- create database 'your DB name here';
- \c 'your DB name here'
- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
- cd create_db
- python3 create_tables.py

- Choose country you wont to scrape
- cd scraper
- open get_list_of_queries_from_hotelscombined.py
- open website https://www.hotelscombined.com/Place/{}.htm - {enter your country}
- get queries by country, per region, save them to a file (name it too)
- copy saved queries from your file to scraper/query_list.py
- queries need to be saved like that:
- "first",
- "second",
- "etc",
- open scraper/db/main.py
- input your database credentials
- open scraper/run.py
- on line 175 enter country name which you want to scrape, to make query, to be able to make requests in Google
- on line 223 enter language on what you want to scrape data (hl=en)
- python3 run.py

## Get hotel data from database, to see what you've scraped:
- cd joins
- run: python3 select.py --name "Leipzig Marriott Hotel"  (enter "{}" - {name of a hotel})


made by: https://w-e-ll.com
