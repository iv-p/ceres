from pymongo import MongoClient


class DB:
    def __init__(self, global_config, currency_config):
        self.global_config = global_config
        self.currency_config = currency_config
        self.client = MongoClient(self.global_config["mongodb"]["location"], 27017)
        try:
            self.client.admin.command('ismaster')
        except pymongo.errors.ConnectionFailure:
            print("Could not connect to mongodb")

    def get(self, collection):
        return self.client[self.currency_config["name"]][collection]
