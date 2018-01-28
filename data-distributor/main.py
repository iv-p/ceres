import yaml
import numpy as np
import sys
from flask import Flask
from db import DB
from tempfile import TemporaryFile

from aggregator import Aggregator
from provider import Provider
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
aggregator = Aggregator(global_config, currency_config, db)
provider = Provider(global_config, db, app)
api = Api(app, aggregator)
app.run("0.0.0.0")
