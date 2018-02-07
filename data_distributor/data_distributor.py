from data_distributor.aggregator import Aggregator
from data_distributor.provider import Provider

class DataDistributor():
    def __init__(self, global_config, currency_config, db):
        # self.aggregator = Aggregator(global_config, currency_config, db)
        self.provider = Provider(global_config, currency_config, db)
