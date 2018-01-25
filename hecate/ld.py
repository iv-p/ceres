
import numpy as np
import tensorflow as tf

tf.reset_default_graph()

# Create some variables.
v1 = tf.get_variable("v1", shape=[3])
v2 = tf.get_variable("v2", shape=[5])

# Add ops to save and restore all the variables.
saver = tf.train.Saver()

# Later, launch the model, use the saver to restore variables from disk, and
# do some work with the model.
with tf.Session() as sess:
  # Restore variables from disk.
    saver.restore(sess, "./test.ckpt")
    print("Model restored.")

    mse_final = sess.run(mse, feed_dict={X: X_test, Y: Y_test})
    print(mse_final)