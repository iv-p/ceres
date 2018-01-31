from stocks import Stocks
from events import Events

class WebApi:
    def __init__(self, global_config, currency_config, app, db):
        self.stocks = Stocks(global_config, currency_config, db, app)
        self.events = Events(global_config, currency_config, db, app)
