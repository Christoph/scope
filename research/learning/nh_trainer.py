'''
NH classifier script
'''

import numpy as np
import pandas as pd
import spacy
from gensim import corpora, models

from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.layers import LSTM
from keras.layers.embeddings import Embedding
from keras.layers.normalization import BatchNormalization
from keras.preprocessing.sequence import pad_sequences

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

    # Prepare for TF-IDF
    texts = [pipeline(t.decode("utf-8")) for t in data["text"]]

    word_vectors = []
    for doc in texts:
        word_vectors.append([tok.lemma_ for tok in doc if
                             (tok.is_digit or tok.is_alpha) and not tok.is_stop])

    texts_clean = [u" ".join(vec) for vec in word_vectors]

    # dictionary = corpora.Dictionary(word_vectors)
    # corpus = [dictionary.doc2bow(vec) for vec in word_vectors]
    #
    # tfidf_model = models.TfidfModel(corpus)
    # tfidf = tfidf_model[corpus]
    #
    # padded_tfidf = pad_sequences(tfidf, dtype='float32')
    #
    # U = padded_tfidf
    V = [pipeline(t).vector for t in texts_clean]
    W = [pipeline(t.decode("utf-8")).vector for t in data["title"]]
    X = [pipeline(t.decode("utf-8")).vector for t in data["text"]]
    Y = data["label"].as_matrix()

    return V, W, X, Y

def load_data_sequence():
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

    # Prepare for TF-IDF
    texts = [pipeline(t.decode("utf-8")) for t in data["text"]]

    word_vectors = []
    for doc in texts:
        word_vectors.append([tok.lemma_ for tok in doc if
                             (tok.is_digit or tok.is_alpha)])

    dictionary = corpora.Dictionary(word_vectors)

    # dictionary.filter_extremes(no_below=5)
    dictionary.compactify()

    # +1 to free up 0 as non-informativity token
    indices = [[dictionary.token2id[word] + 1 for word in vec] for vec in word_vectors]

    vfunc = np.vectorize(len)

    # X = pad_sequences(indices, maxlen=np.max(vfunc(indices)))
    X = pad_sequences(indices, truncating='post', maxlen=1000)
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
train_acc: 99.84%
test_acc: 84.19%

'''

def test_sequence_architecture(X, Y, nb_epochs):
    '''
    Architecture test class.
    '''

    input_size = len(X[0])
    vocab_size = np.max(X) + 1

    # Split data beforehand
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.33, random_state=seed)

    X_train = np.array(X_train)
    X_test = np.array(X_test)

    # baseline model
    model = Sequential()

    model.add(Embedding(vocab_size, 32, input_length=input_size))
    model.add(LSTM(100))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    test_history = model.fit(
        X_train, y_train, batch_size=64, nb_epoch=nb_epochs, verbose=1)

    test_scores = model.evaluate(X_test, y_test, verbose=0)

    print "Result"
    print "Training Accuracy: %.2f%%" % (test_history.history["acc"][-1] * 100)
    print "Test %s: %.2f%%" % (model.metrics_names[1], test_scores[1] * 100)

    # predictions = model.predict_classes(X_test, verbose=0)
    # result = np.vstack((predictions[:, 0], y_test))
    # print "Comparrison"
    # print result.T

    return model


def test_architecture(X, Y, nb_epochs):
    '''
    Architecture test class.
    '''

    input_size = len(X[0])

    # Split data beforehand
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.33, random_state=seed)

    X_train = np.array(X_train)
    X_test = np.array(X_test)

    # baseline model
    test = Sequential()

    test.add(Dense(600, init='normal', activation='relu', input_dim=input_size))
    # test.add(BatchNormalization())
    test.add(Dropout(0.5))

    test.add(Dense(1, init='normal', activation='sigmoid'))
    test.compile(
        loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    test_history = test.fit(
        X_train, y_train, batch_size=20, nb_epoch=nb_epochs, verbose=1)

    test_scores = test.evaluate(X_test, y_test, verbose=0)

    print "Result"
    print "Training Accuracy: %.2f%%" % (test_history.history["acc"][-1] * 100)
    print "Test %s: %.2f%%" % (test.metrics_names[1], test_scores[1] * 100)

    # predictions = model.predict_classes(X_test, verbose=0)
    # result = np.vstack((predictions[:, 0], y_test))
    # print "Comparrison"
    # print result.T

    return test
