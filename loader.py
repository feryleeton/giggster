import coloredlogs
import logging

from utils.db_api.postgres import Database
from slack_bot.bot import Bot

coloredlogs.install()
logging.basicConfig(level=logging.INFO)

db = Database()
bot = Bot()
