import pymongo
import numpy as np
import requests

def mapper(x):
    return np.average(x["predictions"])

class Checker:
    def __init__(self, global_config, currency_config, db):
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db

    def check(self):
        for currency_code in self.currency_config.keys():
            data = self.db.get(currency_code, "predictions").find().sort("timestamp", pymongo.DESCENDING).limit(15)
            data = [mapper(x) for x in data]
            if len(data) > 0:
                predicted = np.average(data)
                predicted_display = round(100*(predicted - 1))
                print(currency_code + " : " + str(predicted_display) + "%")

                if predicted > 1.1:
                    requests.get(self.global_config["url"]["stock-manager"] + "/buy/" + currency_code)
                elif predicted < 0.98:
                    requests.get(self.global_config["url"]["stock-manager"] + "/sell/" + currency_code)