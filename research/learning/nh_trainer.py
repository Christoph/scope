'''
NH classifier script
'''

import numpy as np
import pandas as pd
import spacy

from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.layers.normalization import BatchNormalization

from sklearn.model_selection import train_test_split


# fix random seed for reproducibility
seed = 7
np.random.seed(seed)


def load_data():
    '''
    Load data for the test function
    '''

    # Hand labeled statistics
    # is_tech [1]: 46
    # not tech [0]: 469
    # needed additional tech articles: 423

    data_hand = pd.read_csv("tech_hand_labeled.csv")
    data_tech = pd.read_csv("tech_er_423.csv")

    data = pd.concat([data_hand, data_tech])

    # Convert data to word vectors and splits columns
    pipeline = spacy.load("en")

    X = [pipeline(t.decode("utf-8")).vector for t in data["text"]]
    Y = data["label"].as_matrix()

    return X, Y

'''
input - 300(uniform, relu) - 1(uniform, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 99.84%
test_acc: 84.19%

input - 300(normal, relu) - 1(normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 99.84%
test_acc: 84.52%

input - 300(normal, relu) - 1(normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 99.89%
test_acc: 83.23%

input - 300(glorot_normal, relu) - 1(glorot_normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 99.84%
test_acc: 83.55%

input - 300(he_normal, relu) - 1(he_normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 99.84%
test_acc: 83.55%

BEST INIT: normal

input - 300(normal, tanh) - 1(normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 99.04%
test_acc: 80.97%

input - 300(normal, hard_sigmoid) - 1(normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 92.83%
test_acc: 83.87%

BEST ACTIVATION: relu

input - 300(normal, relu) - 1(normal, sigmoid)
loss: binary_crossentropy
optimizer: adagrad
train_acc: 95.86%
test_acc: 82.90%

input - 300(normal, relu) - 1(normal, sigmoid)
loss: binary_crossentropy
optimizer: RMSprop
train_acc: 99.68%
test_acc: 84.19%

BEST OPT: adam

Using [0,1] normalized input!
input - 300(normal, relu) - 1(normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 50.8.84%
test_acc: 48.39%

input - 300(normal, relu) - Dropout(0.2) - 1(normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 99.84%
test_acc: 83.55%

input - 300(normal, relu) - Dropout(0.5) - 1(normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 99.36%
test_acc: 85.48%

input - dense(300, normal, relu) - BatchNormalization() - Dropout(0.5) -
dense(1, normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: XX%
test_acc: XX%

input -
dense(300, normal, relu) - Dropout(0.5) -
dense(300, normal, relu) - Dropout(0.5) -
dense(1, normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 97.13%
test_acc: 84.19%

input -
dense(300, normal, relu) - Dropout(0.5) -
dense(300, normal, relu) - Dropout(0.5) -
dense(300, normal, relu) - Dropout(0.5) -
dense(1, normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 96.97%
test_acc: 83.55%

input -
dense(300, normal, relu) - Dropout(0.5) -
dense(200, normal, relu) - Dropout(0.4) -
dense(100, normal, relu) - Dropout(0.3) -
dense(1, normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 97.29%
test_acc: 82.90%

BEST STRUCTURE: 1 layer + dropout 0.5

input - 200(normal, relu) - Dropout(0.5) - 1(normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 98.89%
test_acc: 84.84%

input - 600(normal, relu) - Dropout(0.5) - 1(normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 99.52%
test_acc: 84.52%

BEST LAYER SIZE: 600

batch size: 100
input - 600(normal, relu) - Dropout(0.5) - 1(normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 96.02%
test_acc: 85.48%

batch size: 40
input - 600(normal, relu) - Dropout(0.5) - 1(normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 98.57%
test_acc: 85.48%

batch size: 5
input - 600(normal, relu) - Dropout(0.5) - 1(normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 99.04%
test_acc: 83.55%

BEST BATCH SIZE: 20

nb_epochs: 200
batch size: 20
input - 600(normal, relu) - Dropout(0.5) - 1(normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 100.00%
test_acc: 84.52%

nb_epochs: 200
batch size: 20
input - 300(normal, relu) - Dropout(0.5) - 1(normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 99.68%
test_acc: 83.55%

BEST OVERALL: has lowest cost function values

nb_epochs: 300
batch size: 20
input - 600(normal, relu) - Dropout(0.5) - 1(normal, sigmoid)
loss: binary_crossentropy
optimizer: adam
train_acc: 99.84.00%
test_acc: 84.19%

'''


def test_architecture(X, Y):
    '''
    Architecture test class.
    '''

    # Split data beforehand
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.33, random_state=seed)

    X_train = np.array(X_train)
    X_test = np.array(X_test)

    # baseline model
    test = Sequential()

    test.add(Dense(600, init='normal', activation='relu', input_dim=300))
    # test.add(BatchNormalization())
    test.add(Dropout(0.5))

    test.add(Dense(1, init='normal', activation='sigmoid'))
    test.compile(
        loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    test_history = test.fit(
        X_train, y_train, batch_size=20, nb_epoch=300, verbose=1)

    test_scores = test.evaluate(X_test, y_test, verbose=0)

    print "Result"
    print "Training Accuracy: %.2f%%" % (test_history.history["acc"][-1] * 100)
    print "Test %s: %.2f%%" % (test.metrics_names[1], test_scores[1] * 100)

    # predictions = model.predict_classes(X_test, verbose=0)
    # result = np.vstack((predictions[:, 0], y_test))
    # print "Comparrison"
    # print result.T

    return test
