import sqlite3
import numpy as np
import logger
import tweepy

class Twitter:
    def __init__(self, global_config, currency_config, sql_helper):
        self.log = logger.get("twitter")
        self.global_config = global_config
        self.currency_config = currency_config
        self.sql_helper = sql_helper
        auth = tweepy.OAuthHandler(
            self.global_config["twitter"]["consumer_key"], 
            self.global_config["twitter"]["consumer_secret"])
        auth.set_access_token(
            self.global_config["twitter"]["access_token_key"], 
            self.global_config["twitter"]["access_token_secret"])

        self.api = tweepy.API(auth)

    def run(self):
        for tweet in tweepy.Cursor(
                self.api.user_timeline, 
                screen_name=self.currency_config["twitter"]["timelines"][0]
            ).items(10):
            print tweet.text

        for tweet in tweepy.Cursor(
                self.api.search,
                q=self.currency_config["twitter"]["hashtags"][0]
            ).items(10):
            print tweet.text

        connection = self.sql_helper.get()
        c = connection.cursor()
        events = 0
        
        c.close()
        connection.close()

        self.log.info(str(events) + " events saved")
