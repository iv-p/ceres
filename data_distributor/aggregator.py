import numpy as np
import time
import threading
import pymongo
from scipy import stats

def mapper(t):
    return float(t["high"]) + float(t["low"]) / 2

class Aggregator:
    def __init__(self, global_config, currency_config, db):
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db

        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        # self.thread.start()
        self.run()

    def tick(self):
        network_input = self.global_config["neural_network"]["input"]
        network_output = self.global_config["neural_network"]["output"]
        currency_data = {}

        print("saving data")
        shortest_data_count = 0
        for currency in self.currency_config.keys():
            klines_data = list(self.db.get(currency, "klines").find().sort("timestamp", pymongo.ASCENDING).limit(2*1440))
            klines_data = [mapper(x) for x in klines_data]
            currency_data[currency] = klines_data
            if len(klines_data) < shortest_data_count or shortest_data_count == 0:
                print(currency, len(klines_data))
                shortest_data_count = len(klines_data)
        
        print(shortest_data_count)
        lin_regression_x = np.arange(network_input)
        data_per_currency = shortest_data_count - network_input - 61
        num_of_currencies = len(self.currency_config.keys())
        data = np.empty((data_per_currency * num_of_currencies , network_input + network_output + 1))

        for i in range(0, data_per_currency):
            # calculate the global trend
            slopes = []
            for currency in currency_data.keys():
                slope = stats.linregress(lin_regression_x, currency_data[currency][i:i + network_input])
                slopes.append(slope)

            general_trend = np.average(slopes)
            if general_trend > 0:
                print(general_trend)

            j = 0
            for currency in currency_data.keys():
                input_data = currency_data[currency][i:i + network_input + 61]

                label_data = np.array([])
                label_data = np.append(label_data, input_data[network_input + 1])
                label_data = np.append(label_data, input_data[network_input + 60])

                # normalize the data
                input_data = input_data[:network_input] / np.max(input_data[:network_input])
                input_data = np.append(input_data, general_trend)

                result = np.append(input_data, label_data)
                result = result / np.max(result[:network_input])
                data[i * num_of_currencies + j] = result
                j+=1

        np.save(self.global_config["neural_network"]["training_file"], data)
        print(str(data.shape) + " sets of data saved")

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
