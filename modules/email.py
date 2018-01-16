from lxml import html
import requests
import yaml
import sys
import poplib
import string, random
import StringIO, rfc822
from textblob import TextBlob
import logger
import sqlite3
import time


class Email:
    def __init__(self, global_config, currency_config, sql_helper):
        self.log = logger.get("klines")
        self.global_config = global_config
        self.currency_config = currency_config
        self.sql_helper = sql_helper

        self.email_connection = poplib.POP3_SSL(self.global_config["email"]["server"])
        self.email_connection.user(self.currency_config["email"]["username"] + "@" + self.global_config["email"]["domain"])
        self.email_connection.pass_(self.currency_config["email"]["password"])

    def run(self):
        connection = self.sql_helper.get()
        c = connection.cursor()
        resp, items, octets = self.email_connection.list()
        
        for i in range(len(items)):
            id, size = string.split(items[i])
            resp, text, octets = self.email_connection.retr(id)
            text = string.join(text, "\n")
            blob = TextBlob(text)
            file = StringIO.StringIO(text)
            message = rfc822.Message(file)
            date = message.getdate("Date")
            date[5] = 0
            timestamps = {
                "minute": time.mktime(date)
            }
            date[]
            print time.mktime(date)

        c.close()
        connection.commit()