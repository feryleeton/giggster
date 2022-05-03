import logging
import time
import re
import requests
from bs4 import BeautifulSoup
import datetime


class WeddingWire:
    def __init__(self, db):
        self.db = db

    def start(self):
        page = 1
        while True:
            r = requests.get(f'https://www.weddingwire.com/shared/search?group_id=1&page={page}')
            if r.status_code == 403:
                logging.debug('End of pages')
                return
            self.get_info(r)
            page += 1

    def get_info(self, page):
        links = self.get_links(page)
        for link in links:
            venue = requests.get(link)
            soup = BeautifulSoup(venue.text, 'html.parser')
            location_name = self.get_location_name(soup)
            address = self.get_address(soup)
            phone = self.get_phone(soup)
            reviews = self.get_reviews(soup)
            website = self.get_website(soup)

            self.db.add_listing('weddingwire', link, location_name, None, address, phone, website, reviews,
                                datetime.datetime.now())

            # with open('weddingwire.csv', 'a+') as f:
            #     f.write(f'{link},{location_name},,{address},{phone},{reviews},{website}\n')
            time.sleep(3)

    @staticmethod
    def get_links(page):
        links = []
        try:
            soup = BeautifulSoup(page.text, 'html.parser')
            for link in soup.find_all('a', {'class': 'vendorTile__title'}):
                links.append(link['href'])
                logging.info(f'[ WEDDING WIRE ]: got links from page = {page}')
            return links
        except:
            logging.error('[ WEDDING WIRE ]: Something went from while was getting pages')

    @staticmethod
    def get_location_name(soup):
        try:
            name = soup.find('h1', {'class': 'storefrontHeading__title'}).text.replace(',', '')
            logging.info('[ WEDDING WIRE ]: got location name')
            return name
        except:
            logging.error('[ WEDDING WIRE ]: No location name')
        return None

    def get_address(self, soup):
        try:
            address = self.clean_string(soup.find('div', {'class': 'app-static-map-header '
                                                                   'storefrontAddresses__header active'}).text)
            logging.info('[ WEDDING WIRE ]: got address')
            return address
        except:
            logging.error('[ WEDDING WIRE ]: No address')
        return None

    def get_phone(self, soup):
        try:
            phone = self.clean_string(soup.find('span', {'class': 'app-phone-replace'}).text)
            logging.info('[ WEDDING WIRE ]: got phone number')
            return phone
        except:
            logging.error('[ WEDDING WIRE ]: No phone number')
        return None

    @staticmethod
    def get_reviews(soup):
        try:
            review = soup.find('span', {'class': 'storefrontHeading__reviewsValue'}).text.replace(',', '')
            logging.info('[ WEDDING WIRE ]: got reviews count')
            return review
        except:
            logging.error('[ WEDDING WIRE ]: No reviews')
        return None

    @staticmethod
    def get_website(soup):
        try:
            website = soup.find('span', {'class': 'link storefrontHeading__contactItem app-storefront-visit-website'})[
                'data-href']
            logging.info('[ WEDDING WIRE ]: got website')
            return website
        except:
            logging.error('[ WEDDING WIRE ]: No website')
        return None

    @staticmethod
    def clean_string(web_string):
        clear_words = web_string.replace(',', '').replace('See on map', '').replace('\n', '')
        return ' '.join(re.split(r'\s+', clear_words))

    @staticmethod
    def check_if_exist(link):
        with open('weddingwire.csv', encoding="utf8") as f:
            for line in f:
                if link in line:
                    return True
            return False


