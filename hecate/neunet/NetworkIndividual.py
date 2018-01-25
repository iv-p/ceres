''' Neural network individual in genetic algorithms '''
import os
import numpy as np
import uuid
import random

from genalg.individual import Individual
import tensorflow as tf

class NetworkIndividual(Individual):
    ''' Defines how an neural network is generated, mutated, etc. '''
    def __init__(self, params, layers=[]):
        self.fitness = 0
        self.params = params
        self.layers = np.array(layers)
        
        self.loss = np.zeros(self.params["total_iters"])

        if len(self.layers) == 0:
            self.generate_layers()

    def crossover(self, other):
        ''' Defines how we crossover two individuals and produce
            two new ones '''
        my_point = random.randint(1, len(self.layers))
        other_point = random.randint(0, len (other.layers) - 1)

        layers = np.concatenate((self.layers[:my_point], other.layers[other_point:]))

        for layer in layers:
            if "object" in layer.keys():
                del layer["object"]
        return NetworkIndividual(
            self.params,
            layers)

    def mutate(self):
        ''' Defines how we mutate an individual '''
        layer = random.randint(0, len(self.layers) - 1)
        self.layers[layer]["neurons"] = random.randint(self.params["min_neurons"], self.params["max_neurons"])

    def evaluate(self):
        tf.reset_default_graph()

        X, Y, opt, mse = self.define_model()

        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            X_train, Y_train, X_testing, Y_testing = self.params["data"]
            for iteration in range(self.params["total_iters"]):
                shuffle_indices = np.random.permutation(np.arange(len(Y_train)))
                X_train = X_train[shuffle_indices]
                Y_train = Y_train[shuffle_indices]

                losses = np.zeros(len(Y_train) // self.params["batch_size"])
                # Minibatch training
                for batch in range(0, len(Y_train) // self.params["batch_size"]):
                    start = batch * self.params["batch_size"]
                    batch_x = X_train[start:start + self.params["batch_size"]]
                    batch_y = Y_train[start:start + self.params["batch_size"]]
                    # Run optimizer with batch
                    sess.run(opt, feed_dict={X: batch_x, Y: batch_y})


            self.loss = sess.run(mse, feed_dict={X: X_testing, Y: Y_testing})

    def get_fitness(self):
        return np.min(self.loss)

    def generate_layers(self):
        num_layers = random.randint(self.params["min_layers"], self.params["max_layers"])
        for _ in range(0, num_layers):
            self.layers = np.append(self.layers, {
                "neurons" : random.randint(self.params["min_neurons"], self.params["max_neurons"]),
                "dropout" : random.uniform(self.params["min_dropout"], self.params["max_dropout"])
            })

    def define_model(self):
        X = tf.placeholder(dtype=tf.float32, shape=[None, self.params["input_size"]])
        Y = tf.placeholder(dtype=tf.float32, shape=[None, self.params["output_size"]])
        for i, layer in enumerate(self.layers):
            layer_input = X
            if i > 0:
                layer_input = self.layers[i-1]["object"]

            dense = tf.layers.dense(inputs=layer_input, units=layer["neurons"], activation=tf.nn.relu)
            dropout = tf.layers.dropout(
                inputs=dense, rate=layer["dropout"], training=True)

            self.layers[i]["object"] = dropout

        out = tf.layers.dense(inputs=self.layers[-1]["object"], units=2, activation=tf.nn.relu)

        # Cost function
        mse = tf.reduce_mean(tf.squared_difference(out, Y))

        # Optimizer
        opt = tf.train.AdamOptimizer().minimize(mse)

        return X, Y, opt, mse
