import yaml
import sys
import time

from flask import Flask
from checker import Checker
from db import DB
from api import Api

global_config_file = "global.yaml"
currency_config_file = "currencies.yaml"
config_dir = "/config/"


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
checker = Checker(global_config, currency_config, db)
api = Api(app, checker)
app.run("0.0.0.0")