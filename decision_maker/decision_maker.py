from decision_maker.checker import Checker

class DecisionMaker():
    def __init__(self, global_config, currency_config, app, db):
        self.checker = Checker(global_config, currency_config, db)
