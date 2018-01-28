from flask import Flask

class Api:
    def __init__(self, app, aggregator):
        @app.route("/healthcheck")
        def healthcheck():
            if aggregator.healthcheck():
                return "OK"
            else:
                return "down"
        
        @app.route("/<currency>/data_volume")
        def get_currency_data_volume(currency):
            return str(aggregator.get_data_volume(currency))
