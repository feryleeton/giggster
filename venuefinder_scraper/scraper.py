import time
import logging
import datetime

from selenium.webdriver.support.ui import Select
import requests
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re

username = 'Nikola'
password = 'shepa123'

venues_type_class_name = ['resultCardGLD', 'resultCardSIL', 'resultCardPRE',
                          'resultsListBronze', 'resultsListFreeOdd', 'resultsListFreeEven']


class Venuefinder:
    def __init__(self, driver, db):
        self.driver = driver
        self.db = db

    def start(self):
        self.driver.get('https://www.venuefinder.com/')
        self.login_on_site()
        countries = self.get_all_countries()
        for country in countries:
            self.driver.get('https://www.venuefinder.com/')
            self.select_country(country)
            page_exist = True
            while page_exist:
                for class_name in venues_type_class_name:
                    hrefs = self.get_venues_href_on_page(class_name)
                    self.get_info(hrefs)
                try:
                    self.driver.find_element(By.XPATH, '//*[@id="NextItemLink" and @class="page-link"]').click()
                    time.sleep(2)
                except:
                    logging.info(f'[ VENUE FINDER ]: pages with country={country} was ended')
                    page_exist = False
        logging.info('[ VENUE FINDER ]: end of scripting')

    @staticmethod
    def get_all_countries():
        try:
            r = requests.get('https://www.venuefinder.com/')
            soup = BeautifulSoup(r.text, 'html.parser')
            options_tag = soup.find('select', {'name': 'ctl00$SearchBarContent$searchBar$QS_CountryDropDownList'}).find_all('option')
            options_values = [value['value'] for value in options_tag[1:]]
            logging.info('[ Venuefinder ]: got all countries')
            return options_values
        except:
            logging.error('[ Venuefinder ]: something went wrong while getting countries')
            return

    def select_country(self, country):
        try:
            time.sleep(2)
            sel = Select(self.driver.find_element(By.NAME, 'ctl00$SearchBarContent$searchBar$QS_CountryDropDownList'))
            sel.select_by_value(country)
            self.driver.find_element(By.NAME, 'ctl00$SearchBarContent$searchBar$QS_SearchButton').click()
            time.sleep(2)
            logging.info(f'[ VENUEFINDER ]: select country={country}')
        except:
            logging.error('[ VENUEFINDER ]: something went wrong with country selecting')
            return

    def get_venues_href_on_page(self, class_name):
        try:
            hrefs = []
            venues = self.driver.find_elements(By.CLASS_NAME, class_name)
            for venue in venues:
                if not self.db.check_pkey('venuefinder', link):
                    hrefs.append(venue.find_element(By.TAG_NAME, 'a').get_attribute('href'))
            logging.info(f'[ VENUEFINDER ]: got hrefs from venues with class={class_name}')
            return hrefs
        except:
            logging.error(f'[ VENUEFINDER ] something went wrong with href scraping in class={class_name}')
            return

    def login_on_site(self):
        try:
            self.driver.find_element(By.XPATH, '//*[@id="ctl00_theLinkBar_loginLink"]/li/a').click()
            time.sleep(1)
            username_box = self.driver.find_element(By.ID, 'ctl00_BodyContent_Login1_UserName')
            password_box = self.driver.find_element(By.ID, 'ctl00_BodyContent_Login1_Password')
            username_box.send_keys(username)
            password_box.send_keys(password)
            self.driver.find_element(By.ID, 'LoginButton').click()
            logging.info('[ VENUE FINDER ]: login to site')
        except:
            logging.error('[ VENUE FINDER ]: something went wrong with login ')
            return

    def get_info(self, hrefs):
        try:
            for href in hrefs:
                r = requests.get(href)
                time.sleep(3)
                soup = BeautifulSoup(r.text, 'html.parser')
                name = soup.find('h1', {'class': 'venueNameLabel'}).text
                address = soup.find('table', {'id': 'profileTable'}).find_all('td')[1].text.\
                    replace('Address:', '').replace('view on map', '').replace('\n', '').strip()
                phone = soup.find('span', {'id': 'telephoneLabel'}).text
                website = self.get_website(soup.find('tr', {'id': 'urlRow'}).find('a')['href'])
                self.db.add_listing('venuefinder', href, name, None, address, phone, website, None,
                                    datetime.datetime.now())
                # self.save_info(href, name, address, phone, website)
                logging.info(f'[ VENUE FINDER ]: got info from link={href}')
        except Exception as e:
            logging.error('[ VENUE FINDER ] something went wrong with venue data scraping')
            print(e)
            return

    def save_info(self, link, name, address, phone, website):
        try:
            if not self.check_if_exist(link):
                with open('venuefinder.csv', 'a+') as f:
                    f.write(f'{link},{name},None,{address},{phone},{website}\n')
                logging.info('[ VENUE FINDER ]: save info to csv')
        except:
            logging.error('[ VENUE FINDER ]: something went wrong with saving info ')

    @staticmethod
    def check_if_exist(link):
        with open('venuefinder.csv', encoding="utf8") as f:
            for line in f:
                if link in line:
                    return True
            return False

    def get_website(self, full_string):
        return re.findall(r'(?i)\b((?:www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}))', full_string)[1].replace('2f', '')

