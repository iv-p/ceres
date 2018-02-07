from genalg import GeneticAlgorithm
from network import Network

import numpy as np
import math
import yaml

def load_data():
    data = np.load("../bin/training_data.npy")
    np.random.shuffle(data)
    up_to = int(data.shape[0] * 0.9)
    X_train = np.asarray(data[:up_to,:,:1440], dtype=np.float64)
    Y_train = np.asarray(data[:up_to,:,1440:], dtype=np.float64)[:,:,0]
    X_test = np.asarray(data[up_to:,:,:1440], dtype=np.float64)
    Y_test = np.asarray(data[up_to:,:,1440:], dtype=np.float64)[:,:,0]
    print(X_train.shape)
    print(Y_train.shape)
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
            "input_size": 1440,
            "output_size": 50,
            "categories": 13,
            "min_layers": 1,
            "max_layers": 2,
            "min_neurons": 20,
            "max_neurons": 50,
            "min_dropout": 0,
            "max_dropout": 0.5,
            "batch_size": 10,
            "total_iters": 2,
            "min_learning_rate": 0.00001,
            "max_learning_rate": 0.0001,
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