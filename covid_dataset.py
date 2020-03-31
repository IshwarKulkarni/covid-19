"""
Ishwar Kulkarni, 03/31/2020
Creates/Loads the US Covid datasets by county, from NewYork times GitHub
"""
import csv
import logging
import sqlite3
import time
from datetime import datetime

import requests

TABLE_NAME = "data"

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def load_db():
    """Loads today's database and returns a connection, if not present, creates it"""
    today = datetime.now().strftime("%Y-%B-%d")

    con = sqlite3.connect(f'databases/{today}.db')
    cur = con.cursor()
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE_NAME}';")
    tables = cur.fetchall()
    if len(tables) > 0:
        return con

    fetch = time.time()

    url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
    req = requests.get(url)
    fetch = time.time() - fetch

    insert = time.time()
    cur.execute(f"CREATE TABLE {TABLE_NAME} (d_date date, county string, state string,\
                  cases int, deaths int);")

    lines = req.content.decode("utf-8").splitlines()

    split = time.time()
    csv_reader = csv.DictReader(lines)
    to_db = [(i['date'], i['county'], i['state'], i['cases'], i['deaths']) for i in csv_reader]
    split = time.time() - split

    ins = cur.executemany(f"INSERT INTO {TABLE_NAME} VALUES (?, ?, ?, ?, ?);", to_db)

    cur.execute(f'CREATE INDEX countyIndex ON {TABLE_NAME}(county);')
    cur.execute(f'CREATE INDEX stateIndex ON {TABLE_NAME}(state);')

    con.commit()

    insert = time.time() - insert
    logging.info("Inserted {%d} rows.\n\
                 Fetch time: {%1.3f}s, Split time: {%1.3f}s, Insert time: {%1.3f}",\
                 ins.rowcount, fetch, split, insert)
    return con
