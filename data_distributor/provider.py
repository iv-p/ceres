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

    def prediction_data(self, code):
        since_timestamp = 0
        slopes = []
        lin_regression_x = np.arange(self.global_config["neural_network"]["input"])
        for currency in self.currency_config.keys():
            klines_data = list(self.db.get(currency, "klines").find().sort("timestamp", pymongo.ASCENDING).limit(1440))
            klines_data = [mapper(x) for x in klines_data]
            slope = stats.linregress(lin_regression_x, klines_data)
            slopes.append(slope)

        global_trend = np.average(slopes)
        klines_data = list(self.db.get(code, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(self.global_config["neural_network"]["input"]))
        count = len(klines_data)
        klines_data = [mapper(x) for x in klines_data]
        return np.append(klines_data, global_trend)

    def get_price(self, code):
        klines_data = list(self.db.get(code, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(1))
        return klines_data[0]

    def get_average_price(self, code):
        klines_data = list(self.db.get(code, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(1))
        return mapper(klines_data[0])
    def get_klines(self, code):
        klines_data = list(self.db.get(code, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(500))
        return np.array(klines_data)