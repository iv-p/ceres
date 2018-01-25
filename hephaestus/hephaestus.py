#!/usr/bin/env python
import yaml
import sys
import time
import pymongo
import numpy as np

from db import DB
from caffe2.python import core, utils
from caffe2.proto import caffe2_pb2

def mapper(t):
    return float(t["high"]) + float(t["low"]) / 2

class Hephaestus:
    global_config_file = "global"
    config_dir = "../config/"
    config_file_extention = ".yaml"

    def __init__(self, currency_code):
        self.currency_config = None
        self.global_config = None
        try:
            with open(self.config_dir + self.global_config_file + self.config_file_extention) as fp:
                self.global_config = yaml.load(fp)

            with open(self.config_dir + currency_code + self.config_file_extention) as fp:
                self.currency_config = yaml.load(fp)
        except IOError:
            print("Error loading configuration files.")
            return

        self.db = DB(self.global_config, self.currency_config)

    def tick(self):
        self.loadData()

    def stop(self):
        pass

    def loadData(self):
        since_timestamp = 0
        klines_data = np.array(list(self.db.get("klines").find({"timestamp": { "$gt" : since_timestamp }}).sort("timestamp")))

        count = len(klines_data)
        klines_data = np.array([mapper(x) for x in klines_data])

        data = np.empty((0, self.global_config["neural_network"]["input"] + 3))

        for i in range(0, count - self.global_config["neural_network"]["input"] - 1440):
            input_data = klines_data[i:i + self.global_config["neural_network"]["input"]]

            label_data = np.array([])
            label_data = np.append(label_data, klines_data[i + self.global_config["neural_network"]["input"] + 1])
            label_data = np.append(label_data, klines_data[i + self.global_config["neural_network"]["input"] + 60])
            label_data = np.append(label_data, klines_data[i + self.global_config["neural_network"]["input"] + 1440])

            result = np.append(input_data, label_data)
            result = result / np.max(result)
            data = np.vstack((data, result))

        train,val = np.split(data,[int(0.8*data.shape[0])])
        self.write_db("minidb", "data/train.minidb", train[:,:200], train[:,200:])
        self.write_db("minidb", "data/test.minidb", val[:,:200], val[:,200:])

    def write_db(self, db_type, db_name, features, labels):
        labels = labels.reshape(labels.shape[0]).flatten().astype(float)
        db = core.C.create_db(db_type, db_name, core.C.Mode.write)
        transaction = db.new_transaction()
        for i in range(features.shape[0]):
            feature_and_label = caffe2_pb2.TensorProtos()
            feature_and_label.protos.extend([
                utils.NumpyArrayToCaffe2Tensor(features[i]),
                utils.NumpyArrayToCaffe2Tensor(labels[i])])
            transaction.put(
                'train_%03d'.format(i),
                feature_and_label.SerializeToString())
        # Close the transaction, and then close the db.
        del transaction
        del db

if __name__ == "__main__":
    hephaestus = Hephaestus(sys.argv[1])
    starttime=time.time()
    try:
        while True:
            hephaestus.tick()
            time.sleep(60.0 - ((time.time() - starttime) % 60.0))
    except KeyboardInterrupt:
        hephaestus.stop()