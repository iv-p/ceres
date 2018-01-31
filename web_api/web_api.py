from web_api.stocks import Stocks
from web_api.events import Events
from flask import Flask

class WebApi:
    def __init__(self, global_config, currency_config, db):
        app = Flask(__name__)
        self.stocks = Stocks(global_config, currency_config, db, app)
        self.events = Events(global_config, currency_config, db, app)
        app.run("0.0.0.0")
