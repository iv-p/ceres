import numpy as np
import time
import threading
import pymongo
from scipy import stats
import math

def mapper(t):
    return float(t["high"]) + float(t["low"]) / 2

class Aggregator:
    def __init__(self, global_config, currency_config, db):
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db

        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def tock(self):
        np.set_printoptions(threshold=np.nan)
        network_input = self.global_config["neural_network"]["input"]
        network_output = self.global_config["neural_network"]["output"]
        currency_data = {}

        print("saving data")
        shortest_data_count = 0
        for currency in self.currency_config.keys():
            klines_data = list(self.db.get(currency, "klines").find().sort("timestamp", pymongo.ASCENDING))
            klines_data = [mapper(x) for x in klines_data]
            currency_data[currency] = klines_data
            if len(klines_data) < shortest_data_count or shortest_data_count == 0:
                shortest_data_count = len(klines_data)
        
        lin_regression_x = np.arange(network_input)
        data_per_currency = shortest_data_count - network_input - 61
        num_of_currencies = len(self.currency_config.keys())
        data = np.empty((data_per_currency * num_of_currencies , network_input + network_output + 1))

        batches = data_per_currency / network_input

        for currency in self.currency_data.keys():
            currency_data[currency] = currency_data[currency][:-data_per_currency]

        j = 0
        for i in range(0, data_per_currency):
            # calculate the global trend
            slopes = []
            for currency in currency_data.keys():
                slope = stats.linregress(lin_regression_x, currency_data[currency][i:i + network_input])
                slopes.append(slope)

            general_trend = np.average(slopes)

            for currency in currency_data.keys():
                input_data = currency_data[currency][i:i + network_input + 61]

                label_data = input_data[network_input + 1]
                label_data = np.append(label_data, input_data[network_input + 60])

                # normalize the data
                max_value = np.max(input_data[:network_input])
                input_data = input_data[:network_input] / max_value
                label_data = label_data / max_value
                input_data = np.append(input_data, general_trend)

                result = np.append(input_data, label_data)
                data[j] = result
                j+=1

        data = data[:j]

        np.save(self.global_config["neural_network"]["training_file"], data)
        print(str(data.shape) + " sets of data saved")

    def tick(self):
        np.set_printoptions(threshold=np.nan)
        network_input = self.global_config["neural_network"]["input"]
        network_output = self.global_config["neural_network"]["output"]
        currency_data = {}
        result = np.empty((0, 50, network_input+ network_output))
        lin_regression_x = np.arange(60)

        print("saving data")
        shortest_data_count = 0
        for currency in self.currency_config.keys():
            klines_data = list(self.db.get(currency, "klines").find().sort("timestamp", pymongo.ASCENDING).limit(3 * 14400))
            klines_data = [mapper(x) for x in klines_data]
            data_points = len(klines_data) - network_input - 61

            data = np.empty((math.ceil(data_points / 50), 50, network_input + network_output))
            batch = np.empty((50, network_input + network_output))

            for i in range(0, data_points):
                if i % 50 == 0 and i > 0:
                    data[math.floor(i/50)] = batch 

                input = klines_data[i:i + network_input]
                input = input / np.max(input)
                slope = stats.linregress(lin_regression_x, klines_data[i+ network_input + 1:i + network_input + 61])
                row = np.concatenate((input, [slope.slope]))
                batch[i % 50] = row

            result = np.vstack((result, data))
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
