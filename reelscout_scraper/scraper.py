import logging
import time
import datetime

import requests
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


class ReelScout:
    def __init__(self, driver, db):
        self.driver = driver
        self.db = db

    def get_pagination_lenght(self):
        self.driver.get('https://rs.locationshub.com/Home/Index?page=1')

        time.sleep(5)

        pagination = self.driver.find_element(By.CLASS_NAME, 'pagination')
        total_count = pagination.find_element(By.CLASS_NAME, 'totalCount').text

        logging.info('[ REELSCOUT ]: Pagination length: ' + total_count)

        return total_count

    def parse_page(self, link):
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')

        time.sleep(1)

        try:
            host_name = soup.find('div', class_='categories').find('a', class_='brandcolor').text
        except AttributeError:
            # if host name not available
            host_name = ''

        try:
            location_name = soup.find('h3').text
        except AttributeError:
            location_name = ''

        try:
            listing_location = soup.find('div', class_='heading-properties').find('p').text
        except AttributeError:
            listing_location = ''

        try:
            phone_num = soup.findAll('div', class_='categories')[-1].find('p').text
            phone_num = ''.join(i for i in phone_num if i.isdigit())[:10]
        except Exception as e:
            print(e)
            phone_num = None

        print('\n\n')

        print(link)
        print(location_name)
        print(listing_location)
        print(host_name)
        print(phone_num)

        print('\n\n')

        self.db.add_listing('reelscout', link, location_name, host_name, listing_location, phone_num, None, None,
                            datetime.datetime.now())

    def proceed_pages(self, pag_len):
        for page_num in range(1, pag_len + 1):
            self.driver.get('https://rs.locationshub.com/Home/Index?page=' + str(page_num))
            logging.info('Processing url: ' + 'https://rs.locationshub.com/Home/Index?page=' + str(page_num))
            time.sleep(5)
            boxes = self.driver.find_elements(By.CLASS_NAME, 'property-outer-box')

            for box in boxes:
                link = box.find_element(By.TAG_NAME, 'h1').find_element(By.TAG_NAME, 'a').get_attribute('href')
                self.parse_page(link)

    def start(self):
        logging.info('[ REELSCOUT ]: Parsing started')
        self.proceed_pages(int(self.get_pagination_lenght()))
