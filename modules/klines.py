import requests
import sqlite3
import numpy as np
import logger

class Klines:
    def __init__(self, global_config, currency_config, sql_helper):
        self.log = logger.get("klines")
        self.global_config = global_config
        self.currency_config = currency_config
        self.sql_helper = sql_helper

    def run(self):
        connection = self.sql_helper.get()
        c = connection.cursor()
        entries = 0
        for key in self.global_config["binance"]["intervals"].keys():
            interval = self.global_config["binance"]["intervals"][key]
            payload = {
                "symbol": self.currency_config["symbol"],
                "interval": interval
            }
            r = requests.get(self.global_config["binance"]["url"] + "api/v1/klines", payload)
            data = np.array(r.json())
            data = np.delete(data, 4, 1)
            data = np.delete(data, 10, 1)

            for entry in data:
                try:
                    c.execute("INSERT INTO " + key + " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", entry)
                    connection.commit()
                    entries += 1
                except sqlite3.IntegrityError:
                    continue
        c.close()
        connection.close()

        self.log.info(str(entries) + " klines saved")
