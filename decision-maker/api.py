from flask import Flask
import json

class Api:
    def __init__(self, app, checker):
        @app.route("/healthcheck")
        def healthcheck():
            if checker.healthcheck():
                return "OK"
            return "down"

        @app.route("/events")
        def get_events():
            return json.dumps(checker.get_events())

        @app.route("/thresholds/<verb>/<float:value>", methods=['POST'])
        def set_thresholds(verb, value):
            if verb == "buy":
                checker.set_buy(value)
            elif verb == "sell":
                checker.set_sell(value)
            else:
                return "verb not found"
            return "OK"


