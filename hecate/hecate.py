#!/usr/bin/env python3
from genalg.GeneticAlgorithm import GeneticAlgorithm
from neunet.NetworkIndividual import NetworkIndividual

import numpy as np
import math

def load_data():
    data = np.load("../target/data/nn/training_data.npy")
    up_to = math.floor(data.shape[0] / 10) * 10
    X_train = np.asarray(data[:,:5], dtype=np.float64)
    Y_train = np.asarray(data[:,5:7], dtype=np.float64)
    return X_train, Y_train, X_train, Y_train

def main():
    ''' Program entry '''
    params = {
        "generations": 1000,
        "population": 40, #individual = neural network
        "crossover": 0.2,
        "mutation": 0.2,
        "threshold": 0.99,
        "backup_file": "./run.bac",
        "class": NetworkIndividual,
        "individual_params": {
            "input_size": 5,
            "output_size": 2,
            "categories": 13,
            "min_layers": 1,
            "max_layers": 3,
            "min_neurons": 20,
            "max_neurons": 200,
            "min_dropout": 0,
            "max_dropout": 0.5,
            "batch_size": 10,
            "total_iters": 10,
            "base_learning_rate": 0.2,
            "gamma": 0.9,
            "data": load_data()
        }
    }

    ga = GeneticAlgorithm(params)

if __name__ == '__main__':
    main()
