import time
import logging
import datetime

import coloredlogs
from selenium import webdriver
import requests
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WeddingSpot:
    def __init__(self, driver, db):
        self.driver = driver
        self.db = db

    @staticmethod
    def get_phone(link):
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
        if soup.find('span', 'SecondaryCTA--hidden') is None:
            return None
        return soup.find('span', 'SecondaryCTA--hidden').text

    @staticmethod
    def get_link(div):
        try:
            link = div.find_element_by_tag_name('a').get_attribute('href')
            logging.info('[ WEDDING SPOT ]: got venue link')
            return link
        except:
            logging.error('[ WEDDING SPOT ]: something went wrong with link scraping')
            return None

    @staticmethod
    def get_name(div):
        try:
            name = div.find_element(By.CLASS_NAME, 'venueCard--title').text.replace(',', '')
            logging.info('[ WEDDING SPOT ]: got venue name')
            return name
        except:
            logging.error('[ WEDDING SPOT ]: something went wrong with name scraping')
            return None

    @staticmethod
    def get_address(link):
        try:
            r = requests.get(link)
            soup = BeautifulSoup(r.text, 'html.parser')
            address = soup.find_all('div', {'class': 'VenuePage--detail'})[3]
            address = address.text.replace(',', '').replace('\n', '').replace('Location:', '')
            logging.info('[ WEDDING SPOT ]: got venue address')
            return address
        except:
            logging.error('[ WEDDING SPOT ]: something went wrong with address scraping')
            return None

    def get_all_info(self, page):
        self.driver.get(f'https://www.wedding-spot.com/wedding-venues/?page={page}&sr=1')
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        all_venues = self.driver.find_elements(By.CLASS_NAME, 'venueCard--wrapper')
        for div_path in all_venues:
            link = self.get_link(div_path)
            name = self.get_name(div_path)
            address = self.get_address(link)
            phone = self.get_phone(link)
            self.db.add_listing('weddingspot', link, name, None, address, phone, None, None,
                                datetime.datetime.now())
            # with open('wedding_spot.csv', 'a+') as f:
                # f.write(f'{link},{name},None,{address},{phone},None\n')
            time.sleep(3)

    @staticmethod
    def get_pages_count():
        try:
            page = requests.get('https://www.wedding-spot.com/wedding-venues/?sr=1')
            soup = BeautifulSoup(page.text, 'html.parser')
            pages_count = soup.find_all('button', {'class': 'css-158cw5n', 'aria-label': ''})
            return int(pages_count[-1].text)
        except:
            logging.error('[ WEDDING SPOT: something went wrong with getting pages count]')

    def start(self):
        pages = self.get_pages_count()
        logging.info('[ WEDDING SPOT ]: got pages count')
        for page in range(1, pages+1):
            self.get_all_info(page)

    @staticmethod
    def check_if_exist(link):
        with open('wedding_spot.csv', encoding="utf8") as f:
            for line in f:
                if link in line:
                    return True
            return False


