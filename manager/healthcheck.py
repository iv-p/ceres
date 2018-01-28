import requests
import json

class Healthcheck:
    def __init__(self, app, global_config):
        @app.route("/healthcheck")
        def healthcheck():
            services = {}
            for service, url in global_config["url"].items():
                txt = "down"
                try:
                    response = requests.get(url + "/healthcheck")
                    txt = response.text
                except:
                    pass
                services[service] = txt
            return json.dumps(services)