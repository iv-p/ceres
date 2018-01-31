import requests
import numpy as np
import pymongo
import time
import threading
import time

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

        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def tick(self):
        for currency in self.currency_config.keys():
            entries = 0
            latest_kline = self.db.get(currency, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(1)
            self.db.get(currency, "klines").create_index(
                [("timestamp", pymongo.DESCENDING)],
                unique=True)
            payload = {
                "symbol": self.currency_config[currency]["symbol"],
                "interval": self.global_config["binance"]["interval"]
            }

            if latest_kline.count() > 0:
                payload["startTime"] = int(latest_kline[0]["timestamp"]) + 1

            r = requests.get(self.global_config["binance"]["url"] + "api/v1/klines", payload)
            data = [mapper(x) for x in r.json()]
            if len(data) > 0:
                self.db.get(currency, "klines").insert_many(data)
                entries += len(data)
            print("saved " + str(entries) + " klines for " + currency)

    def run(self):
        starttime=time.time()
        interval = self.global_config["data-fetcher"]["klines"]
        while True:
            # try:
            self.tick()
            time.sleep(interval - ((time.time() - starttime) % interval))
            # except Exception:
            #     pass

    def healthcheck(self):
        return self.thread.is_alive()