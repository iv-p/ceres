import numpy as np
import random
import tensorflow as tf

def define(params, model=None):
    if model is None:
        model = generate(params)
    
    X = tf.placeholder(tf.float32, [None, params["cell_size"], params["input_size"]])
    Y = tf.placeholder(tf.float32, [None, params["cell_size"], params["output_size"]])
    training = tf.placeholder(tf.bool)

    rnn_layers = []
    tf_layers = []

    for layer in model["layers"]:
        if layer["type"] == "rnn":
            l = tf.contrib.rnn.BasicRNNCell(num_units=layer["neurons"], activation=tf.nn.relu)
            rnn_layers.append(l)
        elif layer["type"] == "dense":
            if len(tf_layers) == 0:
                cell = tf.contrib.rnn.MultiRNNCell(rnn_layers)
                output, _ = tf.nn.dynamic_rnn(cell, X, dtype=tf.float32)
                tf_layers.append(output)
            l = tf.layers.dense(tf_layers[-1], layer["neurons"], activation=tf.nn.sigmoid)
            d = tf.layers.dropout(l, rate=layer["dropout"], training=training)
            tf_layers.append(d)

    logits = tf_layers[-1]

    loss = tf.losses.mean_squared_error(Y, logits)
    optimizer = tf.train.AdadeltaOptimizer(learning_rate=model["learning_rate"]).minimize(loss)
    return model, (X, Y, training, optimizer, loss, logits)

def generate(params):
    num_layers = random.randint(params["min_layers"], params["max_layers"])
    rnn_count = random.randint(1, num_layers)
    layers = []

    for _ in range(rnn_count):
        rnn = generate_rnn(params)
        layers.append(rnn)
    for _ in range(rnn_count, num_layers):
        dense = generate_dense(params)
        layers.append(dense)
    output = generate_output(params)
    layers.append(output)

    lr = random.uniform(params["min_learning_rate"], params["max_learning_rate"])
    return {
        "layers"        : layers,
        "learning_rate" : lr
    }

def generate_rnn(params):
    return {
        "neurons" : random.randint(params["min_neurons"], params["max_neurons"]),
        "type": "rnn"
    }

def generate_dense(params):
    return {
        "neurons" : random.randint(params["min_neurons"], params["max_neurons"]),
        "dropout" : random.uniform(params["min_dropout"], params["max_dropout"]),
        "type": "dense"
    }   

def generate_output(params):
    return {
        "neurons"   : params["output_size"],
        "dropout"   : 0,
        "type"      : "dense"
    }