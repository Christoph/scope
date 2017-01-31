'''
NH classifier script
'''

import numpy as np
import pandas as pd
import spacy
from gensim import corpora, models

import keras
import tensorflow as tf

from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.layers import LSTM
from keras.layers.embeddings import Embedding
from keras.layers.normalization import BatchNormalization
from keras.preprocessing.sequence import pad_sequences
from keras.wrappers.scikit_learn import KerasClassifier

from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_score


# fix random seed for reproducibility
seed = 7
np.random.seed(seed)


def load_data(filename):
    '''
    Load data for the test function
    '''

    data = pd.read_csv(filename)

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
    W = [pipeline(t.decode("utf-8")).vector for t in data["title"].astype(str)]
    X = [pipeline(t.decode("utf-8")).vector for t in data["text"]]
    Y = data["label"].as_matrix()

    return V, W, X, Y

def load_data_sequence(filename):
    '''
    Load data for the test function
    '''

    # Hand labeled statistics
    # is_tech [1]: 46
    # not tech [0]: 469
    # needed additional tech articles: 423

    data = pd.read_csv(filename)

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

def test_neural_model(model, X, Y):
    test_scores = model.evaluate(X, Y, verbose=1)

    print "Test Results"
    print "Test %s: %.2f%%" % (model.metrics_names[1], test_scores[1] * 100)

    predictions = model.predict_classes(X_test, verbose=0)
    result = np.vstack((predictions[:, 0], y_test))
    print "Comparrison"
    print result.T

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

def train_svm(X, Y):
    input_size = len(X[0])
    vocab_size = np.max(X) + 1

    # Split data beforehand
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.33, random_state=seed)

    X_train = np.array(X_train)
    X_test = np.array(X_test)

    tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4],
                     'C': [1, 10, 100, 1000]},
                    {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]

    scores = ['precision', 'recall']

    for score in scores:
        print("# Tuning hyper-parameters for %s" % score)
        print()

        clf = GridSearchCV(SVC(C=1), tuned_parameters, cv=5,
                           scoring='%s_macro' % score)
        clf.fit(X_train, y_train)

        print("Best parameters set found on development set:")
        print()
        print(clf.best_params_)
        print()
        print("Grid scores on development set:")
        print()
        means = clf.cv_results_['mean_test_score']
        stds = clf.cv_results_['std_test_score']
        for mean, std, params in zip(means, stds, clf.cv_results_['params']):
            print("%0.3f (+/-%0.03f) for %r"
                  % (mean, std * 2, params))
        print()

        print("Detailed classification report:")
        print()
        print("The model is trained on the full development set.")
        print("The scores are computed on the full evaluation set.")
        print()
        y_true, y_pred = y_test, clf.predict(X_test)
        print(classification_report(y_true, y_pred))
        print()

    # model
    # clf = svm.SVC(kernel='rbf', gamma=0.7, C=1).fit(X_train, y_train)
    #
    # # evaluate
    # test_scores = clf.score(X_test, y_test)
    #
    # print "Result"
    # print "Test Accuracy:"
    # print test_scores

def get_model_stats(X, Y):
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

    return model

def lstm_model(optimizer='adam', init='normal', vocab_size=1000):
    # vocab_size = np.max(X) + 1
    # baseline model
    model = Sequential()

    model.add(Embedding(vocab_size, 32, input_length=input_size))
    model.add(LSTM(100))
    model.add(Dense(1, activation='sigmoid'))

def three_layer_model(optimizer='adam', init='normal'):
    model = Sequential()

    model.add(Dense(50, init=init, activation='relu', input_dim=input_size))
    model.add(BatchNormalization())
    model.add(Dense(250, init=init, activation='relu', input_dim=input_size))
    model.add(BatchNormalization())
    model.add(Dense(10, init=init, activation='relu', input_dim=input_size))
    model.add(Dropout(0.5))
    model.add(Dense(1, init=init, activation='sigmoid'))

    model.compile(
        loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    return model

def single_layer_model(optimizer='adam', init='normal'):
    # baseline model
    model = Sequential()

    model.add(Dense(10, init=init, activation='relu', input_dim=300))
    # test.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(1, init=init, activation='sigmoid'))

    model.compile(
        loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    return model

def gridsearch_model(X, Y):
    '''
    Architecture test class using grid search.
    '''

    model = KerasClassifier(build_fn=single_layer_model, verbose=1)

    optimizers = ['rmsprop', 'adam']
    init = ['glorot_uniform', 'normal']
    epochs = [5, 10, 15]
    batches = [5, 10, 20]

    param_grid = dict(optimizer=optimizers, nb_epoch=epochs, batch_size=batches, init=init)

    grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=-1)

    keras.backend.get_session().run(tf.global_variables_initializer())

    grid_result = grid.fit(np.array(X), Y)

    # summarize results
    print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
    means = grid_result.cv_results_['mean_test_score']
    stds = grid_result.cv_results_['std_test_score']
    params = grid_result.cv_results_['params']
    for mean, stdev, param in zip(means, stds, params):
    	print("%f (%f) with: %r" % (mean, stdev, param))

    return model

def kfold_model(X, Y):
    '''
    Architecture test class using kfold cross validation.
    '''

    # Split data beforehand
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.33, random_state=seed)

    X_train = np.array(X_train)
    X_test = np.array(X_test)

    model = KerasClassifier(build_fn=basic_neural_net, nb_epoch=10, batch_size=20, verbose=0)

    keras.backend.get_session().run(tf.global_variables_initializer())

    # evaluate using 10-fold cross validation
    kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    results = cross_val_score(model, np.array(X), np.array(Y), cv=kfold)

    print "Mean Accuracy:"
    print(results.mean())

    return model
