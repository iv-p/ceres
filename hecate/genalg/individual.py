''' Genetic algorithm module '''
class Individual(object):
    ''' Abstract class to define what functionality we need
        to define for each individual '''
    def __init__(self):
        ''' Defines how we generate an individual '''
        pass
    def crossover(self, other):
        ''' Defines how we crossover two individuals and produce
            two new ones
        '''
        pass
    def mutate(self):
        ''' Defines how we mutate an individual '''
        pass
    def evaluate(self):
        ''' Defines how we evaluate an individual.
            Returns the fitness of that individual '''
        pass
    def get_fitness(self):
        ''' Gets the fitness of the individual '''
        pass
