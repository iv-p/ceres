import os
import numpy as np
import uuid
import random
import os
import zipfile
import tensorflow as tf
import boto3
import pickle

class Network():
    local_model_file = "model.zip"
    local_model_dir = "./models/"

    def __init__(self, config):
        self.config = config
        self.load()

    def predict(self):
        
        with tf.Session() as net:
            saver = tf.train.Saver()
            saver.restore(net, self.local_model_dir + self.config["neural_network"]["model_file"])
            X_test = np.array([[0.2, 0.2, 0.1, 0, 1]])
            pred = net.run(self.out, feed_dict={self.X: X_test})
            print(pred)
    
    def load(self):
        session = boto3.session.Session()
        client = session.client('s3',
                                region_name=self.config["digital_ocean"]["region"],
                                endpoint_url=self.config["digital_ocean"]["endpoint"],
                                aws_access_key_id=self.config["digital_ocean"]["access_key"],
                                aws_secret_access_key=self.config["digital_ocean"]["access_secret"])

        client.download_file(
                            self.config["digital_ocean"]["space"], 
                            self.config["digital_ocean"]["model_file"], 
                            self.local_model_file)
        zipf = zipfile.ZipFile(self.local_model_file, 'r')
        zipf.extractall(".")
        zipf.close()
        self.params = pickle.load(open(self.local_model_dir + "params", "rb"))

        self.define_model()

    def define_model(self):
        tf.reset_default_graph()
        self.X = tf.placeholder(dtype=tf.float32, shape=[None, self.params["input"]])
        self.Y = tf.placeholder(dtype=tf.float32, shape=[None, self.params["output"]])

        layer_objects = np.array([ self.X ])
        for i, layer in enumerate(self.params["layers"]):
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

        self.out = tf.layers.dense(inputs=layer_objects[-1], units=2, activation=tf.nn.relu)
        self.mse = tf.reduce_mean(tf.squared_difference(self.out, self.Y))
        self.opt = tf.train.AdamOptimizer().minimize(self.mse)
