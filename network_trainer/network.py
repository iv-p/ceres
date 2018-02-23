import os
import numpy as np
import uuid
import random
import os
import zipfile
import tensorflow as tf
import pickle
import sys
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

class Network():
    local_model_file = "model.zip"
    local_model_dir = "./model/"

    def __init__(self, params, import_data=None, layers=[]):
        self.params = params
        self.config = params["config"]
        if import_data != None:
            self.layers = import_data["layers"]
            self.name = import_data["name"]
            self.loss = import_data["loss"]
        else:
            if len(layers) == 0:
                self.layers = self.generate_layers()
            else:
                self.layers = layers
            self.name = str(uuid.uuid4())
            self.loss = float("inf")


    def crossover(self, other):
        my_point = random.randint(1, len(self.layers))
        other_point = random.randint(0, len (other.layers) - 1)

        layers = np.concatenate((self.layers[:my_point], other.layers[other_point:]))

        for layer in layers:
            if "object" in layer.keys():
                del layer["object"]
        return Network(
            self.params,
            layers=layers)

    def mutate(self):
        layer = random.randint(0, len(self.layers) - 1)
        self.layers[layer]["neurons"] = random.randint(self.params["min_neurons"], self.params["max_neurons"])

    def evaluate(self, best_fitness):
        tf.reset_default_graph()

        X, Y, opt, loss, outputs, accuracy, confusion = self.define_model()

        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            X_train, Y_train, X_test, Y_test = self.params["data"]
            for iteration in range(self.params["total_iters"]):
                losses = np.zeros(len(Y_train) // self.params["batch_size"])
                # Minibatch training
                print(".")
                for batch in range(0, len(Y_train) // self.params["batch_size"]):
                    start = batch * self.params["batch_size"]
                    # Run optimizer with batch
                    sess.run(opt, feed_dict={
                        X: X_train[start:start + self.params["batch_size"]], 
                        Y: Y_train[start:start + self.params["batch_size"]]
                    })

            con = np.zeros((self.params["output_size"], self.params["output_size"]))
            accuracies = [] 
            for batch in range(0, len(Y_test) // self.params["batch_size"]):
                start = batch * self.params["batch_size"]
                current_accuracy = sess.run(accuracy, feed_dict={
                    X: X_test[start:start + self.params["batch_size"]], 
                    Y: Y_test[start:start + self.params["batch_size"]]
                })
                con += sess.run(confusion, feed_dict={
                    X: X_test[start:start + self.params["batch_size"]], 
                    Y: Y_test[start:start + self.params["batch_size"]]
                })
                accuracies.append(current_accuracy)
            self.loss = np.average(accuracies)
            print(con)
            print(self.loss)
            test_point = random.randint(0, X_test.shape[0])

            diff = sess.run(outputs, feed_dict={X: X_test[test_point:test_point + 1]})        
            print(diff)
            plt.close()
            plt.plot(X_test[test_point])
            plt.show(block=False)

            if self.loss < best_fitness:
                print(str(self.loss) + " saving model.")
                self.save_model(sess)

            print (".")
            sess.close()

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
                "name_1": str(uuid.uuid4()),
                "name_2": str(uuid.uuid4()),
            })
        return layers

    def define_model(self):
        # keep_prob_ = tf.placeholder(tf.float32, name='keep_prob')


        # lstms = [tf.contrib.cudnn_rnn.CudnnCompatibleLSTMCell(layer["neurons"]) for layer in self.layers]
        # drops = [tf.contrib.rnn.DropoutWrapper(lstm, output_keep_prob=0.5) for lstm in lstms]
        # cell = tf.contrib.rnn.MultiRNNCell(drops, state_is_tuple=True)

        # state = cell.zero_state(50, tf.float32)
        # rnn_outputs, final_state = cell(X, state)
        
        # outputs = tf.layers.dense(inputs=rnn_outputs, units=self.params["output_size"], activation=tf.nn.relu)
        # mse = tf.losses.mean_squared_error(Y, outputs[-1])
        # learning_rate = random.uniform(self.params["min_learning_rate"], self.params["max_learning_rate"])
        # optimizer = tf.train.AdamOptimizer(learning_rate).minimize(mse)

                # X = tf.placeholder(tf.float32, [None, 50, self.params["input_size"]])
                # Y = tf.placeholder(tf.float32, [None, self.params["output_size"]])

                # lstms = [tf.contrib.cudnn_rnn.CudnnCompatibleLSTMCell(layer["neurons"]) for layer in self.layers]
                # drops = [tf.contrib.rnn.DropoutWrapper(lstm, output_keep_prob=0.5) for lstm in lstms]
                # cell = tf.contrib.rnn.MultiRNNCell(drops, state_is_tuple=True)

                # val, _ = tf.nn.dynamic_rnn(cell, X, dtype=tf.float32)
                # val = tf.transpose(val, [1, 0, 2])
                # last = tf.gather(val, int(val.get_shape()[0]) - 1)

                # outputs = tf.layers.dense(inputs=last, units=self.params["output_size"], activation=tf.nn.relu)
                # loss = tf.reduce_mean(tf.square(outputs - Y))
                # learning_rate = random.uniform(self.params["min_learning_rate"], self.params["max_learning_rate"])
                # optimizer = tf.train.AdamOptimizer(learning_rate).minimize(loss)

        # self.layers = [
        #     {
        #         "neurons": 500,
        #         "dropout": 0.5
        #     },
        #     {
        #         "neurons": 100,
        #         "dropout": 0.5
        #     }
        # ]

        X = tf.placeholder(tf.float32, [None, self.params["input_size"]])
        Y = tf.placeholder(tf.float32, [None,])

        layers = np.array([X])
        for layer in self.layers:
            dense = tf.layers.dense(
                inputs=layers[-1], 
                units=layer["neurons"], 
                activation=tf.nn.sigmoid)
            dropout = tf.layers.dropout(
                inputs=dense, 
                rate=layer["dropout"], 
                training=True)
            layers = np.append(layers, dropout)

        logits = tf.layers.dense(
            inputs=layers[-1],
            units=self.params["output_size"], 
            activation=tf.nn.relu)
    
        # stacked_rnn_output = tf.reshape(logits, [-1, self.layers[-1]["neurons"]])
        # stacked_outputs = tf.layers.dense(stacked_rnn_output, self.params["output_size"])
        # out = tf.reshape(stacked_outputs, [-1, 50, self.params["output_size"]])

        onehot_labels = tf.one_hot(
            indices=tf.cast(Y, dtype=tf.int64),
            depth=self.params["output_size"],
            dtype=tf.int64)
        loss = tf.losses.softmax_cross_entropy(
            onehot_labels=onehot_labels, logits=logits)

        argmax_outputs = tf.argmax(input=logits, axis=1)
        accuracy = tf.reduce_mean(tf.cast(tf.equal(tf.cast(Y, dtype=tf.int64), argmax_outputs), tf.float32))
        confusion = tf.confusion_matrix(labels=Y, predictions=argmax_outputs, num_classes=self.params["output_size"])

        optimizer = tf.train.AdadeltaOptimizer().minimize(loss)

        return X, Y, optimizer, loss, argmax_outputs, accuracy, confusion
    
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

        zipf = zipfile.ZipFile("../bin/" + self.local_model_file, 'w', zipfile.ZIP_DEFLATED)
        zipdir(self.local_model_dir, zipf)
        zipf.close()      

    def export(self):
        return {
            "layers": self.layers,
            "name": self.name,
            "loss": self.loss
        }
