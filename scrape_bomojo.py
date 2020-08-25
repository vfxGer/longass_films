import os

from bs4 import BeautifulSoup
import requests

URL_FORMAT = "https://www.boxofficemojo.com/year/{year}/"


def get_cached_filename(year):
    return "cached_html/%d.html" % year


def get_cached_year(year):
    try:
        with open(get_cached_filename(year), 'r') as fp:
            return fp.read()
    except FileNotFoundError:
        return False


def cache_contents(year, content):
    with open(get_cached_filename(year), 'wb') as fp:
        fp.write(content)


def get_raw_year(year):
    content = get_cached_year(year)
    if content:
        return content
    url = URL_FORMAT.format(year=year)
    print(url)
    res = requests.get(url)  
    cache_contents(year, res.content)
    return res.content


def parse_res(content, num_films=10):
    films = []
    soup = BeautifulSoup(content, 'html.parser')
    table = soup.find('table')
    keep = {0, 1, 5, 6, 8}
    for n, tr in enumerate(table.find_all('tr')):
        this_film = []
        for tn, td in enumerate(tr.find_all('td')):
            print(td.string)
            if tn in keep:
                this_film.append(td.string)
        if this_film:
            films.append(this_film)
        print(n)
        print("+"*30)
        if len(films)>=num_films:
            break
    films.reverse()
    from pprint import pprint
    pprint(films)
    return films

    
def main():
    res = get_raw_year(2018)
    parse_res(res)

if __name__=="__main__":
    main()