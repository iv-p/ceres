import sqlite3
import numpy as np
import logger
import tweepy
from textblob import TextBlob


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
        tweets = np.array([])
        for timeline in self.currency_config["twitter"]["timelines"]:
            user_tweets = tweepy.Cursor(
                    self.api.user_timeline, 
                    screen_name=timeline)
            tweets = np.append(tweets, list(user_tweets.items(10)))

        for hashtag in self.currency_config["twitter"]["hashtags"]:
            hashtag_tweets = tweepy.Cursor(
                    self.api.search,
                    q=hashtag)
            tweets = np.append(tweets, list(hashtag_tweets.items(10)))

        connection = self.sql_helper.get()
        c = connection.cursor()
        events = 0
        for tweet in tweets:
            blob = TextBlob(tweet.text.encode('unicode_escape'))
            print tweet.id
            values = (
                tweet.id, 
                tweet.created_at,
                blob.polarity, 
                blob.subjectivity,
                "twitter",
                "")
            try:
                c.execute("INSERT INTO event VALUES (?, ?, ?, ?, ?, ?)", values)
                events += 1
            except sqlite3.IntegrityError:
                continue

        c.close()
        connection.commit()
        connection.close()

        self.log.info(str(events) + " events saved")
