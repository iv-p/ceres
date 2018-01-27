import requests
import numpy as np
import pymongo

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
        for currency_code in self.currency_config.keys():
            entries = 0
            latest_kline = self.db.get(currency_code, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(1)
            payload = {
                "symbol": self.currency_config[currency_code]["symbol"],
                "interval": self.global_config["binance"]["interval"]
            }

            if latest_kline.count() > 0:
                payload["startTime"] = int(latest_kline[0]["timestamp"]) + 1

            r = requests.get(self.global_config["binance"]["url"] + "api/v1/klines", payload)
            data = [mapper(x) for x in r.json()]
            if len(data) > 0:
                self.db.get(currency_code, "klines").insert_many(data)
                entries += len(data)

            print(currency_code + " : " + str(entries) + " klines saved")
