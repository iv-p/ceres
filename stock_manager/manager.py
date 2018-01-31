import pymongo
import numpy as np
from flask import Flask
import requests
import json
import math
import datetime

from stock_manager.stock import Stock

def mapper(x):
    return np.average(x["predictions"])

class Manager:
    eth_per_stock = 0.1
    def __init__(self, global_config, currency_config, db):
        self.stocks = []
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db
        self.wallet = 2.0

    def buy(self, currency):
        active_stocks = self.db.get("manager", "stocks").find({"sell": None})
        if active_stocks.count() >= 20:
            return "full"

        r = requests.get(self.global_config["url"]["data-distributor"] + "/" + currency + "/price")
        price = float(r.text)
        quantity = math.floor(self.eth_per_stock / price)

        if self.wallet < price * quantity:
            return "not enough funds"
        
        self.wallet -= price * quantity
        stock = self.buy_stock(currency, quantity, price)
        self.db.get("manager", "stocks").insert_one(stock)

        return "OK"

    def sell(self, currency):
        stocks = self.db.get("manager", "stocks").find({"sell": None})
        sold = 0
        for stock in stocks:
            if stock["symbol"] == currency:
                result = self.db.get("manager", "stocks").delete_one(stock)
                r = requests.get(self.global_config["url"]["data-distributor"] + "/" + currency + "/price")
                price = float(r.text)
                self.wallet += price * stock["quantity"]
                self.sell_stock(stock, price)
                self.db.get("manager", "stocks").insert_one(stock)
                sold += result.deleted_count
        return str(sold)

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

    def sell_stock(self, stock, price):
        stock["sell"] = {
            "price": price * self.global_config["binance"]["loss"],
            "timestamp":int(datetime.datetime.now().timestamp())
        }

    def buy_stock(self, symbol, quantity, price):
        return {
            "symbol": symbol,
            "quantity": int(quantity * self.global_config["binance"]["loss"]),
            "buy": {
                "price": price,
                "timestamp": int(datetime.datetime.now().timestamp())
            },
            "sell": None
        }