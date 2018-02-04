from web_api.stocks import Stocks
from web_api.events import Events
from web_api.predictions import Predictions
from flask import Flask
from flask_cors import CORS, cross_origin

class WebApi:
    def __init__(self, global_config, currency_config, db):
        app = Flask(__name__)
        CORS(app)
        self.stocks = Stocks(global_config, currency_config, db, app)
        self.events = Events(global_config, currency_config, db, app)
        self.predictions = Predictions(global_config, currency_config, db, app)
        app.run(host="0.0.0.0", port=1337)
