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
    local_model_file = "/data/model.zip"
    local_model_dir = "./data/model/"

    def __init__(self, global_config, currency_config, db):
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db

        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def tick(self):
        print("tick")
        with tf.Session() as net:
            self.load()
            saver = tf.train.Saver()
            saver.restore(net, self.local_model_dir + self.global_config["neural_network"]["model_file"])

            for currency_code in self.currency_config.keys():
                print(currency_code)
                r = requests.get(self.global_config["url"]["data-distributor"] + "/" + currency_code + "/prediction_data")
                X_test = np.array([json.loads(r.text)])
                print(X_test)
                pred = net.run(self.out, feed_dict={self.X: X_test})
                print(pred)
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
            try:
                self.tick()
                time.sleep(interval - ((time.time() - starttime) % interval))
            except:
                pass

    def healthcheck(self):
        return self.thread.is_alive()
    
    def load(self):
        zipf = zipfile.ZipFile(self.local_model_file, 'r')
        zipf.extractall(".")
        zipf.close()
        self.params = pickle.load(open("./model/params", "rb"))

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
                                    activation=tf.nn.relu)
            dropout = tf.layers.dropout(
                                    inputs=dense, 
                                    rate=layer["dropout"], 
                                    training=True)
            layer_objects = np.append(layer_objects, dropout)

        self.out = tf.layers.dense(inputs=layer_objects[-1], units=2, activation=tf.nn.relu)
        self.mse = tf.reduce_mean(tf.squared_difference(self.out, self.Y))
        self.opt = tf.train.AdamOptimizer().minimize(self.mse)
