from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
import coloredlogs
import datetime


class Tripleseat:
    def __init__(self, driver_, db_):
        self.driver = driver_
        self.db = db_

    def start(self):
        venue_types = ['https://venues.tripleseat.com/venue_directory/search?venue_type=Hotel',
                       'https://venues.tripleseat.com/venue_directory/search?venue_type=Restaurant',
                       'https://venues.tripleseat.com/venue_directory/search?venue_type%5B%5D='
                       'Arcade&venue_type%5B%5D=Bakery&venue_type%5B%5D=Bed+%26+Breakfast&venue_type%5B%5D='
                       'Boat&venue_type%5B%5D=Bowling&venue_type%5B%5D=Brewery&venue_type%5B%5D=Caterer&venue_type'
                       '%5B%5D=Cocktail+Lounge&venue_type%5B%5D=Conference+Center&venue_type%5B%5D'
                       '=Country+Club&venue_type%5B%5D=Distillery&venue_type%5B%5D=Entertainment&venue_type%5B%5D='
                       'Event+Hall&venue_type%5B%5D=Event+Space&venue_type%5B%5D=Food+Hall&venue_type%5B%5D='
                       'Food+Truck&venue_type%5B%5D=Gallery&venue_type%5B%5D=Golf+Course&venue_type%5B%5D='
                       'Inn&venue_type%5B%5D=Museum&venue_type%5B%5D=Night+Club&venue_type%5B%5D=Other&'
                       'venue_type%5B%5D=Resort&venue_type%5B%5D=Stadium&venue_type%5B%5D=Theater&venue_type%5B%5D='
                       'Unique&venue_type%5B%5D=Vineyard&venue_type%5B%5D=Wedding&venue_type%5B%5D=Winery']
        for venue_type in venue_types:
            self.driver.get(venue_type)
            logging.info(f'[ TRIPLE SEAT ]: venue type = {venue_type}')
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            while True:
                try:
                    venues = self.get_page_venues()
                    for venue in venues:
                        link = self.get_venue_link(venue)
                        name = self.get_venue_name(venue)
                        address = self.get_venue_address(venue)
                        phone = self.get_venue_phone(venue)
                        website = self.get_venue_website(venue)

                        print(link)
                        print(name)
                        print(address)
                        print(phone)

                        self.db.add_listing('tripleseat', link, name, None, address, phone, website, None,
                                            datetime.datetime.now())

                        time.sleep(5)
                except Exception as e:
                    print(e)
                try:
                    self.driver.find_element(By.CLASS_NAME, 'next_page').click()
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    logging.info('[ TRIPLE SEAT ]: went to new page')
                except:
                    logging.info(f'[ TRIPLE SEAT ]: end with the venue={venue_type}')
                    break



    @staticmethod
    def get_venue_link(venue):
        try:
            link = venue.find_element(By.CLASS_NAME, 'header').find_element(By.TAG_NAME, 'a').get_attribute('href')
            logging.info(f'[ TRIPLE SEAT ]: got link = {link}')
            return link
        except:
            logging.error('[ TRIPLE SEAT ]: no link')
            return

    @staticmethod
    def get_venue_name(venue):
        try:
            name = venue.find_element(By.CLASS_NAME, 'header').find_element(By.TAG_NAME, 'h3').text.replace(',', '')
            logging.info('[ TRIPLE SEAT ]: got name')
            return name
        except:
            logging.error('[ TRIPLE SEAT ]: no name')
            return

    @staticmethod
    def get_venue_address(venue):
        try:
            address = venue.find_element(By.CLASS_NAME, 'header').find_element(By.CLASS_NAME, 'map_link').text\
                .replace(',', '')
            logging.info('[ TRIPLE SEAT ]: got address')
            return address
        except:
            logging.error('[ TRIPLE SEAT ]: no address')
            return

    @staticmethod
    def get_venue_phone(venue):
        try:
            phone = venue.find_element(By.CLASS_NAME, 'header').find_elements(By.TAG_NAME, 'li')[1].find_element(
                By.TAG_NAME, 'a').get_attribute('href').replace('tel:', '')
            logging.info('[ TRIPLE SEAT ]: got phone')
            return phone
        except:
            logging.error('[ TRIPLE SEAT ]: no phone')
            return

    @staticmethod
    def get_venue_website(venue):
        try:
            website = venue.find_element(By.CLASS_NAME, 'header').find_element(By.TAG_NAME, 'small').find_element(
                By.TAG_NAME, 'a').get_attribute('href')
            logging.info('[ TRIPLE SEAT ]: got website')
            return website
        except:
            logging.error('[ TRIPLE SEAT ]: no website')
            return

    def get_search_result(self):
        try:
            search_result = self.driver.find_element(By.CLASS_NAME, 'search-results')
            logging.info('[ TRIPLE SEAT ]: got search result')
            return search_result
        except:

            logging.error('[ TRIPLE SEAT ]: cant get page element')

    def get_page_venues(self):
        try:
            time.sleep(4)
            venues = [x for x in self.get_search_result().find_elements(By.CLASS_NAME, 'venue_details') if
                      not x.get_attribute('style')]
            logging.info('[ TRIPLE SEAT ]: got venues from page')
            return venues
        except:
            logging.error('[ TRIPLE SEAT ]: cant get venues from page')
            return []

    @staticmethod
    def save_info(link, name, address, phone, website):
        try:
            with open('tripleseat.csv', 'a+') as f:
                f.write(f'{link},{name},,{address},{phone},,{website}\n')
            logging.info('[ TRIPLE SEAT ]: save info to csv')
        except:
            logging.error('[ TRIPLE SEAT ]: something went wrong with saving info ')

    @staticmethod
    def check_if_exist(link):
        with open('tripleseat.csv', encoding="utf8") as f:
            for line in f:
                if (link is None) or (link in line):
                    return True
            return False
