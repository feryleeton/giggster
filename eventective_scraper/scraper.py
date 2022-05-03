import logging
import time
import re
import requests
import datetime
from bs4 import BeautifulSoup


class Eventective:
    def __init__(self, db):
        self.db = db

    def start(self):
        locations = self.get_all_wedding_locations()
        links = self.get_cities_links(locations)

        print('LINKS: \n')
        print(links)
        print('\n LOCATIONS: \n')
        print(locations)

        for link in links:
            page = 1
            while page in self.get_pages_count(link):
                r = requests.get(link + f'?p={page}')
                self.get_info(r)
                page += 1

    def get_info(self, page):
        links = self.get_links(page)
        for link in links:
            try:
                if not self.db.check_pkey('eventective', link):
                    print('Parsing link: ' + str(link))
                    venue = requests.get(link)
                    soup = BeautifulSoup(venue.text, 'html.parser')
                    location_name = self.get_location_name(soup)
                    if location_name is None:
                        continue
                    address = str(self.get_address(soup))
                    phone = str(self.get_phone(soup))
                    website = str(self.get_website(soup))

                    print(location_name)
                    print(address)
                    print(phone)
                    print(website)

                    self.db.add_listing('eventective', link, location_name, None, address, phone, website, None,
                                        datetime.datetime.now())

                    # with open('eventective.csv', 'a+') as f:
                    #     f.write(f'{link},{location_name},,{address},{phone},,{website}\n')
                    time.sleep(3)
                else:
                    print('Skipped link')
            except:
                continue

    @staticmethod
    def get_links(page):
        links = []
        try:
            soup = BeautifulSoup(page.text, 'html.parser')
            for link in soup.find_all('a', {'class': 'provider-name'}):
                links.append(link['href'])
            logging.info(f'[ WEDDING WIRE ]: got links from page = {page}')
            return links
        except (AttributeError, TypeError):
            logging.error('[ Eventective ]: Something went from while was getting pages')

    @staticmethod
    def get_location_name(soup):
        try:
            name = soup.find('h1', {'style': 'font-weight: 300; margin-bottom: 0;'}).text.replace(',', '')
            logging.info('[ Eventective ]: got location name')
            return name
        except (AttributeError, TypeError):
            logging.error('[ Eventective ]: No location name')
        return None

    def get_address(self, soup):
        try:
            address = self.clean_string(soup.find('div', {'class': 'h4 eve-address-nav eve-hover-pointer'}).text)
            logging.info('[ Eventective ]: got address')
            return address
        except (AttributeError, TypeError):
            logging.error('[ Eventective ]: No address')
        return None

    @staticmethod
    def get_phone(soup):
        try:
            phone = soup.find('a', {'id': 'phoneHyperLink'}).text
            logging.info('[ Eventective ]: got phone number')
            return phone
        except AttributeError:
            logging.error('[ Eventective ]: No phone number')
        return None

    @staticmethod
    def get_website(soup):
        try:
            website = soup.find('div', {'id': 'detail-page'}).find('a', {'rel': 'nofollow', 'target': 'blank'})['href']
            logging.info('[ Eventective ]: got website link')
            return website
        except TypeError:
            logging.error('[ Eventective ]: No website link')
        return None

    @staticmethod
    def clean_string(web_string):
        clear_words = web_string.replace(',', '')
        return ' '.join(re.split(r'\s+', clear_words))

    @staticmethod
    def get_all_wedding_locations():
        types_links = ['https://www.eventective.com/wedding-venues/',
                       'https://www.eventective.com/party-event-venues/',
                       'https://www.eventective.com/meeting-venues/']
        links = []
        for type_link in types_links:
            try:
                r = requests.get(type_link).text
                soup = BeautifulSoup(r, 'html.parser')
                divs = soup.find_all('div', {'class': 'col-md-2 col-sm-3 col-xs-6'})
                for div in divs:
                    all_a = div.find_all('a')
                    for a in all_a:
                        if a.find_all('strong'):
                            links.append(a['href'])
                logging.info('[ Eventective ]: got all links')
            except:
                logging.error('[ Eventective ]: something went wrong with getting links')
        return links

    @staticmethod
    def get_cities_links(locations):
        links = []
        for location in locations:
            cities = requests.get(location).text
            soup = BeautifulSoup(cities, 'html.parser')
            try:
                all_a = soup.find('div', {'class': 'col-sm-2 col-xs-6'}).find_all('a')
                for a in all_a:
                    logging.info('[ Eventective ]: got venue city')
                    if '?alpha' in a['href']:
                        print('Skipped link')
                    else:
                        links.append(a['href'])
            except AttributeError:
                links.append(location)
            try:
                all_a = soup.find('div', {'class': 'col-sm-3 col-xs-12'}).find_all('a')
                for a in all_a:
                    logging.info('[ Eventective ]: got venue city')
                    if '?alpha' in a['href']:
                        print('Skipped link')
                    else:
                        links.append(a['href'])
            except AttributeError:
                links.append(location)
        return links

    @staticmethod
    def get_pages_count(link):
        r = requests.get(link).text
        soup = BeautifulSoup(r, 'html.parser')
        try:
            pages = [int(x.text) for x in soup.find('ul', {'class': 'pagination'}).find_all('a') if x.text.isdigit()]
            logging.info('[ Eventective ]: got pages count')
            return pages
        except AttributeError:
            logging.error('[ Eventective ]: something went wrong!!!')
            return []
