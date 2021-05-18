import csv
import datetime
import re
from functools import partial
from itertools import product

import requests
from bs4 import BeautifulSoup, element
from requests.exceptions import HTTPError

CITY = {
    'name': 'krasnodar',
    'cian_region': 4820
}
MAX_PAGE = 55
BASE_URL = 'https://{city_name}.cian.ru/cat.php?region={cian_region}&{tale}'.format(
    city_name=CITY['name'],
    cian_region=CITY['cian_region'],
    tale='deal_type=sale&engine_version=2&object_type%5B0%5D=1&offer_type=flat&p={page}&room{room_type}=1'
)
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
    price: str = offer_soup.select_one('span[itemprop="price"]')['content']
    price_value = int(price.replace(' ', '')[:-1])  # ex.: '2 700 000 ₽' -> 2700000
    views = offer_soup.select_one('div[data-name="OfferStats"] a')
    views_total_value = int(views.get_text().split()[0])

    flat_square: str = offer_soup.select_one('div[data-name="OfferTitle"] h1').text  # todo other squares
    # ex.: '1-комн. квартира, 44,22 м²' -> 44.22
    flat_square_value = float(re.search(r'(\d+,?\d*) м', flat_square)[1].replace(',', '.'))
    floor_info: str = offer_soup.find_all(string=re.compile(r'\d+ из \d+'))[0]
    flat_floor, total_floors = map(int, floor_info.split(' из '))

    geo_info: str = offer_soup.select_one('div[data-name="Geo"] span[itemprop="name"]')['content']
    geo_info_split = geo_info.split(', ')
    area_value = geo_info_split[2]
    flat_number = geo_info_split[-1]
    street = geo_info_split[-2]
    district_main = geo_info_split[3] if len(geo_info_split) > 5 else ''
    district_local = geo_info_split[4] if len(geo_info_split) > 6 else ''

    flat_main_info = offer_soup.select('li[data-name="AdditionalFeatureItem"]')
    dict_main_info = {}
    for info in map(partial(element.Tag.get_text, separator='::'), flat_main_info):  # todo func-way
        info_key, info_value = info.split('::')  # todo check all possible elements
        dict_main_info[info_key] = info_value

    flat_cian_info = offer_soup.select('div[data-name="BtiHouseData"] div[data-name="Item"]')
    dict_cian_info = {}
    for info in map(partial(element.Tag.get_text, separator='::'), flat_cian_info):
        info_key, info_value = info.split('::')  # todo check all possible elements
        dict_cian_info[info_key] = info_value

    description = offer_soup.select_one('div[data-name="Description"] p[itemprop="description"]')
    description_value = description.get_text()

    return {
        'price': price_value,
        'views': views_total_value,
        'total_square': flat_square_value,
        'floor': flat_floor, 'total_floors': total_floors,
        'area': area_value,
        'flat_number': flat_number,
        'street': street,
        'district_main': district_main,
        'district_local': district_local,
        'description': description_value,
        'flat_type': dict_main_info.get('Тип жилья', ''),
        'toilet': dict_main_info.get('Санузел', ''),
        'balcony': dict_main_info.get('Балкон/лоджия', ''),
        'repair_status': dict_main_info.get('Ремонт', ''),
        'window_view': dict_main_info.get('Вид из окон', ''),
        'house_type': dict_cian_info.get('Тип дома', '')
    }


def scrape_page(url):
    response = session.get(url)
    response.raise_for_status()
    if response.status_code // 100 == 3:
        raise NoMorePagesException()

    page_soup = BeautifulSoup(response.text, 'lxml')
    offers = page_soup.select('div[data-name="LinkArea"] a[href*="/flat/"]')
    offers_links = [offer['href'] for offer in offers]
    return offers_links


def init_parsing(file_name):
    timer_start = datetime.datetime.now()
    offers_counter = 0
    for room_type, page_number in product(ROOM_TYPES.keys(), range(1, MAX_PAGE + 1)):
        page_timer_start = datetime.datetime.now()
        offers_data = {}
        try:
            page_offers_links = scrape_page(BASE_URL.format(page=page_number, room_type=room_type))
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
                offers_data[offer_id] = {
                    'link': offer_link,
                    'room_type': room_type,
                    'soup': scrape_offer(offer_link)
                }
                offers_counter += 1
            except HTTPError as http_error:
                print("[HTTP]: Couldn't scrape page.", http_error)
                continue
            except Exception as e:
                print('[DNG]: Unresolved exception. Continue scraping pages.', e)
                continue

        page_timer_end = datetime.datetime.now()
        print('[I] Scraping done for page {}, room_type {} in {} seconds. Start parsing...'.format(
            page_number,
            room_type,
            (page_timer_end - page_timer_start).seconds
        ))

        for offer_id, offer_data in offers_data.items():
            try:
                flat_info = parse_offer(offer_data['soup'])
            except Exception as e:
                print('[DNG] Exception during parsing. ', e)
                continue

            with open(file_name, 'a', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=' ', quotechar='|')
                csv_writer.writerow([
                    offer_id, offer_data['link'], flat_info['price'], ROOM_TYPES[offer_data['room_type']][0],
                    flat_info['views'], flat_info['total_square'], flat_info['floor'], flat_info['total_floors'],
                    flat_info['area'], flat_info['flat_number'], flat_info['street'], flat_info['district_main'],
                    flat_info['district_local'], "<flat_info['description']>", flat_info['flat_type'],
                    flat_info['toilet'], flat_info['balcony'], flat_info['repair_status'], flat_info['window_view'],
                    flat_info['house_type']
                ])

        print('[I] Batch has been parsed and saved.')

    timer_end = datetime.datetime.now()
    print('Scraping past in {} seconds. Fetched {} offers.'.format(
        (timer_end - timer_start).seconds,
        offers_counter
    ))


if __name__ == '__main__':
    current_time = datetime.datetime.now()
    file_stamp = current_time.strftime('%Y%m%d_%H%M')
    file_name = 'cian_flats_{}.csv'.format(file_stamp)
    with open(file_name, 'w', newline='', encoding='utf-8') as flats_file:
        flats_writer = csv.writer(flats_file, delimiter=' ', quotechar='|')
        flats_writer.writerow([
            'ID', 'Link', 'Price', 'Rooms', 'Views', 'Square', 'Floor', 'Total Floors', 'Area', 'Flat number',
            'Street', 'District', 'District 2', 'Description', 'Flat Type', 'Toilet', 'Balcony', 'Repair',
            'Window View', 'House Type'
        ])
    init_parsing(file_name)
