import datetime
import coloredlogs
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

from loader import bot, db

from peerspace_scraper.scraper import Peerspace
from utils.notifications.reporter import Reporter

if __name__ == '__main__':
    # peerspace
    try:
        # driver
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument("--remote-debugging-port=9222")
        options.headless = True

        driver = webdriver.Remote('http://localhost:4444/wd/hub', options=options)

        PARSING_STARTED = datetime.datetime.now()
        peerspace = Peerspace(driver, db)
        bot.send_message("Peerspace scraper started at: " + str(PARSING_STARTED))
        peerspace.start()
        PARSING_FINISHED = datetime.datetime.now()

        reporter = Reporter(db, PARSING_STARTED, PARSING_FINISHED)
        reporter.parse_table('peerspace')
        driver.quit()
    except Exception as e:
        bot.send_message(
            f"[ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ] Peerspace parser filed with error: \n"
            f"{e}")
        print(e)
        try:
            driver.quit()
        except:
            pass