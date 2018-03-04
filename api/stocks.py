import json
import pymongo

class Stocks:
    def __init__(self, global_config, currency_config, db, app, data_distributor, stock_manager):
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db
        self.data_distributor = data_distributor
        self.stock_manager = stock_manager

        app.add_url_rule("/worth", "worth", self.get_worth)
        app.add_url_rule("/stocks/active", "stocks", self.get_stocks_active)
        app.add_url_rule("/stocks/history", "stocks_history", self.get_stocks_history)

    def get_worth(self):
        return str(self.stock_manager.manager.get_worth())

    def get_stocks_active(self):
        stocks = self.db.get("manager", "stocks").find({"sell": None})
        stocks_list = []
        for stock in stocks:
            del stock["_id"]
            stocks_list.append(stock)
        return json.dumps(stocks_list)

    def get_stocks_history(self):
        stocks = self.db.get("manager", "stocks").find()
        stocks_list = []
        for stock in stocks:
            del stock["_id"]
            stocks_list.append(stock)
        return json.dumps(stocks_list)
