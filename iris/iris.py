#!/usr/bin/env python

import yaml
import sys
import time
from klines import Klines
# from mail import Email
# from twitter import Twitter
from db import DB

class Ceres:
    global_config_file = "global"
    config_dir = "../config/"
    config_file_extention = ".yaml"

    def __init__(self, currency_code):
        self.currency_config = None
        self.global_config = None
        try:
            with open(self.config_dir + self.global_config_file + self.config_file_extention) as fp:
                self.global_config = yaml.load(fp)

            with open(self.config_dir + currency_code + self.config_file_extention) as fp:
                self.currency_config = yaml.load(fp)
        except IOError:
            print("Error loading configuration files.")
            return

        self.db = DB(self.global_config, self.currency_config)
        # self.twitter = Twitter(self.global_config, self.currency_config, self.db)
        self.klines = Klines(self.global_config, self.currency_config, self.db)
        # self.email = Email(self.global_config, self.currency_config, self.db)

    def tick(self):
        # self.twitter.run()
        self.klines.run()
        # self.email.run()
    def stop(self):
        pass

if __name__ == "__main__":
    ceres = Ceres(sys.argv[1])
    starttime=time.time()
    try:
        while True:
            ceres.tick()
            time.sleep(60.0 - ((time.time() - starttime) % 60.0))
    except KeyboardInterrupt:
        ceres.stop()