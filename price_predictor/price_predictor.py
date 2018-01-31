from price_predictor.network import Network

class PricePredictor():
    def __init__(self, global_config, currency_config, db, data_distributor):
        self.network = Network(global_config, currency_config, db, data_distributor)