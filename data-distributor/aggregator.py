import numpy as np
import time
import threading
import pymongo

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

    def tick(self):
        network_input = self.global_config["neural_network"]["input"]
        network_output = self.global_config["neural_network"]["output"]
        data = np.empty((0, network_input + network_output))

        for currency in self.currency_config.keys():
            since_timestamp = 0
            klines_data = np.array(list(self.db.get(currency, "klines").find().sort("timestamp", pymongo.ASCENDING)))
            count = len(klines_data)
            klines_data = np.array([mapper(x) for x in klines_data])

            for i in range(0, count - network_input - 60):
                input_data = klines_data[i:i + network_input]

                label_data = np.array([])
                label_data = np.append(label_data, klines_data[i + network_input + 1])
                label_data = np.append(label_data, klines_data[i + network_input + 60])

                result = np.append(input_data, label_data)
                result = result / np.max(result[:network_input])
                data = np.vstack((data, result))

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
