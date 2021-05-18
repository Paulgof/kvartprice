import csv
import re
from itertools import product

import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError

MAX_PAGE = 55
BASE_URL = 'https://krasnodar.cian.ru/cat.php?deal_type=sale&engine_version=2&object_type%5B0%5D=1&offer_type=flat&' \
           'p={page}&region=4820&room{room_type}=1'
ROOM_TYPES = {
    1: (1, '1-комнатная'),
    2: (2, '2-комнатная'),
    3: (3, '3-комнатная'),
    4: (4, '4-комнатная'),
    5: (5, '5-комнатная'),
    6: (6, '6-комнатная'),
    9: (0, 'студия')
}

session = requests.Session()
session.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/90.0.4430.93 Safari/537.36 OPR/76.0.4017.123',
    'Accept-Language': 'ru'
}


class NoMorePagesException(Exception):
    message = 'No more pages for scraping'


def scrape_offer(url):
    response = session.get(url)
    response.raise_for_status()
    offer_soup = BeautifulSoup(response.text, 'lxml')
    return offer_soup


def parse_offer(offer_soup):

    return


def scrape_page(url):
    response = session.get(url)
    response.raise_for_status()
    if response.status_code // 100 == 3:
        raise NoMorePagesException()

    page_soup = BeautifulSoup(response.text, 'lxml')
    offers = page_soup.select('div[data-name="LinkArea"] a[href*="/flat/"]')
    offers_links = [offer['href'] for offer in offers]
    return offers_links


def init_parsing():
    offers_data = {}
    for room_type, page_number in product(ROOM_TYPES.keys(), range(1, MAX_PAGE + 1)):
        try:
            page_offers_links = scrape_page(BASE_URL.format(page=page_number))
            print('Got offers on page {}, room_type {}'.format(page_number, room_type))
        except NoMorePagesException:
            print('[NMP]: Skip page {} for room_type {}'.format(page_number, room_type))
            continue
        except HTTPError as http_error:
            print("[HTTP]: Couldn't scrape page.", http_error)
            continue
        except Exception as e:
            print('[DNG]: Unresolved exception. Continue scraping pages.', e)
            continue

        for offer_link in page_offers_links:
            offer_id = int(re.search(r'flat/(\d+)/', offer_link)[1])
            print('Parsing on url', offer_link)
            try:
                offers_data[offer_id] = scrape_offer(offer_link)
            except HTTPError as http_error:
                print("[HTTP]: Couldn't scrape page.", http_error)
                continue
            except Exception as e:
                print('[DNG]: Unresolved exception. Continue scraping pages.', e)
                continue


if __name__ == '__main__':
    init_parsing()
