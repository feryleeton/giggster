import datetime
import coloredlogs
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from selenium.webdriver.chrome.service import Service

from loader import bot, db

from splacer_scraper.scraper import Splacer
from utils.notifications.reporter import Reporter

logging.basicConfig(level = logging.INFO, filename = 'splacer.log')

if __name__ == '__main__':
    try:
        # driver
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--proxy-server=p.webshare.io:10000")
        options.add_argument("--window-size=1920,1080")
        options.headless = True

        # s = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM, version="99.0.4844.51").install())

        # driver = webdriver.Chrome(service=s, options=options)
        
        driver = webdriver.Remote('http://localhost:4444/wd/hub', options=options)

        PARSING_STARTED = datetime.datetime.now()
        splacer = Splacer(driver, db)
        bot.send_message("Splacer scraper started at: " + str(PARSING_STARTED))
        splacer.start()
        PARSING_FINISHED = datetime.datetime.now()

        print('PARSING FINISHED !!!')

        reporter = Reporter(db, PARSING_STARTED, PARSING_FINISHED)
        reporter.parse_table('splacer')
        driver.quit()
    except Exception as e:
        bot.send_message(
            f"[ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ] Splacer parser filed with error: \n"
            f"{e}")
        print(e)
        try:
            driver.quit()
        except:
            pass