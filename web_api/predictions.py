import json
import pymongo

class Predictions:
    def __init__(self, global_config, currency_config, db, app):
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db

        app.add_url_rule("/predictions/currency/<currency>", "price_predictions", self.get_price_predictions)

    def get_price_predictions(self, currency):
        predictions = list(self.db.get(currency, "predictions").find().limit(500))
        for prediction in predictions:
            del prediction["_id"]
        return json.dumps(predictions)