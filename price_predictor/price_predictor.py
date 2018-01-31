from price_predictor.network import Network

class PricePredictor():
    def __init__(self, global_config, currency_config, app, db):
        self.network = Network(global_config, currency_config, db)