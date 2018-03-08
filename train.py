#!/usr/bin/env python3

from trainer.genalg import GeneticAlgorithm
from trainer.network import Network

import numpy as np
import math
import yaml
import threading

data_len = 600

def load_data():
    data = np.load("./bin/training_data.npy")
    np.random.shuffle(data)
    up_to = int(data.shape[0] * 0.9)
    X_train = np.asarray(data[:up_to, :data_len], dtype=np.float64)
    Y_train = np.asarray(data[:up_to, data_len:], dtype=np.float64)
    X_test = np.asarray(data[up_to:, :data_len], dtype=np.float64)
    Y_test = np.asarray(data[up_to:, data_len:], dtype=np.float64)
    print(X_train.shape)
    print(X_test.shape)
    return X_train, Y_train, X_test, Y_test

global_config_file = "global"
config_dir = "./config/"
config_file_extention = ".yaml"
params = {
    "population"        : 20,
    "crossover"         : 0.2,
    "mutation"          : 0.2,
    "threshold"         : 0.99,
    "backup_file"       : "./run.bac",
    "class"             : Network,
    "individual_params" : {
        "model" : {
            "input_size"        : data_len,
            "output_size"       : 1,
            "min_layers"        : 2,
            "max_layers"        : 10,
            "min_neurons"       : 2,
            "max_neurons"       : 200,
            "min_dropout"       : 0.01,
            "max_dropout"       : 0.5,
            "min_learning_rate" : 0.001,
            "max_learning_rate" : 0.01,
            "cell_size"         : 10
        },
        "batch_size"    : 10,
        "total_iters"   : 100,
        "min_iters"     : 5,
        "data"          : load_data()
    }
}

global_config = None
try:
    with open(config_dir + global_config_file + config_file_extention) as fp:
        global_config = yaml.load(fp)

except IOError:
    print("Error loading configuration files.")
    os.exit()

ga = GeneticAlgorithm(params)
