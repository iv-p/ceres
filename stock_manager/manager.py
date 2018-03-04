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

    def __init__(self, global_config, currency_config, db, data_distributor):
        self.stocks = []
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db
        self.data_distributor = data_distributor
        wallet = self.db.get("manager", "wallet").find({"type": "eth"})
        if wallet.count() == 0:
            self.wallet = 2.0            
            self.db.get("manager", "wallet").insert_one({
                "type": "eth",
                "quantity": self.wallet
            })
        else:
            self.wallet = float(wallet[0]["quantity"])

    def buy(self, currency):
        active_stocks = self.db.get("manager", "stocks").find({"sell": None})
        if active_stocks.count() >= 20:
            return "full"

        currency_stocks = self.db.get("manager", "stocks").find({"symbol": currency})
        if currency_stocks.count() > 0:
            return "slot filled"

        price = self.data_distributor.provider.get_average_price(currency)
        quantity = float(self.eth_per_stock) / price
        if self.wallet < price * quantity:
            return "not enough funds"
        
        self.wallet -= price * quantity
        self.update_wallet()
        stock = self.buy_stock(currency, quantity, price)
        self.db.get("manager", "stocks").insert_one(stock)

        return "OK"

    def sell(self, currency):
        stocks = self.db.get("manager", "stocks").find({"sell": None})
        sold = 0
        for stock in stocks:
            if stock["symbol"] == currency:
                result = self.db.get("manager", "stocks").delete_one(stock)
                price = self.data_distributor.provider.get_average_price(currency)
                self.wallet += price * stock["quantity"]
                self.update_wallet()
                self.sell_stock(stock, price)
                self.db.get("manager", "stocks").insert_one(stock)
                sold += result.deleted_count
        return str(sold)

    def get_worth(self):
        stocks = self.db.get("manager", "stocks").find({"sell": None})
        worth = 0
        for stock in stocks:
            price = self.data_distributor.provider.get_average_price(stock["symbol"])
            worth += price * stock["quantity"]
        return worth + self.wallet

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
        for stock in stocks:
            del stock["id"]
        return json.dumps(stocks)

    def sell_stock(self, stock, price):
        stock["sell"] = {
            "price": price * self.global_config["binance"]["loss"],
            "timestamp": int(datetime.datetime.now().timestamp())
        }

    def buy_stock(self, symbol, quantity, price):
        return {
            "symbol": symbol,
            "quantity": quantity * self.global_config["binance"]["loss"],
            "buy": {
                "price": price,
                "timestamp": int(datetime.datetime.now().timestamp())
            },
            "sell": None
        }
    def update_wallet(self):
        self.db.get("manager", "wallet").find_one_and_update({'type': 'eth'}, {'$set': {'quantity': self.wallet}})
        