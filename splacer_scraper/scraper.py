import logging
import time
import datetime
import requests

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from selenium.webdriver.common import action_chains


class Splacer:
    # confiig useragent rotation
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

    def __init__(self, driver, db):
        self.driver = driver
        self.db = db

    def parse_activities(self):
        """
        This method parses activities from target website: peerspace.com,
        to form a search query for each activity in future and group parsed items based on this in monthly report

        returns a list of parsed activities
        """

        # redirecting to activities page

        logging.info('[ SPLACER ]: Activity parsing started')

        self.driver.get('https://www.splacer.co/search/activities')

        # finding the container div of available activities on the page

        activities_container = self.driver.find_element(By.CLASS_NAME, 'seo-list')

        # finding all activity categories

        categories = activities_container.find_elements(By.CLASS_NAME, 'category')

        result = dict()

        for category in categories:
            category_name = category.find_element(By.TAG_NAME, 'h3').text
            activities = category.find_elements(By.TAG_NAME, 'a')
            category_activities = []

            for activity in activities:
                category_activities.append(activity.text)

            result[str(category_name)] = list(category_activities)

        return result

    def parse_locations(self):
        """
        This method parses locations from target website: peerspace.com,
        to form a search query for each activity in future and group parsed items based on this in monthly report

        returns a list of parsed locations
        """
        # redirecting to locations page

        logging.info('[ SPLACER ]: Locations parsing started')

        self.driver.get('https://www.splacer.co/rent/locations')

        # finding the container div of available locations on the page

        locations_container = self.driver.find_element(By.CLASS_NAME, 'page-section-inner')

        # finding all locations links

        locations_links = locations_container.find_elements(By.TAG_NAME, 'h3')

        result = []

        for location in locations_links:
            result.append(location.text)

        logging.info('[ SPLACER ]: Locations parsing finished')
        return result

    def parse_card(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        # parsing data
        try:
            location_name = soup.find('div', class_='title').find('h1').text.translate(''.join(["'", '"']))
        except AttributeError:
            location_name = None
        try:
            host_name = soup.find('div', class_='owner-name').text.translate(''.join(["'", '"']))
        except AttributeError:
            host_name = None
        try:
            listing_location = soup.find('span', class_='splace-city').text.translate(''.join(["'", '"']))
        except:
            listing_location = None
        try:
            container = soup.find('div', class_='h-stars')
            reviews_count = container.find('div', class_='sp-pointer').text
            reviews_count = ''.join(c for c in str(reviews_count) if c.isdigit())
        except Exception as e:
            reviews_count = 0

        # there is no access to phone number on the page
        phone_number = None

        print(url)
        print(location_name)
        print(host_name)
        print(listing_location)
        print(reviews_count)
        print(phone_number)
        print('\n\n\n\n')

        try:
            self.db.add_listing('splacer', url, location_name, host_name, listing_location, phone_number, None,
                                int(reviews_count), datetime.datetime.now())
        except Exception as e:
            print('Add listing error')
            print(e)

    def get_pag_len(self):
        """
        Detecting pagination len
        :return: [int] len of page pagination
        """
        try:
            pagination = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.pagination')))

            pagination_elems = pagination.find_elements(By.TAG_NAME, 'li')

            pagination_len = pagination_elems[-2].text
            return int(pagination_len)

        except TimeoutException:
            logging.info('[ SPLACER ]: Page has no pagination')
            return 1

    def proceed_page(self, url):
        self.driver.get(url)

        time.sleep(5)

        body = self.driver.find_element(By.TAG_NAME, 'html')
        action = action_chains.ActionChains(self.driver)
        action.move_to_element_with_offset(body, 5, 5)
        action.click()
        action.perform()

        try:
            cards = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'sp-splace')))

        except TimeoutException:
            logging.info('[ SPLACER ]: Filed to find cards on page, ' + str(url) + ' skipping..')
            cards = []

        for card in cards:
            link = card.find_element(By.CLASS_NAME, 'sp-title').get_attribute('href')
            if not self.db.check_pkey('splacer', link):
                print('Parsing card')
                self.parse_card(link)
            else:
                print('Skipping card')
                print(card.text)
                print('\n\n\n\n')

    def proceed_url(self, url):
        self.driver.get(url)
        pagination_len = self.get_pag_len()

        for pagination_page in range(1, pagination_len + 1):
            pagination_url = url + '&page=' + str(pagination_page)

            try:
                logging.info('[ SPLACER ]: Parsing pagination page: ' + str(pagination_url))
                self.proceed_page(pagination_url)
            except Exception as e:
                logging.info('[ SPLACER ]: Filed to proceed page, ' + str(pagination_url) + ' skipping..')
                print(e)

    def start(self):
        """
        Generates get requests to parse items with
        Example of the url:
        https://www.splacer.co/splaces/search?activity_category=Corporate%20Event&city=New%20York&activity=Business%20Brunch&sort_by=popularity
        """
        # parsing url parts
        activities = self.parse_activities()
        locations = self.parse_locations()

        # generating all possible urls to parse
        for location in locations:
            for key in activities:
                for activity in activities[key]:
                    print(location + " : " + key + " : " + activity)
                    url = 'https://www.splacer.co/splaces/search?activity_category=' + str(key) + '&city=' + str(
                        location) + '&activity=' + str(activity) + '&sort_by=popularity'
                    print(url)

                    try:
                        self.proceed_url(url)
                    except Exception as e:
                        logging.info('[ SPLACER ]: Filed to proceed url, ' + str(url) + ' skipping..')
                        print(e)
