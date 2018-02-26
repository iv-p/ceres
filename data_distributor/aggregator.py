import numpy as np
import time
import threading
import pymongo
from scipy import stats
import math

import matplotlib.pyplot as plt

def mapper(t):
    return float(t["high"]) + float(t["low"]) / 2

def moving_average(x, N=3):
    return np.convolve(x, np.ones((N,))/N, mode='same')

class Aggregator:
    def __init__(self, global_config, currency_config, db):
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db

        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def tick(self):
        data_len = self.global_config["neural_network"]["input"]
        features_per_currency = 1000
        rnn_groups = 10
        skip = 5
        data_per_group = 60
        currency_fetch_data_len = features_per_currency * skip + rnn_groups * data_per_group
        pred_len = 5
        currencies_count = len(self.currency_config.keys())

        result = np.zeros((features_per_currency * currencies_count, rnn_groups, data_per_group + pred_len))

        print("saving data")
        for currency_index, currency in enumerate(self.currency_config.keys()):
            klines_data = list(self.db.get(currency, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(currency_fetch_data_len + pred_len))
            klines_data = [mapper(x) for x in klines_data]
            klines_data.reverse()
            for i, data_index in enumerate(range(0, currency_fetch_data_len - rnn_groups * data_per_group, skip)):
                features = np.zeros((rnn_groups, data_per_group + pred_len))
                for j in range(rnn_groups):
                    fr = data_index + j * data_per_group
                    to = fr + data_per_group
                    input = klines_data[fr : to]
                    min_input = np.min(input)
                    max_input = np.max(input) - min_input
                    input -= min_input
                    input /= max_input
                    pred = klines_data[to : to + pred_len]
                    pred -= min_input
                    pred /= max_input
                    features[j] = np.concatenate((input, pred))
                result[i + currency_index * features_per_currency] = features

            print(currency)

        np.save(self.global_config["neural_network"]["training_file"], result)
        print(str(result.shape) + " sets of data saved")

    def run(self):
        starttime=time.time()
        interval = self.global_config["data-distributor"]["interval"]
        while True:
            self.tick()
            time.sleep(interval - ((time.time() - starttime) % interval))
    
    def healthcheck(self):
        print(self.thread.is_alive())
        return self.thread.is_alive()

    def get_data_volume(self, currency):
        return self.db.get(currency, "klines").find().count()
