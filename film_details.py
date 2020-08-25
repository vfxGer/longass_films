import re
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import requests_cache
import sys
import csv

requests_cache.install_cache('bojodetails_cache')

from db import get_connection

from pprint import pprint

SELECT_SQL = """
SELECT Name, BO_Year, BOMojoFilmURL FROM Film WHERE BO_Year!=1978 and Domestic_BO_Rank<21;
"""

UPDATE_SQL = """
UPDATE Film
SET DurationMinutes=?,
    RawDuration=?,
    ReleaseDate=?
WHERE Name=? AND BO_Year=?;
"""


def get_datetime(value):
    # 'Dec 15, 1978'
    return datetime.strptime(value, "%b %d, %Y")


def parse_to_minutes(value):
    # 2 hr 23 min
    # reg_ex = re.compile(r"\s*([0-9]+)\s*hr\s*([0-9]+)\s*min.*")
    hour_reg = re.match(r"\s*([0-9]+)\s*hr.*", value)
    if hour_reg:
        hours = int(hour_reg.groups()[0])
    else:
        hours = 0

    min_reg = re.match(r".*\s([0-9]+)\s*min.*", value)
    if min_reg:
        minutes = int(min_reg.groups()[0])
    else:
        minutes = 0
    return int(hours) * 60 + int(minutes)


def get_movies():
    conn = get_connection()
    curs = conn.cursor()
    curs.execute(SELECT_SQL)
    return curs.fetchall()

def parse_film_details(bojo_url):
    resp = requests.get(bojo_url)
    soup = BeautifulSoup(resp.content, 'html.parser')
    result = {}
    raw_span = list(soup.find_all('span'))
    for n, value in enumerate(raw_span):
        if value.string == 'Running Time':
            result['RawDuration'] = raw_span[n+1].string
            result['DurationMinutes'] = parse_to_minutes(result['RawDuration'])
        elif value.string and value.string.startswith("Release Date"):
            if raw_span[n+1].string is not None:
                result['Release_Date_Raw'] = raw_span[n+1].string
                result['ReleaseDate'] = get_datetime(result['Release_Date_Raw'])
            else:
                result['Release_Date_Raw'] = raw_span[n+1].find("a").string
                result['ReleaseDate'] = get_datetime(result['Release_Date_Raw'])
    assert 'RawDuration' in result
    assert "Release_Date_Raw" in result
    return result


def update_db(film_name, year, details):
    conn = get_connection()
    curs = conn.cursor()
    print(curs.execute(UPDATE_SQL,
                 (details['DurationMinutes'],
                  details['RawDuration'],
                  details['ReleaseDate'],
                  film_name,
                  year)
                 ))
    assert curs.rowcount==1
    conn.commit()
    conn.close()


def create_csvfile(filename="film_duration.csv"):
    csv_sql = """
SELECT Name, BO_Year, BOMojoFilmURL, RawDuration
FROM Film WHERE BO_Year!=1978 and Domestic_BO_Rank<21;
"""
    conn = get_connection()
    curs = conn.cursor()
    curs.execute(csv_sql)
    all_info = [('Name', 'BO_Year', 'BOMojoFilmURL', 'Duration')]
    all_info.extend(curs.fetchall())
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        for line in all_info:
            csvwriter.writerow(line)


def main():
    if "--csv" in sys.argv[1:]:
        create_csvfile()
    else:
        films = get_movies()
        for film in films:
            print(film[0])
            print(film[2])
            details = parse_film_details(film[2])
            pprint(details)
            assert details
            update_db(film[0], film[1], details)


if __name__=="__main__":
    main()
