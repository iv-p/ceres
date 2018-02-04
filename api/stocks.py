import json
import pymongo

class Stocks:
    def __init__(self, global_config, currency_config, db, app):
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db

        app.add_url_rule("/worth", "worth", self.get_worth)
        app.add_url_rule("/stocks/active", "stocks", self.get_stocks_active)
        app.add_url_rule("/stocks/history", "stocks_history", self.get_stocks_history)


    def get_worth(self):
        stocks = self.db.get("manager", "stocks").find({"sell": None})
        worth = 0
        for stock in stocks:
            r = requests.get(self.global_config["url"]["data-distributor"] + "/" + stock["symbol"] + "/price")
            price = float(r.text)
            worth += price * stock["quantity"]
        return str(worth)

    def get_stocks_active(self):
        stocks = self.db.get("manager", "stocks").find({"sell": None})
        stocks_list = []
        for stock in stocks:
            s = {
                "symbol": stock["symbol"],
                "quantity": stock["quantity"],
                "buy_price": stock["buy"]["price"]
            }
            stocks_list.append(s)
        return json.dumps(stocks_list)

    def get_stocks_history(self):
        stocks = self.db.get("manager", "stocks").find()
        stocks_list = []
        for stock in stocks:
            s = {
                "symbol": stock["symbol"],
                "quantity": stock["quantity"],
                "buy_price": stock["buy"]["price"]
            }
            stocks_list.append(s)
        return json.dumps(stocks_list)
