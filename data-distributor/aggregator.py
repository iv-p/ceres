import numpy as np

def mapper(t):
    return float(t["high"]) + float(t["low"]) / 2

class Aggregator:
    def __init__(self, global_config, currency_config, db):
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db

    def tick(self):
        network_input = self.global_config["neural_network"]["input"]
        network_output = self.global_config["neural_network"]["output"]
        data = np.empty((0, network_input + network_output))

        for currency_code in self.currency_config.keys():
            since_timestamp = 0
            klines_data = np.array(list(self.db.get(currency_code, "klines").find().sort("timestamp", pymongo.ASCENDING)))
            count = len(klines_data)
            klines_data = np.array([mapper(x) for x in klines_data])

            for i in range(0, count - network_input - 60):
                input_data = klines_data[i:i + network_input]

                label_data = np.array([])
                label_data = np.append(label_data, klines_data[i + network_input + 1])
                label_data = np.append(label_data, klines_data[i + network_input + 60])
                # label_data = np.append(label_data, klines_data[i + self.config["neural_network"]["input"] + 1440])

                result = np.append(input_data, label_data)
                result = result / np.max(result[:network_input])
                data = np.vstack((data, result))

        np.save(self.config["neural_network"]["training_file"], data)
        print(currency_code + " data saved")