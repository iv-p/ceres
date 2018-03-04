import requests
import numpy as np
import pymongo
import time
import threading
import time
from scipy import stats

def mapper(t):
    return {
        "timestamp": t[0],
        "open": t[1],
        "high": t[2],
        "low": t[3],
        "close": t[4]
    }

def chart(t):
    return float(t["open"]) + float(t["close"]) / 2

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

class Klines:
    def __init__(self, global_config, currency_config, db, decision_maker):
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db
        self.decision_maker = decision_maker

        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def tick(self):
        entries = 0
        for currency in self.currency_config.keys():
            latest_kline = self.db.get(currency, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(1)
            self.db.get(currency, "klines").create_index(
                [("timestamp", pymongo.DESCENDING)],
                unique=True)
            payload = {
                "symbol": self.currency_config[currency]["symbol"],
                "interval": self.global_config["binance"]["interval"],
                "startTime": 1517443200
            }

            if latest_kline.count() > 0:
                payload["startTime"] = int(latest_kline[0]["timestamp"]) + 1

            r = requests.get(self.global_config["binance"]["url"] + "api/v1/klines", payload)
            data = [mapper(x) for x in r.json()]
            
            if len(data) > 0:
                self.decision_maker.checker.check(currency)
                self.db.get(currency, "klines").insert_many(data)
                entries += len(data)
        if entries > 0:
            print("saved " + str(entries) + " klines")

    def run(self):
        starttime=time.time()
        interval = self.global_config["data-fetcher"]["klines"]
        while True:
            self.tick()
            time.sleep(interval - ((time.time() - starttime) % interval))

    def healthcheck(self):
        return self.thread.is_alive()