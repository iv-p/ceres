from genalg import GeneticAlgorithm
from network import Network

import numpy as np
import math
import yaml

data_len = 120

def load_data():
    data = np.load("../bin/training_data.npy")
    np.random.shuffle(data)
    up_to = int(data.shape[0] * 0.9)
    X_train = np.asarray(data[:up_to,:,:data_len], dtype=np.float64)
    Y_train = np.asarray(data[:up_to, 0, data_len], dtype=np.float64)
    X_test = np.asarray(data[up_to:,:,:data_len], dtype=np.float64)
    Y_test = np.asarray(data[up_to:, 0, data_len], dtype=np.float64)
    print(X_train.shape)
    print(X_test.shape)
    return X_train, Y_train, X_test, Y_test

class NetworkTrainer:
    global_config_file = "global"
    config_dir = "../config/"
    config_file_extention = ".yaml"
    params = {
        "generations": 1000,
        "population": 20,
        "crossover": 0.2,
        "mutation": 0.2,
        "threshold": 0.99,
        "backup_file": "./run.bac",
        "class": Network,
        "individual_params": {
            "input_size": data_len,
            "output_size": 2,
            "categories": 13,
            "min_layers": 2,
            "max_layers": 5,
            "min_neurons": 2,
            "max_neurons": 120,
            "min_dropout": 0.1,
            "max_dropout": 0.3,
            "batch_size": 10,
            "total_iters": 10,
            "min_learning_rate": 0.1,
            "max_learning_rate": 0.3,
            "data": load_data()
        }
    }

    def __init__(self):
        self.global_config = None
        try:
            with open(self.config_dir + self.global_config_file + self.config_file_extention) as fp:
                self.global_config = yaml.load(fp)

        except IOError:
            print("Error loading configuration files.")
            return

    def start(self):
        self.params["individual_params"]["config"] = self.global_config
        ga = GeneticAlgorithm(self.params)

if __name__ == "__main__":
    network_trainer = NetworkTrainer()
    network_trainer.start()
