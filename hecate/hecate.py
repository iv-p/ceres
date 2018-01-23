#!/usr/bin/env python
from genalg.GeneticAlgorithm import GeneticAlgorithm
from neunet.NetworkIndividual import NetworkIndividual

def main():
    ''' Program entry '''
    params = {
        "generations": 1000,
        "population": 40, #individual = neural network
        "crossover": 0.2,
        "mutation": 0.2,
        "threshold": 0.99,
        "backup_file": "./backup/run.bac",
        "class": NetworkIndividual,
        "individual_params": {
            "input_size": 1920,
            "categories": 13,
            "min_layers": 5,
            "max_layers": 40,
            "min_neurons": 20,
            "max_neurons": 4000,
            "batch_size": 100,
            "total_iters": 200,
            "base_learning_rate": 0.2,
            "gamma": 0.9
        }
    }

    ga = GeneticAlgorithm(params)

if __name__ == '__main__':
    main()
