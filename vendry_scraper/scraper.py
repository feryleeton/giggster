import datetime
import re
import time
import logging

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup


class Vendry:
    def __init__(self, driver, db):
        self.driver = driver
        self.db = db

    def parse_locations(self):
        logging.info('[ VENDRY ]: Parsing locations')

        self.driver.get('https://thevendry.com/search')

        venues_container = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.venues-by')))[2]

        links = WebDriverWait(venues_container, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'a')))

        locations_links = []

        for link in links:
            href = link.get_attribute('href')
            # if it is location link
            if 'https://thevendry.com/venues/usa/' in href:
                locations_links.append(link.get_attribute('href'))

        return locations_links

    def parse_card(self, link):
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')

        location_name = soup.find('div', class_='header__title').find('h1').text

        try:
            location_address = soup.find('div', class_='header__extra').text.split('Max S')[0]

        except Exception as e:
            print(e)
            location_address = None

        try:
            reviews_count = soup.find('div', class_='container').text
            reviews_count = re.search(r"Reviews (.*?)Write a review.", reviews_count).group(1).replace('(', '').replace(
                ')', '')
        except:
            reviews_count = None

        print(link)
        print(location_name)
        print(location_address)
        print(reviews_count)
        print('\n\n\n')

        try:
            self.db.add_listing('vendry', link, location_name, None, location_address, None, None,
                                int(reviews_count), datetime.datetime.now())
        except Exception as e:
            print('Add listing error')
            print(e)

    def parse_cards(self, card_links):
        for link in card_links:
            try:
                if not self.db.check_pkey('vendry', link):
                    self.parse_card(link)
                else:
                    print('Skipped card: ' + str(link))
            except Exception as e:
                print('Cant parse card: ' + str(link))
                print(e)

    def proceed_location(self, link):
        pag_counter = 1
        while True:
            self.driver.get(link + '?p=' + str(pag_counter))

            content_container = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.content')))

            try:
                cards = WebDriverWait(content_container, 5).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.business__info')))

                card_links = []

                for card in cards:
                    card_links.append(card.find_element(By.TAG_NAME, 'a').get_attribute('href'))

                self.parse_cards(card_links)

            except TimeoutException:
                logging.info('[ VENDRY ]: Pagination parsing finished')
                break

            pag_counter = pag_counter + 1

    def start(self):
        locations_links = self.parse_locations()

        for link in locations_links:
            logging.info('[ VENDRY ]: Parsing location: ' + str(link))
            self.proceed_location(link)
