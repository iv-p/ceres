from decision_maker.checker import Checker

class DecisionMaker():
    def __init__(self, global_config, currency_config, db, stock_manager, price_predictor):
        self.checker = Checker(global_config, currency_config, db, stock_manager, price_predictor)
