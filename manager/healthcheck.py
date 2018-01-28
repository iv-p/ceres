import requests
import json

class Healthcheck:
    def __init__(self, app, global_config):
        @app.route("/healthcheck")
        def healthcheck():
            services = {}
            for service, url in global_config["url"].items():
                response = requests.get(url + "/healthcheck")
                services[service] = response.text
            return json.dumps(services)