import datetime
import logging
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys


class Breawer:
    def __init__(self, driver, db):
        self.db = db
        self.driver = driver

    def parse_card(self, card):
        location_name = WebDriverWait(card, 1).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h3'))).text

        try:
            address_street = WebDriverWait(card, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'p[itemprop="streetAddress"]'))).text
        except TimeoutException:
            address_street = ''

        try:
            address_locality = WebDriverWait(card, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span[itemprop="addressLocality"]'))).text
        except TimeoutException:
            address_locality = ''

        try:
            address_region = WebDriverWait(card, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span[itemprop="addressRegion"]'))).text
        except TimeoutException:
            address_region = ''

        try:
            phone_num = WebDriverWait(card, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span[itemprop="telephone"]'))).text
        except TimeoutException:
            phone_num = None

        try:
            website = WebDriverWait(card, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[itemprop="image"]'))).text
        except TimeoutException:
            website = None

        listing_location = address_street + ', ' + address_locality + ', ' + address_region
        link = (location_name + address_locality + address_street + address_region)

        print(location_name)
        print(address_street)
        print(address_locality)
        print(address_region)
        print(phone_num)
        print(website)

        print('\n\n\n')

        try:
            self.db.add_listing('breawer', link, location_name, None, listing_location, phone_num, website,
                                None, datetime.datetime.now())
        except Exception as e:
            print('Cant add listing to db: ' + str(e))

    def parse_cards(self, cards):
        counter = 0
        for card in cards:
            counter = counter + 1
            print('[ ' + str(counter) + ' ]')
            self.parse_card(card)

    def do_parsing(self):
        # finding cards to parse

        counter = 0

        while True:

            time.sleep(5)

            try:
                block = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'slide-up-fade-in')))[-1]
            except TimeoutException:
                print('Block #' + str(counter) + ' not found, stopping...')
                break
            counter = counter + 1
            print('Parsing block #' + str(counter))

            try:
                cards = WebDriverWait(block, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'company-listing')))
            except TimeoutException:
                print('Cards on block #' + str(counter) + ' not found, stopping...')
                break

            if not cards:
                logging.warning('[ BREAWER ]: Cant find new cards, stopping...')
                break
            else:
                self.parse_cards(cards)

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)

    def start(self):
        self.driver.get('https://www.brewersassociation.org/directories/breweries/')
        self.do_parsing()

        print('Finished')