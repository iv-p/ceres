import os
import numpy as np
import uuid
import random
import os
import zipfile

import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import pickle
import sys
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import common.neural_network as nn

import statsmodels.api as sm

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

class Network():
    local_model_file = "model.zip"
    local_model_dir = "./model/"

    def __init__(self, params, import_data=None, model=None):
        self.params = params
        if import_data != None:
            self.model = import_data["model"]
            self.loss = import_data["loss"]
        else:
            self.model = None
            self.loss = float("inf")

        self.tf_config = tf.ConfigProto(allow_soft_placement = True)

    def crossover(self, other):
        my_point = random.randint(1, len(self.model["layers"]))
        other_point = random.randint(0, len (other.model["layers"]) - 1)

        layers = np.concatenate((self.model["layers"][:my_point], other.model["layers"][other_point:]))
        model = {
            "layers"        : layers,
            "learning_rate" : self.model["learning_rate"]
        }
        return Network(
            self.params,
            model=model)

    def mutate(self):
        layer = random.randint(0, len(self.model["layers"]) - 1)
        self.model["layers"][layer]["neurons"] = random.randint(self.params["min_neurons"], self.params["max_neurons"])

    def evaluate(self, best_model_loss):
        tf.reset_default_graph()

        with tf.device("/device:GPU:0"):
            with  tf.Session(config = self.tf_config) as model:
                (X, Y, training, opt, loss, output) = self.define_model()
                model.run(tf.global_variables_initializer())
                X_train, Y_train, X_test, Y_test = self.params["data"]
                losses = []
                for iteration in range(self.params["total_iters"]):
                    for batch in range(0, len(Y_train) // self.params["batch_size"]):
                        start = batch * self.params["batch_size"]
                        # Run optimizer with batch
                        model.run(opt, feed_dict={
                            X           : X_train[start:start + self.params["batch_size"]], 
                            Y           : Y_train[start:start + self.params["batch_size"]],
                            training    : True
                        })

                    iteration_losses = [] 
                    for batch in range(0, len(Y_test) // self.params["batch_size"]):
                        start = batch * self.params["batch_size"]
                        l = model.run(loss, feed_dict={
                            X           : X_test[start:start + self.params["batch_size"]], 
                            Y           : Y_test[start:start + self.params["batch_size"]],
                            training    : False
                        })
                        iteration_losses.append(l)
                    losses.append(np.average(iteration_losses))

                    if iteration > self.params["min_iters"] and losses[-1] / losses[-2] > 0.99:
                        print("stopping early with fitness {} after {}".format(losses[-1], iteration))
                        break
                self.loss = losses[-1]

                if self.loss < best_model_loss:
                    print(str(self.loss) + " saving model.")
                    self.save_model(model)

                print (".")
                model.close()

        return self.loss

    def get_fitness(self):
        return np.min(self.loss)

    def define_model(self):
        self.model, tensors = nn.define(self.params["model"], "/gpu:0", self.model)
        return tensors
    
    def save_model(self, model):
        saver = tf.train.Saver()
        if not os.path.exists(self.local_model_dir):
            os.makedirs(self.local_model_dir)
        save_path = saver.save(model, self.local_model_dir + self.params["config"]["neural_network"]["model_file"])

        params = {
            "params": self.params["model"],
            "model": self.model
        }
        
        pickle.dump(params, open(self.local_model_dir + "params", "wb"))

        zipf = zipfile.ZipFile("./bin/" + self.local_model_file, 'w', zipfile.ZIP_DEFLATED)
        zipdir(self.local_model_dir, zipf)
        zipf.close()

        self.params["predictor"].network.load()

    def export(self):
        return {
            "model": self.model,
            "loss": self.loss
        }
