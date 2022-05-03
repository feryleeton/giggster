import logging
import time
import datetime
import requests
import urllib3

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from selenium.webdriver.common import action_chains


class Yogafinder:
    def __init__(self, db, driver, help_driver):
        self.db = db
        self.driver = driver
        self.help_driver = help_driver

    def get_states(self, url):
        self.driver.get(url)

        menu = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.menu')))
        states = WebDriverWait(menu, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a')))

        links = []

        for state in states:
            links.append(state.get_attribute('href'))

        return links

    def parse_cities(self, state_link):
        self.driver.get(state_link)

        menu = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.menu')))
        cities = WebDriverWait(menu, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a')))

        links = []

        for city in cities:
            links.append(city.get_attribute('href'))

        return links

    def pass_redirect(self, url):
        try:
            self.help_driver.get(url)
        except:
            return None

        time.sleep(1)
        redirect = self.help_driver.current_url

        if '?yoganumber=' in redirect:
            return None

        return redirect

    def parse_card(self, card, city):
        location_name = None
        website_url = None

        insidetext_blocks = card.find_elements(By.CSS_SELECTOR, 'div.insidetext')
        try:
            title_block__links = insidetext_blocks[0].find_elements(By.CSS_SELECTOR, 'a')
        except Exception as e:
            title_block__links = []

        location_name = insidetext_blocks[0].text
        if title_block__links:
            website_url = self.pass_redirect(title_block__links[0].get_attribute('href'))
            for link in title_block__links:
                location_name.replace(link.text, '')
        else:
            pass

        try:
            location_address = insidetext_blocks[1].text
        except:
            location_address = None

        try:
            phone_num = insidetext_blocks[2].text.replace('Tel: ', '')
        except:
            phone_num = None

        location_link = city + str(location_name).replace(',', ' ').replace(' ', '_')
        print(location_link)
        print(location_name)
        print(website_url)
        print(location_address)
        print(phone_num)
        print('\n\n')

        try:
            self.db.add_listing('yogafinder', location_link, location_name, None, location_address, phone_num, website_url,
                                None, datetime.datetime.now())
        except Exception as e:
            print('Add listing error')
            print(e)

    def parse_city(self, city):
        self.driver.get(city)
        cards = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#maininfo')))

        if cards:
            for card in cards:
                try:
                    self.parse_card(card, city)
                except Exception as e:
                    print('Card skipped, got error: ' + str(e))
                    continue

    def parse_country(self, country):
        logging.info('Parsing ' + str(country) + ' states')
        url = 'https://www.yogafinder.com/yogaarea.cfm?yogacountry=' + str(country)
        states = self.get_states(url)
        for state in states:
            try:
                cities = self.parse_cities(state)
            except Exception as e:
                cities = []
                print('No cities found on state: ' + str(state))
                print(str(e))
            for city in cities:
                print(country + ' : ' + state + ' : ' + city)
                try:
                    self.parse_city(city)
                except:
                    print('Skipped empty city link: ' + str(city))

        logging.info(str(country) + ' states parsed !')

    def start(self):
        countries = ['England', 'New%20Zealand', 'Australia', 'USA']

        for country in countries:
            logging.info('Processing country: ' + str(country))
            self.parse_country(country)
