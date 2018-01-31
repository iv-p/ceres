from manager.healthcheck import Healthcheck

class Manager:
    def __init__(self, global_config, currency_config, db, app):
        self.healthcheck = Healthcheck(app, self.global_config)
