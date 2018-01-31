import datetime

class Stock:
    def __init__(self, symbol, quantity, price):
        self.data = {
            "symbol": symbol,
            "quantity": quantity,
            "buy": {
                "price": price,
                "timestamp": int(datetime.datetime.now().timestamp())
            },
            "sell": None
        }

    def sell(self, price):
        self.data["sell"] = {
            "price": price,
            "timestamp":int(datetime.datetime.now().timestamp())
        }

    def get_profit(self, price):
        if self.data["sell"] != None:
            return (self.data["sell"]["price"] - self.data["buy"]["price"]) * self.data["quantity"]
        else:
            return self.data["quantity"] * price