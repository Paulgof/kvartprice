import csv
import datetime
import re
from itertools import product

import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError

CITY = {
    'name': 'krasnodar',
    'cian_region': 4820
}
MAX_PAGE = 75
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


def str_square_to_float(str_square):
    """
    Функция для перевода строки в определенном формате в число с плавающей точкой
    ex.: '1-комн. квартира, 44,22 м²' -> 44.22
    """
    return float(re.search(r'(\d+,?\d*)\sм', str_square)[1].replace(',', '.'))


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

    flat_desc_dict = {}
    flat_description = offer_soup.select('div[data-name="Description"] div[itemscope=""] > div')
    for flat_desc_block in [desc_block.get_text(separator='::') for desc_block in flat_description]:
        desc_value, desc_key = flat_desc_block.split('::')
        flat_desc_dict[desc_key] = desc_value

    flat_square = flat_desc_dict.get('Общая')
    flat_square_value = str_square_to_float(flat_square) if flat_square else ''
    live_square = flat_desc_dict.get('Жилая')
    live_square_value = str_square_to_float(live_square) if live_square else ''
    kitchen_square = flat_desc_dict.get('Кухня')
    kitchen_square_value = str_square_to_float(kitchen_square) if kitchen_square else ''
    floor = flat_desc_dict.get('Этаж')
    flat_floor, total_floors = map(int, floor.split(' из '))

    geo_info: str = offer_soup.select_one('div[data-name="Geo"] span[itemprop="name"]')['content']
    geo_info_split = geo_info.split(', ')
    area_value = geo_info_split[2]
    flat_number = geo_info_split[-1]
    street = geo_info_split[-2]
    district_main = geo_info_split[3] if len(geo_info_split) > 5 else ''
    district_local = geo_info_split[4] if len(geo_info_split) > 6 else ''

    flat_main_info = offer_soup.select('li[data-name="AdditionalFeatureItem"]')
    dict_main_info = {}
    for info in [main_info_text.get_text(separator='::') for main_info_text in flat_main_info]:
        info_key, info_value = info.split('::')
        dict_main_info[info_key] = info_value

    flat_cian_info = offer_soup.select('div[data-name="BtiHouseData"] div[data-name="Item"]')
    dict_cian_info = {}
    for info in [cian_info_text.get_text(separator='::') for cian_info_text in flat_cian_info]:
        info_key, info_value = info.split('::')
        dict_cian_info[info_key] = info_value

    description = offer_soup.select_one('div[data-name="Description"] p[itemprop="description"]')
    description_value = description.get_text()

    return {
        'price': price_value,
        'views': views_total_value,
        'total_square': flat_square_value,
        'live_square': live_square_value,
        'kitchen_square': kitchen_square_value,
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
        'ceiling': dict_main_info.get('Высота потолков', ''),
        'house_type': dict_cian_info.get('Тип дома', ''),
        'house_year': flat_desc_dict.get('Построен', ''),
        'lifts': dict_cian_info.get('Лифты', ''),
        'parking': dict_cian_info.get('Парковка', ''),
        'gas': dict_cian_info.get('Газоснабжение', '')
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
    scraped_offers = set()
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
            print('Scraping offer on url', offer_link)
            try:
                if offer_id in scraped_offers:
                    print('[DOUBLE] Offer {} already scraped. Pass to next.'.format(offer_id))
                    continue

                offers_data[offer_id] = {  # todo: use asyncio get
                    'link': offer_link,
                    'room_type': room_type,
                    'soup': scrape_offer(offer_link)
                }
                scraped_offers.add(offer_id)
            except HTTPError as http_error:
                print("[HTTP]: Couldn't scrape offer.", http_error)
                continue
            except Exception as e:
                print('[DNG]: Unresolved exception. Continue scraping offers.', e)
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
                csv_writer = csv.writer(csv_file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow([
                    offer_id, offer_data['link'], flat_info['price'], ROOM_TYPES[offer_data['room_type']][0],
                    flat_info['views'], flat_info['total_square'], flat_info['live_square'],
                    flat_info['kitchen_square'], flat_info['floor'], flat_info['total_floors'],
                    flat_info['area'], flat_info['flat_number'], flat_info['street'], flat_info['district_main'],
                    flat_info['district_local'], flat_info['description'].replace(';', ' ').replace('\n', ' '), 
                    flat_info['flat_type'], flat_info['toilet'], flat_info['balcony'], flat_info['repair_status'], 
                    flat_info['window_view'], flat_info['ceiling'], flat_info['house_type'], flat_info['house_year'], 
                    flat_info['lifts'], flat_info['parking'], flat_info['gas']
                ])

        print('[I] Batch has been parsed and saved.')

    timer_end = datetime.datetime.now()
    print('Scraping past in {} seconds. Fetched {} offers.'.format(
        (timer_end - timer_start).seconds,
        len(scraped_offers)
    ))


def main():
    current_time = datetime.datetime.now()
    file_stamp = current_time.strftime('%Y%m%d_%H%M')
    file_name = 'cian_flats_{}.csv'.format(file_stamp)
    with open(file_name, 'w', newline='', encoding='utf-8') as flats_file:
        flats_writer = csv.writer(flats_file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        flats_writer.writerow([
            'ID', 'Link', 'Price', 'Rooms', 'Views', 'Square', 'Live Square', 'Kitchen', 'Floor', 'Total Floors',
            'Area', 'Flat number', 'Street', 'District', 'District 2', 'Description', 'Flat Type', 'Toilet', 'Balcony',
            'Repair', 'Window View', 'Ceiling', 'House Type', 'House Year', 'Lifts', 'Parking', 'Gas'
        ])
    init_parsing(file_name)


if __name__ == '__main__':
    main()
