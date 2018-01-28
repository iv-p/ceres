from flask import Flask

class Api:
    def __init__(self, app, network):

        @app.route("/healthcheck")
        def healthcheck():
            if network.healthcheck():
                return "OK"
            return "down"

