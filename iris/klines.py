import requests
import numpy as np
import logger

def mapper(t):
    return {
                "timestamp": t[0],
                "open": t[1],
                "high": t[2],
                "low": t[3],
                "close": t[4]
            }

class Klines:
    def __init__(self, global_config, currency_config, db):
        self.log = logger.get("klines")
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db

    def run(self):
        klines = self.db.get().klines
        entries = 0
        for key in self.global_config["binance"]["intervals"].keys():
            interval = self.global_config["binance"]["intervals"][key]
            payload = {
                "symbol": self.currency_config["symbol"],
                "interval": interval
            }
            r = requests.get(self.global_config["binance"]["url"] + "api/v1/klines", payload)

            data = [mapper(x) for x in r.json()]
            # print np.array(r.json()).shape
            # data = json_mapper(r.json())
            klines.insert_many(data)

        self.log.info(str(len(data)) + " klines saved")
