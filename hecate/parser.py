#!/usr/bin/env python
import yaml
import sys
import time
import sqlite3
import numpy as np

from db import DB
from caffe2.python import core, utils
from caffe2.proto import caffe2_pb2

class Hecate:
    global_config_file = "global"
    config_dir = "/config/"
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
        data = np.array([])

        since_timestamp = 0
        self.db.get().klines.find({"timestamp": { "$lt" : since_timestamp }}).sort("timestamp")

        train,val = np.split(data,[int(0.8*data.shape[0])])
        self.write_db("minidb", "data/crowdflower/train.minidb", train[:,:1920], train[:,1920:])
        self.write_db("minidb", "data/crowdflower/test.minidb", val[:,:1920], val[:,1920:])

    def write_db(self, db_type, db_name, features, labels):
        labels = labels.reshape(labels.shape[0]).flatten().astype(int)
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
    hecate = Hecate(sys.argv[1])
    starttime=time.time()
    try:
        while True:
            hecate.tick()
            time.sleep(60.0 - ((time.time() - starttime) % 60.0))
    except KeyboardInterrupt:
        hecate.stop()