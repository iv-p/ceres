import yaml
import sys

from flask import Flask
from common.db import DB
from data_fetcher.data_fetcher import DataFetcher
from data_distributor.data_distributor import DataDistributor
from price_predictor.price_predictor import PricePredictor
from decision_maker.decision_maker import DecisionMaker
from stock_manager.stock_manager import StockManager
from manager.manager import Manager

global_config_file = "global.yaml"
currency_config_file = "currencies.yaml"
config_dir = "./config/"

currency_config = None
global_config = None
try:
    with open(config_dir + global_config_file) as fp:
        global_config = yaml.load(fp)

    with open(config_dir + currency_config_file) as fp:
        currency_config = yaml.load(fp)
except IOError:
    print("Error loading configuration files.")
    sys.exit(1)

app = Flask(__name__)
db = DB(global_config)

data_fetcher = DataFetcher(global_config, currency_config, app, db)
data_distributor = DataDistributor(global_config, currency_config, app, db)
price_predictor = PricePredictor(global_config, currency_config, app, db)
decision_maker = DecisionMaker(global_config, currency_config, app, db)
stock_manager = StockManager(global_config, currency_config, app, db)
manager = Manager(global_config, currency_config, app, db)

app.run("0.0.0.0")