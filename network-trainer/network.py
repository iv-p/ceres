import os
import numpy as np
import uuid
import random
import os
import zipfile
import tensorflow as tf
import boto3
import pickle

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

class Network():
    local_model_file = "model.zip"
    local_model_dir = "./model/"

    def __init__(self, params, import_data=None):
        self.params = params
        self.config = params["config"]
        if import_data != None:
            self.layers = import_data["layers"]
            self.name = import_data["name"]
            self.loss = import_data["loss"]
        else:
            self.layers = self.generate_layers()
            self.name = str(uuid.uuid4())
            self.loss = float("inf")


    def crossover(self, other):
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
        layer = random.randint(0, len(self.layers) - 1)
        self.layers[layer]["neurons"] = random.randint(self.params["min_neurons"], self.params["max_neurons"])

    def evaluate(self, best_fitness):
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
            if self.loss < best_fitness:
                print("saving model.")
                self.save_model(sess)

            print (".")

        return self.loss

    def get_fitness(self):
        return np.min(self.loss)

    def generate_layers(self):
        num_layers = random.randint(self.params["min_layers"], self.params["max_layers"])
        layers = np.array([])
        for _ in range(0, num_layers):
            layers = np.append(layers, {
                "neurons" : random.randint(self.params["min_neurons"], self.params["max_neurons"]),
                "dropout" : random.uniform(self.params["min_dropout"], self.params["max_dropout"]),
                "name": str(uuid.uuid4())
            })
        return layers

    def define_model(self):
        X = tf.placeholder(dtype=tf.float32, shape=[None, self.params["input_size"]])
        Y = tf.placeholder(dtype=tf.float32, shape=[None, self.params["output_size"]])

        layer_objects = np.array([ X ])
        for i, layer in enumerate(self.layers):
            dense = tf.layers.dense(
                                    inputs=layer_objects[-1], 
                                    units=layer["neurons"], 
                                    activation=tf.nn.relu,
                                    name=layer["name"] + "-dense")
            dropout = tf.layers.dropout(
                                    inputs=dense, 
                                    rate=layer["dropout"],
                                    training=True,
                                    name=layer["name"] + "-dropout")
            layer_objects = np.append(layer_objects, dropout)

        out = tf.layers.dense(inputs=layer_objects[-1], units=self.params["output_size"], activation=tf.nn.relu)
        mse = tf.reduce_mean(tf.squared_difference(out, Y))
        opt = tf.train.AdamOptimizer().minimize(mse)

        return X, Y, opt, mse
    
    def save_model(self, sess):
        saver = tf.train.Saver()
        if not os.path.exists(self.local_model_dir):
            os.makedirs(self.local_model_dir)
        save_path = saver.save(sess, self.local_model_dir + self.config["neural_network"]["model_file"])

        params = {
            "layers": self.layers,
            "loss": self.loss,
            "input": self.params["input_size"],
            "output": self.params["output_size"]
        }
        
        pickle.dump(params, open(self.local_model_dir + "params", "wb"))

        zipf = zipfile.ZipFile(self.local_model_file, 'w', zipfile.ZIP_DEFLATED)
        zipdir(self.local_model_dir, zipf)
        zipf.close()

        session = boto3.session.Session()
        client = session.client('s3',
                                region_name=self.config["digital_ocean"]["region"],
                                endpoint_url=self.config["digital_ocean"]["endpoint"],
                                aws_access_key_id=self.config["digital_ocean"]["access_key"],
                                aws_secret_access_key=self.config["digital_ocean"]["access_secret"])

        client.upload_file(
                    self.config["digital_ocean"]["model_file"], 
                    self.config["digital_ocean"]["space"], 
                    self.local_model_file)
        

    def export(self):
        return {
            "layers": self.layers,
            "name": self.name,
            "loss": self.loss
        }
