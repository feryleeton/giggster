import psycopg2
from psycopg2._psycopg import DatabaseError

import logging


class Database:
    def __init__(self):
        # connecting to existing database
        self.connection = psycopg2.connect(user="postgres",
                                           password="toor",
                                           host="127.0.0.1",
                                           port="5432",
                                           database="postgres")
        self.cursor = self.connection.cursor()

        self.create_tables()

    def create_tables(self):
        self.cursor = self.connection.cursor()

        # peerspace table creation
        sql = """
                        CREATE TABLE IF NOT EXISTS peerspace (
                        listing_url VARCHAR(255) NOT NULL,
                        location_name VARCHAR(255),
                        host_name VARCHAR(255),
                        address VARCHAR(255),
                        phone_number VARCHAR(255),
                        web_site VARCHAR(255),
                        review_count INT,
                        date_created TIMESTAMP,
                        PRIMARY KEY (listing_url)
                        )
                        """

        self.cursor.execute(sql)
        self.connection.commit()

        logging.info('[ DATABASE ]: Table for peerspace.com was created successfully')

        # splacer table creation
        sql = """
                        CREATE TABLE IF NOT EXISTS splacer (
                        listing_url VARCHAR(255) NOT NULL,
                        location_name VARCHAR(255),
                        host_name VARCHAR(255),
                        address VARCHAR(255),
                        phone_number VARCHAR(255),
                        web_site VARCHAR(255),
                        review_count INT,
                        date_created TIMESTAMP,
                        PRIMARY KEY (listing_url)
                        )
                        """
        self.cursor.execute(sql)
        self.connection.commit()
        logging.info('[ DATABASE ]: Table for slpacer.com was created successfully')

        # reelscout table creation
        sql = """
                                CREATE TABLE IF NOT EXISTS reelscout (
                                listing_url VARCHAR(255) NOT NULL,
                                location_name VARCHAR(255),
                                host_name VARCHAR(255),
                                address VARCHAR(255),
                                phone_number VARCHAR(255),
                                web_site VARCHAR(255),
                                review_count INT,
                                date_created TIMESTAMP,
                                PRIMARY KEY (listing_url)
                                )
                                """
        self.cursor.execute(sql)
        self.connection.commit()

        logging.info('[ DATABASE ]: Table for reel-scout.com was created successfully')

        # eventective table creation
        sql = """
                                        CREATE TABLE IF NOT EXISTS eventective (
                                        listing_url VARCHAR(255) NOT NULL,
                                        location_name VARCHAR(255),
                                        host_name VARCHAR(255),
                                        address VARCHAR(255),
                                        phone_number VARCHAR(255),
                                        web_site VARCHAR(255),
                                        review_count INT,
                                        date_created TIMESTAMP,
                                        PRIMARY KEY (listing_url)
                                        )
                                        """
        self.cursor.execute(sql)
        self.connection.commit()

        logging.info('[ DATABASE ]: Table for eventective.com was created successfully')

        # tripleseat table creation
        sql = """
                                                CREATE TABLE IF NOT EXISTS tripleseat (
                                                listing_url VARCHAR(255) NOT NULL,
                                                location_name VARCHAR(255),
                                                host_name VARCHAR(255),
                                                address VARCHAR(255),
                                                phone_number VARCHAR(255),
                                                web_site VARCHAR(255),
                                                review_count INT,
                                                date_created TIMESTAMP,
                                                PRIMARY KEY (listing_url)
                                                )
                                                """
        self.cursor.execute(sql)
        self.connection.commit()

        logging.info('[ DATABASE ]: Table for tripleseat.com was created successfully')

        # venuefinder table creation
        sql = """
                                                        CREATE TABLE IF NOT EXISTS venuefinder (
                                                        listing_url VARCHAR(255) NOT NULL,
                                                        location_name VARCHAR(255),
                                                        host_name VARCHAR(255),
                                                        address VARCHAR(255),
                                                        phone_number VARCHAR(255),
                                                        web_site VARCHAR(255),
                                                        review_count INT,
                                                        date_created TIMESTAMP,
                                                        PRIMARY KEY (listing_url)
                                                        )
                                                        """
        self.cursor.execute(sql)
        self.connection.commit()

        logging.info('[ DATABASE ]: Table for venuefinder.com was created successfully')

        # weddingspot table creation
        sql = """
                                                                CREATE TABLE IF NOT EXISTS weddingspot (
                                                                listing_url VARCHAR(255) NOT NULL,
                                                                location_name VARCHAR(255),
                                                                host_name VARCHAR(255),
                                                                address VARCHAR(255),
                                                                phone_number VARCHAR(255),
                                                                web_site VARCHAR(255),
                                                                review_count INT,
                                                                date_created TIMESTAMP,
                                                                PRIMARY KEY (listing_url)
                                                                )
                                                                """
        self.cursor.execute(sql)
        self.connection.commit()

        logging.info('[ DATABASE ]: Table for weddingspot.com was created successfully')

        # yogafinder table creation
        sql = """
                                CREATE TABLE IF NOT EXISTS yogafinder (
                                listing_url VARCHAR(255) NOT NULL,
                                location_name VARCHAR(255),
                                host_name VARCHAR(255),
                                address VARCHAR(255),
                                phone_number VARCHAR(255),
                                web_site VARCHAR(255),
                                review_count INT,
                                date_created TIMESTAMP,
                                PRIMARY KEY (listing_url)
                                )
                                """
        self.cursor.execute(sql)
        self.connection.commit()
        logging.info('[ DATABASE ]: Table for yogafinder.com was created successfully')

        # breawer table creation

        sql = """
                                CREATE TABLE IF NOT EXISTS breawer (
                                listing_url VARCHAR(255) NOT NULL,
                                location_name VARCHAR(255),
                                host_name VARCHAR(255),
                                address VARCHAR(255),
                                phone_number VARCHAR(255),
                                web_site VARCHAR(255),
                                review_count INT,
                                date_created TIMESTAMP,
                                PRIMARY KEY (listing_url)
                                )
                                """
        self.cursor.execute(sql)
        self.connection.commit()
        logging.info('[ DATABASE ]: Table for brewersassociation.org was created successfully')

        # vendry table creation

        sql = """
                                        CREATE TABLE IF NOT EXISTS vendry (
                                        listing_url VARCHAR(255) NOT NULL,
                                        location_name VARCHAR(255),
                                        host_name VARCHAR(255),
                                        address VARCHAR(255),
                                        phone_number VARCHAR(255),
                                        web_site VARCHAR(255),
                                        review_count INT,
                                        date_created TIMESTAMP,
                                        PRIMARY KEY (listing_url)
                                        )
                                        """
        self.cursor.execute(sql)
        self.connection.commit()
        logging.info('[ DATABASE ]: Table for vendry.com was created successfully')

        # weddingwire table creation
        sql = """
                                                                        CREATE TABLE IF NOT EXISTS weddingwire (
                                                                        listing_url VARCHAR(255) NOT NULL,
                                                                        location_name VARCHAR(255),
                                                                        host_name VARCHAR(255),
                                                                        address VARCHAR(255),
                                                                        phone_number VARCHAR(255),
                                                                        web_site VARCHAR(255),
                                                                        review_count INT,
                                                                        date_created TIMESTAMP,
                                                                        PRIMARY KEY (listing_url)
                                                                        )
                                                                        """
        self.cursor.execute(sql)
        self.connection.commit()

        logging.info('[ DATABASE ]: Table for weddingwire.com was created successfully')

        self.cursor.close()

    def check_pkey(self, table, key):
        self.cursor = self.connection.cursor()
        sql = "SELECT EXISTS(SELECT 1 FROM " + str(table) + " WHERE listing_url='" + str(key) + "') LIMIT 1"
        self.cursor.execute(sql, str(key))
        if self.cursor.fetchone()[0] == 0:
            self.cursor.close()
            return False
        else:
            self.cursor.close()
            return True

    def add_listing(self, table_name, listing_url, location_name, host_name, address, phone_number, web_site,
                    review_count, date_created):
        try:
            sql = "INSERT INTO " + str(
                table_name) + " (listing_url, location_name, host_name, address, phone_number, web_site, review_count, date_created) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"

            self.cursor = self.connection.cursor()
            self.cursor.execute(sql, (
                listing_url, location_name, host_name, address, phone_number, web_site, review_count, date_created))
            self.connection.commit()
            self.cursor.close()
        except DatabaseError as e:
            print('rollback')
            print(e)

            self.cursor = self.connection.cursor()
            self.cursor.execute("ROLLBACK")
            self.connection.commit()
            self.cursor.close()
