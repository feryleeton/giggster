"""
Here is the Reporter class, that forms reports (.csv files) after parsing finished.
Works with postgres database to find new parsed listings
"""
import datetime
import csv
from slack_bot.bot import Bot
import logging

bot = Bot()


class Reporter:
    def __init__(self, db, parsing_started, parsing_finished):
        self.db = db
        self.PARSING_STARTED = parsing_started
        self.PARSING_FINISHED = parsing_finished

    def form_csv_report(self, table_name, new_listings, diff):

        with open('/home/automatic_scraping_engine/reports/' + str(table_name) + '.csv', mode='w+', newline='') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            if table_name == 'breawer' or table_name == 'yogafinder':
                writer.writerow(
                    ['Location Name', 'Host Name', 'Address', 'Phone Number', 'Web Site', 'Review Count'])

                for listing in new_listings:
                    try:
                        listing = list(listing)
                        writer.writerow(listing[1:-1])
                    except Exception as e:
                        print(e)
            else:
                writer.writerow(
                    ['Link', 'Location Name', 'Host Name', 'Address', 'Phone Number', 'Web Site', 'Review Count'])

                for listing in new_listings:
                    try:
                        listing = list(listing)
                        writer.writerow(listing[:-1])
                    except Exception as e:
                        print(e)

            logging.info('[ LOGGER ]: created .csv report file for ' + str(table_name))

        try:
            bot.send_report(str(table_name), diff)
            logging.info('[ LOGGER ]: sent parsing report file for ' + str(table_name))
        except Exception as e:
            # if file empty rise exception
            logging.error('[ LOGGER ]: cant send parsing report file for ' + str(table_name))
            print(e)
            pass

    def parse_tables(self):
        tables_list = self.get_tables()

        for table in tables_list:
            new_listings = self.parse_table(table)
            self.form_csv_report(table, new_listings)
            logging.info('[ LOGGER ]: available tables parsed')

    def parse_table(self, table):
        sql = "SELECT * FROM " + str(table)
        self.db.cursor = self.db.connection.cursor()
        self.db.cursor.execute(sql)
        all_listings = self.db.cursor.fetchall()
        self.db.cursor.close()

        new_listings = []

        diff = False

        # check for new listings
        for listing in all_listings:
            if self.PARSING_STARTED - datetime.timedelta(days=9) < listing[-1] < self.PARSING_FINISHED:
                new_listings.append(listing)

        if len(new_listings) < len(all_listings):
            diff = True
        # remove if using parse_tables()
        self.form_csv_report(table, new_listings, diff)
        return new_listings

    def get_tables(self):
        """
        Returns a list of available databases to form report with
        """
        s = ""
        s += "SELECT"
        s += " table_schema"
        s += ", table_name"
        s += " FROM information_schema.tables"
        s += " WHERE"
        s += " ("
        s += " table_schema = 'public'"
        s += " )"
        s += " ORDER BY table_schema, table_name;"

        self.db.cursor = self.db.connection.cursor()
        self.db.cursor.execute(s)
        tables_list = [db_fetch[-1] for db_fetch in self.db.cursor.fetchall()]
        self.db.cursor.close()

        return tables_list
