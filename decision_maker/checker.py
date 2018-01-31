import pymongo
import numpy as np
import requests
import time
import threading

def mapper(x):
    return np.average(x["predictions"])

class Checker:
    def __init__(self, global_config, currency_config, db):
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db
        self.buy_threshold = self.global_config["decision-maker"]["thresholds"]["buy"]
        self.sell_threshold = self.global_config["decision-maker"]["thresholds"]["sell"]

        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def tick(self):
        for currency in self.currency_config.keys():
            data = self.db.get(currency, "predictions").find().sort("timestamp", pymongo.DESCENDING).limit(15)
            data = [mapper(x) for x in data]
            if len(data) > 0:
                predicted = np.average(data)
                predicted_display = round(100*(predicted - 1))

                verb = None
                response = None
                if predicted > self.buy_threshold:
                    print("buy")
                    response = requests.get(self.global_config["url"]["stock-manager"] + "/buy/" + currency)
                    verb = "buy"
                elif predicted < self.sell_threshold:
                    print("sell")
                    response = requests.get(self.global_config["url"]["stock-manager"] + "/sell/" + currency)
                    verb = "sell"

                if verb != None:
                    event = {
                        "timestamp": str(int(time.time())),
                        "status": response.text,
                        "currency": currency,
                        "event": verb
                    }
                    self.log(event)

    def run(self):
        starttime=time.time()
        interval = self.global_config["decision-maker"]["interval"]
        while True:
            try:
                self.tick()
                time.sleep(interval - ((time.time() - starttime) % interval))
            except Exception:
                pass
    
    def healthcheck(self):
        return self.thread.is_alive()

    def log(self, event):
        self.db.get("manager", "events").insert_one(event)

    def get_events(self):
        return list(self.db.get("manager", "events").find().sort("timestamp", pymongo.DESCENDING).limit(500))

    def set_buy(self, value):
        self.buy_threshold = value

    def set_sell(self, value):
        self.sell_threshold = value