from api.stocks import Stocks
from api.events import Events
from api.predictions import Predictions
from api.price import Price
from flask import Flask
from flask_cors import CORS, cross_origin

class WebApi:
    def __init__(self, global_config, currency_config, db, data_distributor, stock_manager):
        app = Flask(__name__)
        CORS(app)
        self.stocks = Stocks(global_config, currency_config, db, app, data_distributor, stock_manager)
        self.events = Events(global_config, currency_config, db, app)
        self.predictions = Predictions(global_config, currency_config, db, app)
        self.price = Price(global_config, currency_config, db, app)
        app.run(host="0.0.0.0", port=1337)
