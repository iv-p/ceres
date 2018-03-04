from stock_manager.manager import Manager

class StockManager:
    def __init__(self, global_config, currency_config, db, data_distributor):
        self.manager = Manager(global_config, currency_config, db, data_distributor)
        