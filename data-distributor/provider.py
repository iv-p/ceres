import numpy as np
from flask import Flask
from flask import jsonify
import pymongo
import json

def mapper(t):
    return float(t["high"]) + float(t["low"]) / 2

class Provider:
    def __init__(self, global_config, db, app):
        self.db = db
        @app.route("/<code>/prediction_data")
        def prediction_data(code):
            return self.prediction_data(code)

        @app.route("/<code>/price")
        def price(code):
            return self.get_price(code)

        @app.route("/<code>/klines")
        def klines(code):
            return self.get_klines(code)

    def prediction_data(self, code):
        since_timestamp = 0
        klines_data = list(self.db.get(code, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(5))
        count = len(klines_data)
        klines_data = [mapper(x) for x in klines_data]
        return json.dumps(klines_data)

    def get_price(self, code):
        klines_data = list(self.db.get(code, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(1))
        return str(mapper(klines_data[0]))

    def get_klines(self, code):
        klines_data = list(self.db.get(code, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(500))
        return json.dumps(klines_data)