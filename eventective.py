import datetime
import time

import coloredlogs
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from selenium.webdriver.common.proxy import *
from selenium.webdriver.chrome.service import Service

from loader import bot, db

from eventective_scraper.scraper import Eventective
from utils.notifications.reporter import Reporter

if __name__ == '__main__':
    try:
        # driver options
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--proxy-server=p.webshare.io:10000")
        options.headless = True

        driver = webdriver.Remote('http://localhost:4444/wd/hub', options=options)

        PARSING_STARTED = datetime.datetime.now()
        evenective = Eventective(db)
        bot.send_message("Eventective scraper started at: " + str(PARSING_STARTED))
        evenective.start()
        PARSING_FINISHED = datetime.datetime.now()

        print('PARSING FINISHED !!!')

        reporter = Reporter(db, PARSING_STARTED, PARSING_FINISHED)
        reporter.parse_table('eventective')
        driver.quit()
    except AttributeError:
        bot.send_message(
            f"[ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ] Eventective parser filed with error: \n"
            f"{e}")
        try:
            driver.quit()
        except:
            pass