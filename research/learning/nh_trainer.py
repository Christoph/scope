'''
NH classifier script
'''

import numpy as np
import pandas as pd
import spacy

import keras
import tensorflow as tf

from keras.models import Sequential
from keras.layers import Dense, Dropout, Merge
from keras.layers import LSTM
from keras.layers.embeddings import Embedding
from keras.layers.normalization import BatchNormalization
from keras.preprocessing.sequence import pad_sequences
from keras.wrappers.scikit_learn import KerasClassifier

from scipy.stats import randint as sp_randint
from scipy.stats import uniform as sp_randfloat

from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RandomizedSearchCV


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

def gridsearch_svm(X, Y):
    # Split data beforehand
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.5, random_state=seed)

    X_train = np.array(X_train)
    X_test = np.array(X_test)

    rand_parameters = {
               "C": sp_randint(1, 10000),
               "gamma": sp_randfloat(1e-2, 1e-5),
               "kernel": ["rbf"]}

    print("# Tuning hyper-parameters")
    print()

    clf = RandomizedSearchCV(SVC(C=1), param_distributions=rand_parameters,
                                   n_iter=10, cv=5, verbose=1, n_jobs=-1)
    clf.fit(X_train, y_train)


    print("Best: %f using %s" % (clf.best_score_, clf.best_params_))
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

    return clf.best_params_

def train_svm(X, Y, kernel, gamma, C):
    # Split data beforehand
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.5, random_state=seed)

    X_train = np.array(X_train)
    X_test = np.array(X_test)

    # train
    clf = SVC(kernel=kernel, gamma=gamma, C=C).fit(X_train, y_train)

    # evaluate
    test_scores = clf.score(X_test, y_test)

    print "Result"
    print "Test Accuracy:"
    print test_scores

    return clf

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

def single_layer_basic_model():
    optimizer='adam'
    init='normal'
    # baseline model
    model = Sequential()

    model.add(Dense(10, init=init, activation='relu', input_dim=300))
    # test.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(1, init=init, activation='sigmoid'))

    model.compile(
        loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    return model

def gridsearch_neuralnet(X, Y):
    '''
    Architecture test class using grid search.
    '''

    model = KerasClassifier(build_fn=single_layer_model, verbose=0)

    # optimizers = ['rmsprop', 'adam']
    # init = ['glorot_uniform', 'normal']
    # epochs = [10]
    # batches = [10]
    #
    # param_grid = dict(optimizer=optimizers, nb_epoch=epochs, batch_size=batches, init=init)

    batch_size = [10, 20, 40]
    epochs = [10, 20, 30]
    optimizer = ['SGD', 'RMSprop', 'Adagrad', 'Adadelta', 'Adam', 'Adamax', 'Nadam']

    # for SGD
    learn_rate = [0.001, 0.01, 0.1, 0.2, 0.3]
    momentum = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9]

    activation = ['softmax', 'softplus', 'softsign', 'relu', 'tanh', 'sigmoid', 'hard_sigmoid', 'linear']


    init_mode = ['uniform', 'lecun_uniform', 'normal', 'zero', 'glorot_normal', 'glorot_uniform', 'he_normal', 'he_uniform']


    param_grid = dict(batch_size=batch_size, nb_epoch=epochs)

    grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=-1, verbose=1, cv=None)

    keras.backend.get_session().run(tf.global_variables_initializer())

    grid_result = grid.fit(np.array(X), Y)

    # summarize results
    print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
    means = grid_result.cv_results_['mean_test_score']
    stds = grid_result.cv_results_['std_test_score']
    params = grid_result.cv_results_['params']
    for mean, stdev, param in zip(means, stds, params):
    	print("%f (%f) with: %r" % (mean, stdev, param))

    return model, {"score": grid_result.best_score_, "params": grid_result.best_params_}

def kfold_neuralnet(X, Y, nb_epoch, batch_size):
    '''
    Architecture test class using kfold cross validation.
    '''

    # Split data beforehand
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.33, random_state=seed)

    X_train = np.array(X_train)
    X_test = np.array(X_test)

    model = KerasClassifier(build_fn=single_layer_model, nb_epoch=nb_epoch, batch_size=batch_size, verbose=0)

    keras.backend.get_session().run(tf.global_variables_initializer())

    # evaluate using 10-fold cross validation
    kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=seed)
    results = cross_val_score(model, np.array(X), np.array(Y), cv=kfold)

    print " "
    print "Mean Accuracy:"
    print(results.mean())

def train_neuralnet(X, Y):
    '''
    Train neural model.
    '''

    # Split data beforehand
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.33, random_state=seed)

    X_train = np.array(X_train)
    X_test = np.array(X_test)

    # params
    batch_size = 20
    nb_epochs = 200

    init = "normal"
    optimizer = "adam"

    # baseline model
    model = Sequential()

    model.add(Dense(300, init=init, activation='relu', input_dim=300))
    # model.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(1, init=init, activation='sigmoid'))

    model.compile(
        loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    model.fit( X_train, y_train, batch_size=batch_size, nb_epoch=nb_epochs, verbose=1)

    # title_branch = Sequential()
    # title_branch.add(Dense(100, input_dim=300))
    #
    # text_branch = Sequential()
    # text_branch.add(Dense(100, input_dim=300))
    #
    # merged = Merge([title_branch, text_branch], mode='concat')
    #
    # model = Sequential()
    # model.add(merged)
    # model.add(Dropout(0.5))
    # model.add(Dense(1, activation='sigmoid'))
    #
    # model.compile(
    #     loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])
    #
    # keras.backend.get_session().run(tf.global_variables_initializer())
    #
    # model.fit([W_train, X_train], y_train, batch_size=batch_size, nb_epoch=nb_epochs, verbose=1)


    test_scores = model.evaluate(X_test, y_test, verbose=1)

    print ()
    print "Test Results"
    print "Test %s: %.2f%%" % (model.metrics_names[1], test_scores[1] * 100)

    return model
