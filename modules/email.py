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
        self.log = logger.get("email")
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
        
        events = 0
        for i in range(len(items)):
            id, size = string.split(items[i])
            resp, text, octets = self.email_connection.retr(id)
            text = string.join(text, "\n")
            blob = TextBlob(text)
            file = StringIO.StringIO(text)
            message = rfc822.Message(file)
            timestamp = time.mktime(message.getdate("Date"))
            
            values = (
                id, 
                timestamp,
                blob.polarity,
                blob.subjectivity,
                "email",
                "")
            try:
                c.execute("INSERT INTO event VALUES (?, ?, ?, ?, ?, ?)", values)
                events += 1
            except sqlite3.IntegrityError:
                continue
        
        c.close()
        connection.commit()
        connection.close()

        self.log.info(str(events) + " events written")        