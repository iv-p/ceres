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
        result = np.empty((10, 60))
        klines_data = list(self.db.get(currency, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(600))
        klines_data = [mapper(x) for x in klines_data]
        klines_data.reverse()

        for i in range(0, 10):
            input = klines_data[i * 60 : (i + 1) * 60]
            min_input = np.min(input)
            max_input = np.max(input) - min_input
            input -= min_input
            input /= max_input
            result[i] = input

        return result

    def get_price(self, code):
        klines_data = list(self.db.get(code, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(1))
        return klines_data[0]

    def get_average_price(self, code):
        klines_data = list(self.db.get(code, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(1))
        return mapper(klines_data[0])
    def get_klines(self, code):
        klines_data = list(self.db.get(code, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(500))
        return np.array(klines_data)