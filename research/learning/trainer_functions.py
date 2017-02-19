import numpy as np
import pandas as pd

from datetime import datetime

from gensim.models import Word2Vec

from scipy.stats import randint as sp_randint
from scipy.stats import uniform as sp_randfloat
from scipy.sparse.csr import csr_matrix

from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import RandomizedSearchCV

from keras.callbacks import EarlyStopping
from keras.models import Sequential
from keras.layers import Dense, Dropout, Merge
from keras.layers import LSTM
from keras.layers.embeddings import Embedding
from keras.layers.normalization import BatchNormalization
from keras.preprocessing.sequence import pad_sequences
from keras.wrappers.scikit_learn import KerasClassifier
from keras.optimizers import Adam, SGD

import data_functions

reload(data_functions)

# Fix until keras gets updated!!!!
import keras
import tensorflow as tf
from keras.wrappers.scikit_learn import BaseWrapper
import copy

def custom_get_params(self, **params):
    res = copy.deepcopy(self.sk_params)
    res.update({'build_fn': self.build_fn})
    return res

BaseWrapper.get_params = custom_get_params

# fix random seed for reproducibility
seed = 7
np.random.seed(seed)


def randsearch_svm(X_dict, Y, iterations, cv, rand_parameters):
    '''
    Use random search for parameter exploration for svms.
    '''
    # Variables
    out = pd.DataFrame(columns=["timestamp", "dataset", "C", "gamma", "kernel", "precision"])
    start = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    for dataset, X in X_dict.iteritems():
        print dataset
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, Y, test_size=0.3)

        # Convert to numpy array
        X_train = np.array(X_train)
        X_test = np.array(X_test)

        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        print("# Tuning hyper-parameters")
        print()

        # Run the random search
        clf = RandomizedSearchCV(SVC(C=1), param_distributions=rand_parameters,
                                       n_iter=iterations, cv=cv, verbose=1, n_jobs=8)
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

        df = pd.DataFrame(clf.cv_results_)
        df.to_csv("histories/" + now + "_history.csv")

        out = out.append({"timestamp": start, "dataset": dataset, "C": clf.best_params_["C"], "gamma": clf.best_params_["gamma"], "kernel": clf.best_params_["kernel"], "precision": clf.best_score_}, ignore_index=True)

    out.to_csv(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+"_model_comparison.csv", index=False)
    return out


def compare_ffm_settings(model, X_dict, Y, params, nb_epochs):
    '''
    compare different datasets and layer sizes using cross valdidation.
    '''
    out = pd.DataFrame(columns=["timestamp", "dataset", "params", "metric_names", "mean_metric_values"])

    print "starting fit"
    for dataset, X in X_dict.iteritems():
        print dataset
        input_l = len(X[0])

        for i, par in enumerate(params):
            par["input_size"] = input_l
            print par

            compiled_model = model(par)

            time, metric_names, metric_values, epochs = cross_validate_model(compiled_model, X, Y, 5, par["batch_size"], nb_epochs)

            out = out.append({"timestamp": time, "dataset": dataset, "params": par, "metric_names": metric_names, "mean_metric_values": metric_values}, ignore_index=True)

    out.to_csv(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+"_model_comparison.csv", index=False)
    return out

def compare_lstm_settings(model, X_dict, Y, params, nb_epochs):
    '''
    compare different datasets and layer sizes using cross valdidation.
    '''
    out = pd.DataFrame(columns=["timestamp", "dataset", "params", "metric_names", "mean_metric_values"])

    print "starting fit"
    for dataset, X in X_dict.iteritems():
        print dataset
        input_l = len(X[0])
        max_f = len(np.unique(X))
        maxlen = len(X[0])

        for i, par in enumerate(params):
            par["max_features"] = max_f
            par["maxlen"] = maxlen
            print par

            compiled_model = model(par)

            time, metric_names, metric_values, epochs = cross_validate_model(compiled_model, X, Y, 5, par["batch_size"], nb_epochs)

            out = out.append({"timestamp": time, "dataset": dataset, "params": par, "metric_names": metric_names, "mean_metric_values": metric_values}, ignore_index=True)

    out.to_csv(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+"_model_comparison.csv", index=False)
    return out

def cross_validate_model(compiled_model, X, y, folds, batch_size, nb_epochs):
    '''
    Run a nn model with cross valdiation and save the output to the histories folder.
    '''
    splits = StratifiedShuffleSplit(n_splits=folds, test_size=1./folds)
    splits.get_n_splits(X, y)

    early = EarlyStopping(monitor='val_loss', min_delta=0.0001, patience=10, verbose=0, mode='auto')

    results = []
    epochs = []

    start = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    for train_index, test_index in splits.split(X, y):
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        keras.backend.get_session().run(tf.global_variables_initializer())
        history = compiled_model.fit( X_train, y_train, batch_size=batch_size, nb_epoch=nb_epochs, verbose=0, validation_data=(X_test, y_test), callbacks=[early])

        df = pd.DataFrame(history.history)
        df.to_csv("histories/" + now + "_history.csv")

        results.append(compiled_model.evaluate(X_test, y_test, verbose=0))
        epochs.append(len(history.epoch))

    return start, compiled_model.metrics_names, np.mean(results, axis=0), np.median(epochs)

def neuralnet(model_template, X, y, w2v=None):
    '''
    Neural model playground.
    '''

    # params
    splits = StratifiedShuffleSplit(n_splits=1, test_size=0.3, random_state=1)
    in_size = len(X[0])

    batch_size = 64
    nb_epochs = 2

    # model

    # Feed forward models
    # model = model_template("adam", in_size)

    # lstm with intern embedding
    # model = model_template()

    # lstm with w2v embedding
    # load word vectors
    # print "start w2v preprocessing"

    # Convert input to index sequence
    # maxlen = 1000
    # X = data_functions.convert_to_wv_sequence(X, maxlen, w2v)
    #
    # params = {"maxlen": maxlen, "embedding_size": len(X[0][0])}
    #
    # model = model_template(params)
    # print "finished w2v preprocessing"

    maxlen = 500
    max_features = 10000
    embedding_size = 300

    params = {"batch_size": 64, "layer_size": 70, "embedding_size": embedding_size, "max_features": max_features, "maxlen": maxlen}

    model = model_template(params)
    X = data_functions.convert_to_index_sequence(X, max_features, maxlen)

    for train_index, test_index in splits.split(X, y):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        keras.backend.get_session().run(tf.global_variables_initializer())

        early = EarlyStopping(monitor='val_loss', min_delta=0.0001, patience=10, verbose=1, mode='auto')

        history = model.fit(X_train, y_train, batch_size=batch_size, nb_epoch=nb_epochs, validation_data=(X_test, y_test), verbose=1 , callbacks=[])

        test_scores = model.evaluate(X_test, y_test, verbose=1)

        print ()
        print "Test Results"
        print test_scores

    return model, history


def ensemblenet(model_template, X, Y):
    '''
    Neural model playground.
    '''

    # Split data beforehand
    # X_train, X_test, y_train, y_test = train_test_split(
    #     X, Y, test_size=0.33, random_state=seed)
    #
    # X_train = np.array(X_train)
    # X_test = np.array(X_test)

    # params
    batch_size = 20
    nb_epochs = 50

    model = model_template("adam")
    keras.backend.get_session().run(tf.global_variables_initializer())

    early = EarlyStopping(monitor='val_loss', min_delta=0.001, patience=5, verbose=1, mode='auto')

    history = model.fit(X, Y, batch_size=batch_size, nb_epoch=nb_epochs, verbose=1 , callbacks=[], validation_split=0.3)

    # test_scores = model.evaluate(X_test, y_test, verbose=1)
    #
    # print ()
    # print "Test Results"
    # print test_scores

    return model, history
