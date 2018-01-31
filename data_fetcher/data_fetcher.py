from data_fetcher.klines import Klines

class DataFetcher():
    def __init__(self, global_config, currency_config, app, db):
        self.klines = Klines(global_config, currency_config, db)
