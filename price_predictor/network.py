import os
import numpy as np
import os
import zipfile
import tensorflow as tf
import pickle
import requests
import json
import datetime
import time
import threading

def roundTime(dt=None, roundTo=60):
   if dt == None : dt = datetime.datetime.now()
   seconds = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

class Network():
    local_model_file = "./bin/model.zip"
    local_model_dir = "./bin/model/"

    def __init__(self, global_config, currency_config, db):
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db

        self.load_file = True

        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def tick(self):
        if self.load_file:
            tf.reset_default_graph()
            self.load()
        with tf.Session() as net:
            saver = tf.train.Saver()
            saver.restore(net, self.local_model_dir + self.global_config["neural_network"]["model_file"])

            for currency_code in self.currency_config.keys():
                r = requests.get(self.global_config["url"]["data-distributor"] + "/" + currency_code + "/prediction_data")
                X_test = np.array([json.loads(r.text)])
                pred = net.run(self.out, feed_dict={self.X: X_test})
                timestamp = int(roundTime(datetime.datetime.now()).timestamp())
                data = {
                    "timestamp": timestamp,
                    "predictions": pred[0].tolist()
                }
                self.db.get(currency_code, "predictions").insert_one(data)
                print("prediction for " + currency_code + " is " + str(data["predictions"]))
            net.close()

    def run(self):
        starttime=time.time()
        interval = self.global_config["price-predictor"]["interval"]
        while True:
            # try:
            self.tick()
            time.sleep(interval - ((time.time() - starttime) % interval))
            # except e:
            #     print(e)

    def healthcheck(self):
        return self.thread.is_alive()
    
    def load(self):
        print("loading new model")
        zipf = zipfile.ZipFile(self.local_model_file, 'r')
        zipf.extractall("./bin/")
        zipf.close()
        self.params = pickle.load(open("./bin/model/params", "rb"))

        self.define_model()

        self.load_file = False

    def define_model(self):
        self.X = tf.placeholder(dtype=tf.float32, shape=[None, self.params["input"]])
        self.Y = tf.placeholder(dtype=tf.float32, shape=[None, self.params["output"]])

        layer_objects = np.array([ self.X ])
        for i, layer in enumerate(self.params["layers"]):
            dense = tf.layers.dense(
                                    inputs=layer_objects[-1], 
                                    units=layer["neurons"],
                                    # name=layer["name_1"],
                                    activation=tf.nn.relu)
            dropout = tf.layers.dropout(
                                    inputs=dense, 
                                    rate=layer["dropout"], 
                                    # name=layer["name_2"],
                                    training=True)
            layer_objects = np.append(layer_objects, dropout)

        self.out = tf.layers.dense(inputs=layer_objects[-1], units=2, activation=tf.nn.relu)
        self.mse = tf.reduce_mean(tf.squared_difference(self.out, self.Y))
        self.opt = tf.train.AdamOptimizer().minimize(self.mse)

    def bump(self):
        self.load_file = True
