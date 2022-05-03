import logging
import time
import datetime

import requests
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


class Peerspace:
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

        logging.info('[ PEERSPACE ]: Activity parsing started')

        self.driver.get('https://www.peerspace.com/plan/activities')

        # finding the container div of available activities on the page

        activities_container = self.driver.find_element(By.CLASS_NAME, 'container-index')

        # finding all activities links

        activities_links = activities_container.find_elements(By.TAG_NAME, 'h3')

        # forming list from parsed activities links

        result = []

        for activities_link in activities_links:
            link = activities_link.text.lower().replace(' ', '-')
            # link = link.replace('https://www.peerspace.com/plan/', '')
            print(link)
            result.append(link)

        logging.info('[ PEERSPACE ]: Activity parsing finished')

        return result

    def parse_locations(self):
        """
        This method parses locations from target website: peerspace.com,
        to form a search query for each activity in future and group parsed items based on this in monthly report

        returns a list of parsed locations
        """
        # redirecting to locations page

        logging.info('[ PEERSPACE ]: Locations parsing started')

        self.driver.get('https://www.peerspace.com/venues/locations')

        # finding the container div of available locations on the page

        locations_container = self.driver.find_element(By.CLASS_NAME, 'container')

        # finding all activities links

        locations_links = locations_container.find_elements(By.TAG_NAME, 'a')

        # forming list from parsed activities links

        result = []

        for location_link in locations_links:
            link = str(location_link.get_attribute('href'))
            link = link.replace('https://www.peerspace.com/venues/', '')

            # deleting unneeded link part (gb) if exists
            if 'gb/' in link:
                link = link.replace('gb/', '')
            # deleting unneeded link part (ca) if exists
            elif 'ca/' in link:
                link = link.replace('ca/', '')

            result.append(link)

        logging.info('[ PEERSPACE ]: Activity parsing finished')

        return result

    def parse_page(self, links_list):
        """
        This method parses given page and updates rows in database,
        to form a report in future
        """

        for link in links_list:
            # removing sort_order argument to keep each listing url unique
            link, sep, order = link.partition('?sort_order=')

            if not self.db.check_pkey('peerspace', link):
                print('Parsing card')
                page = requests.get(link)
                soup = BeautifulSoup(page.text, 'html.parser')
                # parsing data
                try:
                    location_name = soup.find('h1', class_='listing-header').text.translate(''.join(["'", '"']))
                except:
                    location_name = ''
                try:
                    host_name = soup.find('div', class_='host-name').text.translate(''.join(["'", '"']))
                except AttributeError:
                    host_name = None
                try:
                    listing_location = soup.find('p', class_='ListingLocation').text.translate(''.join(["'", '"']))
                except:
                    listing_location = None
                try:
                    reviews_count = soup.find('a', id='reviews-link').text.replace('reviews', '')
                except AttributeError:
                    reviews_count = 0

                # there is no access to phone number on the page
                phone_number = None

                try:
                    self.db.add_listing('peerspace', link, location_name, host_name, listing_location, phone_number,
                                        None,
                                        int(reviews_count), datetime.datetime.now())
                except Exception as e:
                    pass

                print(link)
                print(location_name)
                print(host_name)
                print(listing_location)
                print(reviews_count)
                print(phone_number)
                print('\n\n')
            else:
                print('Skipping card: ' + str(link))

    def proceed_url(self, url):
        """
        This method checks page for pagination and navigates throw it,
        calling the parse_page() method for each pagination page, if exists
        """

        logging.info('[ PEERSPACE ]: Processing url: ' + url)

        self.driver.get(url)

        # checking if page has pagination buttons
        try:
            pagination_ul = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.pagination')))

            logging.warning('[ PEERSPACE ]: Pagination found')

            while True:

                time.sleep(3)

                links_list = []

                items_container = self.driver.find_element(By.CLASS_NAME, 'search-thumbnails')
                items = items_container.find_elements(By.CLASS_NAME, 'Listing-Thumbnail')

                for item in items:
                    links_list.append(item.find_element(By.TAG_NAME, 'a').get_attribute('href'))
                    # print(item.find_element(By.TAG_NAME, 'a').get_attribute('href'))

                self.parse_page(links_list)

                try:
                    pagination_elems = pagination_ul.find_elements(By.TAG_NAME, 'li')

                    for elem in pagination_elems:
                        if elem.text == '›':
                            elem.find_element(By.TAG_NAME, 'span').click()
                            logging.info('Processing next pagination page')

                except ElementClickInterceptedException:
                    logging.warning('[ PEERSPACE ]: Pagination parsing finished')
                    break

        except TimeoutException:
            logging.info('[ PEERSPACE ]: pagination not found')

            links_list = []

            items_container = self.driver.find_element(By.CLASS_NAME, 'search-thumbnails')
            items = items_container.find_elements(By.CLASS_NAME, 'Listing-Thumbnail')

            for item in items:
                links_list.append(item.find_element(By.TAG_NAME, 'a').get_attribute('href'))
                # print(item.find_element(By.TAG_NAME, 'a').get_attribute('href'))

            self.parse_page(links_list)

    def start(self):
        """
        This method forms a search query to parse from given pairs of locations and activities

        calls parse_page() method, that parses generated url
        """

        # getting parsed values
        locations = self.parse_locations()
        activities = self.parse_activities()

        base = 'https://www.peerspace.com/s/'

        for activity in activities:
            activity_url_arg = '?a=' + str(activity)
            logging.info('[ PEERSPACE ]: Parsing activity: ' + str(activity))

            for location in locations:
                 location_url_arg = '&location=' + str(location)
                 logging.info('[ PEERSPACE ]: Parsing location: ' + str(location))

                 try:
                     self.proceed_url(base + activity_url_arg + location_url_arg)
                 except Exception as e:
                     print(e)

        logging.info('[ PEERSPACE ]: Parsing pages finished')