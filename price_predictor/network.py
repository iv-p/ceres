import os
import numpy as np
import zipfile
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import pickle
import datetime
import time
from threading import Lock
import common.neural_network as nn
from scipy import stats

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

        self.lock = Lock()

    def predict(self, currency):
        tf.reset_default_graph()
        self.model, (self.X, self.Y, self.training, self.opt, self.loss, self.out) = self.load()
        with tf.device("/cpu:0"):
            with tf.Session() as net:
                saver = tf.train.Saver()
                saver.restore(net, self.local_model_dir + self.global_config["neural_network"]["model_file"])

                x = self.data_distributor.provider.prediction_data(currency)
                pred = net.run(self.out, feed_dict={
                    self.X           : [x],
                    self.training    : False
                })
                timestamp = int(roundTime(datetime.datetime.now()).timestamp())
                price_predictions = pred[-1][-1] * self.data_distributor.provider.get_average_price(currency)
                x_data = np.arange(len(price_predictions))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, price_predictions)
                diff = (intercept + slope * 5) / intercept
                data = {
                    "timestamp": timestamp,
                    "prediction": diff
                }
                self.db.get(currency, "predictions").insert_one(data)
                net.close()
                return diff
        
    def load(self):
        self.lock.acquire()
        zipf = zipfile.ZipFile(self.local_model_file, 'r')
        zipf.extractall("./bin/")
        zipf.close()
        f = pickle.load(open("./bin/model/params", "rb"))
        self.params = f["params"]
        self.model = f["model"]
        self.lock.release()
        return nn.define(self.params, "/cpu:0", self.model)
