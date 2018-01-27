import yaml
import sys
import time
from manager import Manager
from db import DB

class StockManager:
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

        self.db = DB(self.global_config)
        self.manager = Manager(self.global_config, self.currency_config, self.db)

    def run(self):
        starttime=time.time()
        interval = self.global_config["stock-manager"]["interval"]
        try:
            while True:
                self.tick()
                time.sleep(interval - ((time.time() - starttime) % interval))
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    stock_manager = StockManager()
    stock_manager.run()