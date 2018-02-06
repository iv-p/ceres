import json
import pymongo

def mapper(t):
    return {
        'price':float(t["high"]) + float(t["low"]) / 2
    }

class Price:
    def __init__(self, global_config, currency_config, db, app):
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db

        app.add_url_rule("/price/currency/<currency>", "prices", self.get_price)

    def get_price(self, currency):
        prices = list(self.db.get(currency, "klines").find())
        prices = [mapper(x) for x in prices]
        return json.dumps(prices)