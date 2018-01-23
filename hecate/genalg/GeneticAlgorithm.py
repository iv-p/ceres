''' Genetic algorithm module '''
import numpy as np
import pickle
import os.path
import random

class GeneticAlgorithm(object):
    ''' Genetic algorithm framework. Takes a param json object with definitions on how to
    run the network.
    '''
    def __init__(self, params):
        self.params = params
        self.generations = np.array([]) # numpy is library for very fast data manipulation
        self.generation = np.array([])

        if os.path.isfile(params["backup_file"]):
            print "Found existing backup file"
            with open(params["backup_file"], 'rb') as pickled_file:
                data = pickle.load(pickled_file)
                self.params = params
                self.generations = data["generations"]
                self.generation = self.generations[-1]
        
        self.run()

    def run(self):
        ''' General run method that creates a generation and:
                - evaluates it
                - saves the progess to a file
                - drops last x% of the population
                - mutates the left individuals
                - crosses over the individuals '''

        for i in range(len(self.generations), self.params["generations"]):
            print "Generation " + str(i)
            self.populate()
            self.evaluate()
            self.save_progress()
            self.drop()
            self.mutate()
            self.crossover()

    def populate(self):
        ''' Generates individuals in the current generation to fill it up to the max capacity '''
        print "populating..."
        for _ in range(len(self.generation), self.params["population"]):
            individual = self.params["class"](self.params["individual_params"])
            self.generation = np.append(self.generation, individual)

    def evaluate(self):
        ''' Evaluates the individuals in the current generation, sorts them by fitness
            and adds them to the history'''
        print "evaluating..."
        for individual in self.generation:
            if individual.get_fitness() > 0:
                continue
            individual.evaluate()

        self.generation = sorted(self.generation, key=lambda item: item.get_fitness(), reverse=True)
        print ""
        print "Genetarion evaluated. Maximum fitness is : " + str(self.generation[0].get_fitness())
        self.generations = np.append(self.generations, self.generation)

    def save_progress(self):
        ''' Dumps the previous and current generations and the parameters in a file
            so we can resume at a later date '''
        data = {
            "params": self.params,
            "generation": self.generation,
            "generations": self.generations
        }
        with open(self.params["backup_file"], 'wb') as pickled_file:
            pickle.dump(data, pickled_file)

    def drop(self):
        ''' Drops the lowest x% of individuals '''
        # idiot proof method to get an even number of individuals, so that we can pair them at a further stage
        to_keep = int(int(self.params["population"] * 2 * self.params["crossover"]) / 2)
        self.generation = self.generation[:to_keep]

    def mutate(self):
        ''' Tries to mutate some individuals from the current generation by getting a random
            number and based on the predefined params decides to mutate or not '''
        print "mutating..."
        mutated = 0
        # we don't change the best one because we don't want top break it
        for i in range(1, len(self.generation)):
            if random.random() < self.params["mutation"]:
                mutated += 1
                self.generation[i].mutate()
        print "mutated " + str(mutated) + " individuals"

    def crossover(self):
        ''' Mates the individuals in the generation in pairs -> (0,1) (2,3), etc.
            and adds the offsprings to the generation '''
        print "crossover..."
        children = np.array([])
        for even, odd in zip(self.generation[0::2], self.generation[1::2]):
            children = np.append(children, odd.crossover(even))
            children = np.append(children, even.crossover(odd))
        self.generation = self.generation[:1]
        self.generation = np.append(self.generation, children)
