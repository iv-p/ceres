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
        np.set_printoptions(threshold=np.nan)
        data_len = self.global_config["neural_network"]["input"]
        network_output = self.global_config["neural_network"]["output"]
        currency_data = {}
        pred_len = 10
        result = np.empty((0, data_len + 1))
        lin_regression_x = np.arange(pred_len)
        bands = [0.95, 0.99, 1.01, 1.05]
        averages = [1, 3, 5, 10, 15]
        data_classes_len = np.zeros((len(bands) + 1))


        print("saving data")
        shortest_data_count = 0
        for currency in self.currency_config.keys():
            klines_data = list(self.db.get(currency, "klines").find().sort("timestamp", pymongo.DESCENDING).limit(2000))
            klines_data = [mapper(x) for x in klines_data]
            klines_data.reverse()
            data_points = len(klines_data) - data_len - pred_len - 1

            data = np.empty((data_points, len(averages), data_len + 1))

            for i in range(0, data_points):
                features = np.zeros((len(averages), data_len))
                input = klines_data[i:i + data_len]
                input = input / np.max(input)

                slope = stats.linregress(lin_regression_x, klines_data[i+ data_len + 1:i + data_len + pred_len + 1])
                diff = 1 + np.sum(np.arange(pred_len) * slope.slope) / klines_data[i+ data_len + 1]
                output = -1
                for index, band in enumerate(bands):
                    if diff < band:
                        output = index
                if output == -1:
                    output = len(bands)
                    
                data_classes_len[output] += 1

                plt.close()
                for index, average in enumerate(averages):
                    features[index] = moving_average(input)
                    plt.plot(features[index])
                    plt.show()
                

                data[i] = np.concatenate((input, [output]))

            result = np.vstack((result, data))
            print(currency)

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
