from bs4 import BeautifulSoup
import requests
import sqlite3
import logging

from db import get_connection

URL_FORMAT = "https://www.boxofficemojo.com/year/{year}/"


def null_func(x):
    return x


def dollars(x):
    dol = x.strip("$")
    return to_int(dol)


def to_int(x):
    return int(x.replace(",", ""))


FORMAT_MAP = {0: to_int, 1: null_func, 5: dollars, 8: null_func}


class BoxOfficeYear:
    def __init__(self, year):
        self._content = None
        self.year = year

    @property
    def cached_filename(self):
        return "cached_html/%d.html" % self.year

    def _get_cached_year(self):
        try:
            with open(self.cached_filename, 'r') as fp:
                return fp.read()
        except FileNotFoundError:
            return False

    def _cache_contents(self):
        with open(self.cached_filename, 'wb') as fp:
            fp.write(self._content)

    @property
    def url(self):
        return URL_FORMAT.format(year=self.year)

    @property
    def content(self):
        self._content = self._get_cached_year()
        if self._content:
            return self._content
        res = requests.get(self.url)
        self._content = res.content
        self._cache_contents()
        return self._content

    def parse_res(self, num_films=None):
        films = []
        soup = BeautifulSoup(self.content, 'html.parser')
        table = soup.find('table')
        for n, tr in enumerate(table.find_all('tr')):
            this_film = []
            for tn, td in enumerate(tr.find_all('td')):
                if tn==1:
                    film_url = tr.find("a")['href']
                    film_url = film_url.split("?")[0]
                    film_url = "https://www.boxofficemojo.com" + film_url
                    this_film.append(film_url)
                if tn in FORMAT_MAP.keys():
                    text = td.string
                    if not text:
                        text = td.find("a").string
                        if not text:
                            raise Exception(td)
                    value = FORMAT_MAP[tn](text)
                    this_film.append(value)
            if this_film:
                films.append(this_film)
            if num_films and len(films) >= num_films:
                break
        return films

    def publish_to_db(self, film):
        film.append(self.year)
        film.append(self.url)
        sql = ''' INSERT INTO Film(
        Domestic_BO_Rank, 
        BOMojoFilmURL,
        Name, 
        Gross_Dollar, 
        Release_Date_Raw, 
        BO_Year, 
        BOMojoTableURL) 
        VALUES(?,?,?,?,?,?,?)'''
        conn = get_connection()
        cur = conn.cursor()
        logging.debug(film)
        try:
            cur.execute(sql, film)
        except sqlite3.IntegrityError:
            logging.warning("Film appeared before:%s" % film)
        conn.commit()
        conn.close()

    def populate_db(self):
        films = self.parse_res()
        for film in films:
            self.publish_to_db(film)

    
def main():
    # earliest 1977
    for year in range(1978, 2020):
        bo_year = BoxOfficeYear(year)
        bo_year.populate_db()
        logging.info(bo_year.url)

if __name__=="__main__":
    main()