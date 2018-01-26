#!/usr/bin/env python3
import yaml
import sys
import time
import numpy as np
from db import DB
from tempfile import TemporaryFile

def mapper(t):
    return float(t["high"]) + float(t["low"]) / 2

class Hephaestus:
    global_config_file = "global"
    config_dir = "/config/"
    config_file_extention = ".yaml"

    def __init__(self, currency_code):
        self.currency_config = None
        self.global_config = None
        try:
            with open(self.config_dir + self.global_config_file + self.config_file_extention) as fp:
                self.global_config = yaml.load(fp)

            with open(self.config_dir + currency_code + self.config_file_extention) as fp:
                self.currency_config = yaml.load(fp)
        except IOError:
            print("Error loading configuration files.")
            return

        self.db = DB(self.global_config, self.currency_config)

    def tick(self):
        since_timestamp = 0
        klines_data = np.array(list(self.db.get("klines").find({"timestamp": { "$gt" : since_timestamp }}).sort("timestamp")))

        count = len(klines_data)
        klines_data = np.array([mapper(x) for x in klines_data])

        data = np.empty((0, self.global_config["neural_network"]["input"] + 2))

        for i in range(0, count - self.global_config["neural_network"]["input"] - 60):
            input_data = klines_data[i:i + self.global_config["neural_network"]["input"]]

            label_data = np.array([])
            label_data = np.append(label_data, klines_data[i + self.global_config["neural_network"]["input"] + 1])
            label_data = np.append(label_data, klines_data[i + self.global_config["neural_network"]["input"] + 60])
            # label_data = np.append(label_data, klines_data[i + self.global_config["neural_network"]["input"] + 1440])

            result = np.append(input_data, label_data)
            result = result / np.max(result[:self.global_config["neural_network"]["input"]])
            data = np.vstack((data, result))

        np.save(self.global_config["neural_network"]["training_file"], data)
        print("data saved")

    def stop(self):
        pass

if __name__ == "__main__":
    hephaestus = Hephaestus(sys.argv[1])
    starttime=time.time()
    try:
        while True:
            hephaestus.tick()
            time.sleep(60.0 - ((time.time() - starttime) % 60.0))
    except KeyboardInterrupt:
        hephaestus.stop()