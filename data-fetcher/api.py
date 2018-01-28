from flask import Flask

class Api:
    def __init__(self, app, klines):

        @app.route("/healthcheck")
        def healthcheck():
            if klines.healthcheck():
                return "OK"
            return "down"

        app.run("0.0.0.0")

