# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 13:33:14 2017

@author: think
"""

import tensorflow as tf
from tensorflow.contrib import rnn
import tensorflow.examples.tutorials.mnist.input_data as input_data

mnist = input_data.read_data_sets("data/", one_hot=True)

'''
To classify images using a recurrent neural network, we consider every image
row as a sequence of pixels. Because MNIST image shape is 28*28px, we will then
handle 28 sequences of 28 steps for every sample.
'''

# Parameters
learning_rate=0.001
training_iters=100000
batch_size=128
display_step=10

# Network Params
n_input=28 # MNIST data input (img shape: 28*28)
n_steps=28 # timesteps
n_hidden=128 # hidden layer num of features
n_classes=10 # MNIST total classes (0-9 digits)

# tf graph input
x=tf.placeholder("float",[None,n_steps,n_input])
y=tf.placeholder("float",[None,n_classes])

# Define weights
weights={
        'out':tf.Variable(tf.random_normal([n_hidden,n_classes]))
}
biases={
        'out':tf.Variable(tf.random_normal([n_classes]))
}

def RNN(x,weights,biases):
    # Prepare data shape to match `rnn` function requirements
    # Current data input shape: (batch_size, n_steps, n_input)
    # Required shape: 'n_steps' tensors list of shape (batch_size, n_input)

    # Unstack to get a list of 'n_steps' tensors of shape (batch_size, n_input)
    x=tf.unstack(x,n_steps,1)
    # Define a lstm cell with tensorflow
    lstm_cell=rnn.BasicLSTMCell(n_hidden,forget_bias=1.0)
    # Get lstm cell output
    outputs,states=rnn.static_rnn(lstm_cell,x,dtype=tf.float32)
    # Linear activation, using rnn inner loop last output
    output=tf.matmul(outputs[-1],weights['out'])+biases['out']
    return output

pred=RNN(x,weights,biases)
cost=tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred,labels=y))
optimizer=tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)
corr=tf.equal(tf.argmax(pred,1),tf.argmax(y,1))
accuracy=tf.reduce_mean(tf.cast(corr,tf.float32))

init=tf.global_variables_initializer()
with tf.Session() as sess:
    sess.run(init)
    step=1
    while step*batch_size<training_iters:
        batch_x,batch_y=mnist.train.next_batch(batch_size)
        # Reshape data to get 28 seq of 28 elements
        batch_x=batch_x.reshape((batch_size,n_steps,n_input))
        sess.run(optimizer,feed_dict={x:batch_x,y:batch_y})
        if step%display_step==0:
            acc=sess.run(accuracy,feed_dict={x:batch_x,y:batch_y})
            loss=sess.run(cost,feed_dict={x:batch_x,y:batch_y})
            print("Iter "+str(step*batch_size)+", Minibatch Loss="+"{:.6f}".format(loss)+", Training Accuracy="+"{:.5f}".format(acc))
        step+=1
    
    # Calculate accuracy for 128 mnist test images
    test_len=128
    test_data=mnist.test.images[:test_len].reshape((-1,n_steps,n_input))
    test_label1=mnist.test.labels[:test_len]
    print("Test Accuracy:",sess.run(accuracy,feed_dict={x:test_data,y:test_label1}))