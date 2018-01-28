import yaml
import sys
import time
from healthcheck import Healthcheck
from flask import Flask


class Manager:
    global_config_file = "global.yaml"
    currency_config_file = "currencies.yaml"
    config_dir = "/config/"
    config_file_extention = ".yaml"

    def __init__(self):
        self.currency_config = None
        self.global_config = None
        try:
            with open(self.config_dir + self.global_config_file) as fp:
                self.global_config = yaml.load(fp)

            with open(self.config_dir + self.currency_config_file) as fp:
                self.currency_config = yaml.load(fp)
        except IOError:
            print("Error loading configuration files.")
            return

        app = Flask(__name__)
        self.healthcheck = Healthcheck(app, self.global_config)
        app.run("0.0.0.0")

if __name__ == "__main__":
    manager = Manager()
    manager.run()