import requests
import numpy as np

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

            data = [mapper(x) for x in r.json()]
            self.db.get("klines").insert_many(data)

        print(str(len(data)) + " klines saved")
