import json
import pymongo

class Events:
    def __init__(self, global_config, currency_config, db, app):
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db

        app.add_url_rule("/events", "events_history", self.get_events_history)
        app.add_url_rule("/events/currency/<currency>", "currency_events_history", self.get_events_history)
        app.add_url_rule("/events/type/<typ>", "type_events_history", self.get_type_events_history)

    def get_events_history(self, currency = None):
        events = None
        if currency is None:
            events = self.db.get("manager", "events").find().sort("timestamp", pymongo.DESCENDING)
        else:
            events = self.db.get("manager", "events").find({"currency": currency}).sort("timestamp", pymongo.DESCENDING)
        events_list = []
        for events in events:
            s = {
                "event": events["event"],
                "currency": events["currency"],
                "status": events["status"],
                "timestamp": events["timestamp"]
            }
            events_list.append(s)
        return json.dumps(events_list)

    def get_type_events_history(self, typ):
        events = self.db.get("manager", "events").find({"event": typ}).sort("timestamp", pymongo.DESCENDING)
        events_list = []
        for events in events:
            s = {
                "event": events["event"],
                "currency": events["currency"],
                "status": events["status"],
                "timestamp": events["timestamp"]
            }
            events_list.append(s)
        return json.dumps(events_list)
