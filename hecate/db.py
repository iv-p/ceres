from pymongo import MongoClient
import logger


class DB:
    def __init__(self, global_config, currency_config):
        self.log = logger.get("db")
        self.global_config = global_config
        self.currency_config = currency_config
        self.client = MongoClient(self.global_config["mongodb"]["location"], 27017)
        try:
            self.client.admin.command('ismaster')
        except pymongo.errors.ConnectionFailure:
            print("Could not connect to mongodb")

    def get(self):
        return self.client[self.currency_config["name"]]
