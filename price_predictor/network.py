import os
import numpy as np
import os
import zipfile
import tensorflow as tf
import pickle
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

    def __init__(self, global_config, currency_config, db, data_distributor):
        self.global_config = global_config
        self.currency_config = currency_config
        self.db = db
        self.data_distributor = data_distributor

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

            for currency in self.currency_config.keys():
                X_test = self.data_distributor.provider.prediction_data(currency)
                pred = net.run(self.out, feed_dict={self.X: [X_test]})
                timestamp = int(roundTime(datetime.datetime.now()).timestamp())
                # print(float(pred[0].tolist()))
                price_predictions = np.array(pred[0].tolist(), dtype=np.float64) * self.data_distributor.provider.get_average_price(currency)
                data = {
                    "timestamp": timestamp,
                    "predictions": pred[0].tolist(),
                    "price_predictions": price_predictions.tolist()
                }
                self.db.get(currency, "predictions").insert_one(data)
                print("prediction for " + currency + " is " + str(data["predictions"]))
            net.close()

    def run(self):
        starttime=time.time()
        interval = self.global_config["price-predictor"]["interval"]
        while True:
            # try:
            self.tick()
            time.sleep(interval - ((time.time() - starttime) % interval))
            # except:
                # pass
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
        # self.X = tf.placeholder(dtype=tf.float32, shape=[None, self.params["input"]])
        # self.Y = tf.placeholder(dtype=tf.float32, shape=[None, self.params["output"]])

        # layer_objects = np.array([ self.X ])
        # for i, layer in enumerate(self.params["layers"]):
        #     dense = tf.layers.dense(
        #                             inputs=layer_objects[-1], 
        #                             units=layer["neurons"],
        #                             # name=layer["name_1"],
        #                             activation=tf.nn.relu)
        #     dropout = tf.layers.dropout(
        #                             inputs=dense, 
        #                             rate=layer["dropout"], 
        #                             # name=layer["name_2"],
        #                             training=True)
        #     layer_objects = np.append(layer_objects, dropout)

        # self.out = tf.layers.dense(inputs=layer_objects[-1], units=2, activation=tf.nn.relu)
        # self.mse = tf.reduce_mean(tf.squared_difference(self.out, self.Y))
        # self.opt = tf.train.AdamOptimizer().minimize(self.mse)
        
        self.X = tf.placeholder(tf.float32, [None, 50, self.params["input"]])
        self.Y = tf.placeholder(tf.float32, [None, 50, self.params["output"]])

        def rnn_cell(size):
            return tf.contrib.rnn.LSTMCell(num_units=size, activation=tf.nn.relu)

        stacked_lstm = tf.contrib.rnn.MultiRNNCell(
            [rnn_cell(layer["neurons"]) for layer in self.params["layers"]])

        output, state = tf.nn.dynamic_rnn(stacked_lstm, self.X, dtype=tf.float32)

        self.out = tf.layers.dense(
            inputs=output,
            units=self.params["output"], 
            activation=tf.nn.relu)

        self.mse = tf.reduce_mean(tf.squared_difference(self.out, self.Y))

    def bump(self):
        self.load_file = True
