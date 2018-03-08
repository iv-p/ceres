import pymongo
import numpy as np
import time
import threading

def mapper(x):
    return x["prediction"]

class Checker:
    def __init__(self, global_config, currency_config, db, stock_manager, price_predictor):
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db
        self.stock_manager = stock_manager
        self.price_predictor = price_predictor
        self.buy_threshold = self.global_config["decision-maker"]["thresholds"]["buy"]
        self.sell_threshold = self.global_config["decision-maker"]["thresholds"]["sell"]

    def check(self, currency):
        latest = self.price_predictor.network.predict(currency)
        print(latest)
        data = self.db.get(currency, "predictions").find().sort("timestamp", pymongo.DESCENDING).limit(3)
        if data.count() < 3:
            return
        data = [mapper(x) for x in data]
        data.append(latest)
        print(data)
        if len(data) > 3:
            verb = None
            response = None
            predicted = np.average(data)
            if predicted > self.buy_threshold:
                print("buy")
                response = self.stock_manager.manager.buy(currency)
                verb = "buy"
            elif predicted < self.sell_threshold:
                print("sell")
                response = self.stock_manager.manager.sell(currency)
                verb = "sell"

            if verb != None:
                event = {
                    "timestamp": str(int(time.time())),
                    "status": response,
                    "currency": currency,
                    "event": verb
                }
                self.log(event)

    def log(self, event):
        self.db.get("manager", "events").insert_one(event)

    def get_events(self):
        return list(self.db.get("manager", "events").find().sort("timestamp", pymongo.DESCENDING).limit(500))

    def set_buy(self, value):
        self.buy_threshold = value

    def set_sell(self, value):
        self.sell_threshold = value