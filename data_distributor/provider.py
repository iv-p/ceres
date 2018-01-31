from flask import Flask
import pymongo
import numpy as np

def mapper(t):
    return float(t["high"]) + float(t["low"]) / 2

class Provider:
    def __init__(self, global_config, db):
        self.db = db
        self.global_config = global_config

    def prediction_data(self, code):
        since_timestamp = 0
        klines_data = list(self.db.get(code, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(self.global_config["neural_network"]["input"]))
        count = len(klines_data)
        klines_data = [mapper(x) for x in klines_data]
        return np.array(klines_data)

    def get_price(self, code):
        klines_data = list(self.db.get(code, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(1))
        return klines_data[0]

    def get_klines(self, code):
        klines_data = list(self.db.get(code, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(500))
        return np.array(klines_data)