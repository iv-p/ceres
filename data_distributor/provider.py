from flask import Flask
import pymongo
import numpy as np
from scipy import stats

def mapper(t):
    return float(t["high"]) + float(t["low"]) / 2

class Provider:
    def __init__(self, global_config, currency_config, db):
        self.db = db
        self.global_config = global_config
        self.currency_config = currency_config

    def prediction_data(self, currency):
        network_input = self.global_config["neural_network"]["input"]
        result = np.empty((1, 50, network_input))
        klines_data = list(self.db.get(currency, "klines").find().sort("timestamp", pymongo.ASCENDING).limit(network_input + 49))
        klines_data = [mapper(x) for x in klines_data]

        batch = np.empty((50, network_input))

        for i in range(0, 50):
            input = klines_data[i:i + network_input]
            input = input / np.max(input)
            batch[i] = input

        print(batch)
        return batch

    def get_price(self, code):
        klines_data = list(self.db.get(code, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(1))
        return klines_data[0]

    def get_average_price(self, code):
        klines_data = list(self.db.get(code, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(1))
        return mapper(klines_data[0])
    def get_klines(self, code):
        klines_data = list(self.db.get(code, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(500))
        return np.array(klines_data)