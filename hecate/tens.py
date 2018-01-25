from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf

data = np.load("../target/data/nn/training_data.npy")
X_train = np.asarray(data[:,:5], dtype=np.float64)
Y_train = np.asarray(data[:,5:7], dtype=np.float64)
X_test = np.asarray(data[:,:5], dtype=np.float64)
Y_test = np.asarray(data[:,5:7], dtype=np.float64)

n_stocks = 5
n_neurons_1 = 1024
n_neurons_2 = 512
n_neurons_3 = 256
n_neurons_4 = 128
n_target = 2

# Placeholder
X = tf.placeholder(dtype=tf.float32, shape=[None, n_stocks])
Y = tf.placeholder(dtype=tf.float32, shape=[None, n_target])


dense = tf.layers.dense(inputs=X, units=1024, activation=tf.nn.relu)
dropout = tf.layers.dropout(
    inputs=dense, rate=0.4, training=True)

dense = tf.layers.dense(inputs=dense, units=512, activation=tf.nn.relu)
dropout = tf.layers.dropout(
    inputs=dense, rate=0.4, training=True)

dense = tf.layers.dense(inputs=dense, units=256, activation=tf.nn.relu)
dropout = tf.layers.dropout(
    inputs=dense, rate=0.4, training=True)

dense = tf.layers.dense(inputs=dense, units=128, activation=tf.nn.relu)
dropout = tf.layers.dropout(
    inputs=dense, rate=0.4, training=True)

dense = tf.layers.dense(inputs=dropout, units=2, activation=tf.nn.relu)
out = tf.layers.dropout(
    inputs=dense, rate=0.4, training=True)

# Cost function
mse = tf.reduce_mean(tf.squared_difference(out, Y))

# Optimizer
opt = tf.train.AdamOptimizer().minimize(mse)

# Make Session
net = tf.Session()

# Number of epochs and batch size
epochs = 10
batch_size = 10

for e in range(epochs):

    # Shuffle training data
    shuffle_indices = np.random.permutation(np.arange(len(Y_train)))
    X_train = X_train[shuffle_indices]
    Y_train = Y_train[shuffle_indices]

    # Minibatch training
    for i in range(0, len(Y_train) // batch_size):
        start = i * batch_size
        batch_x = X_train[start:start + batch_size]
        batch_y = Y_train[start:start + batch_size]
        # Run optimizer with batch
        loss = net.run(opt, feed_dict={X: batch_x, Y: batch_y})
        self.loss 

    pred = net.run(out, feed_dict={X: X_test[0:2,:]})
    
# Print final MSE after Training
mse_final = net.run(mse, feed_dict={X: X_test, Y: Y_test})
print(mse_final)
saver = tf.train.Saver()
saver.save(net, "./model/test.ckpt")