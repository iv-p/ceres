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
        currency_fetch_data_len = 2000
        pred_len = 10
        lin_regression_x = np.arange(pred_len)
        bands = [0.95, 0.99, 1.01, 1.05]
        classes = len(bands) + 1
        averages = [1, 3, 5, 10, 15]

        features_per_currency = currency_fetch_data_len - data_len - pred_len - 1
        data_classes_len = np.zeros((classes), dtype=np.int)
        classes_result = np.zeros((len(averages), len(self.currency_config.keys()) * features_per_currency, len(averages), data_len + 1))

        print("saving data")
        for currency in self.currency_config.keys():
            klines_data = list(self.db.get(currency, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(currency_fetch_data_len))
            klines_data = [mapper(x) for x in klines_data]
            klines_data.reverse()

            for i in range(0, features_per_currency):
                features = np.zeros((len(averages), data_len + 1))
                input = klines_data[i:i + data_len]
                input = input / np.max(input)

                slope = stats.linregress(lin_regression_x, klines_data[i+ data_len + 1:i + data_len + pred_len + 1])
                diff = 1 + np.sum(np.arange(pred_len) * slope.slope) / klines_data[i+ data_len + 1]
                output = -1
                for index, band in enumerate(bands):
                    if diff < band:
                        output = index
                        break
                if output == -1:
                    output = len(bands)

                for index, average in enumerate(averages):
                    features[index] = np.concatenate((moving_average(input, N=average), [output]))

                classes_result[output, data_classes_len[output]] = features
                data_classes_len[output] += 1                

            print(currency)

        result = np.empty((0, 5, 121))

        least_data = data_classes_len[0]
        for value in data_classes_len:
            if least_data > value:
                least_data = value

        for i in range(classes):
            print(classes_result[i,:least_data, 0, 120])
            result = np.vstack((result, classes_result[i,:least_data]))

        np.save(self.global_config["neural_network"]["training_file"], result)
        print(str(result.shape) + " sets of data saved")
        print(data_classes_len)

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
