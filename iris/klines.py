import requests
import numpy as np
import logger

class Klines:
    def __init__(self, global_config, currency_config, db):
        self.log = logger.get("klines")
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db

    def run(self):
        entries = 0
        for key in self.global_config["binance"]["intervals"].keys():
            interval = self.global_config["binance"]["intervals"][key]
            payload = {
                "symbol": self.currency_config["symbol"],
                "interval": interval
            }
            r = requests.get(self.global_config["binance"]["url"] + "api/v1/klines", payload)
            data = np.array(r.json())
            data = np.delete(data, 4, 1)
            data = np.delete(data, 10, 1)

        self.log.info(str(entries) + " klines saved")
