import datetime
import time

import coloredlogs
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from selenium.webdriver.common.proxy import *

from loader import bot, db

from brewer_scraper.breawer import Breawer
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
        # s = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        # driver = webdriver.Chrome(service=s, options=options)

        PARSING_STARTED = datetime.datetime.now()
        breawer = Breawer(driver=driver, db=db)
        bot.send_message("Breawer scraper started at: " + str(PARSING_STARTED))
        breawer.start()
        PARSING_FINISHED = datetime.datetime.now()

        reporter = Reporter(db, PARSING_STARTED, PARSING_FINISHED)
        reporter.parse_table('breawer')
        driver.quit()
    except Exception as e:
        bot.send_message(
            f"[ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ] Breawer parser filed with error: \n"
            f"{e}")
        print(e)
        try:
            driver.quit()
        except:
            pass
