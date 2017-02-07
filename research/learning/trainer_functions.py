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
from scipy.sparse.csr import csr_matrix

from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedKFold, StratifiedShuffleSplit
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RandomizedSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer
from sklearn.decomposition import NMF, TruncatedSVD

import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

# Fix until keras get updated!!!!
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

    D = texts_clean
    V = np.array([pipeline(t).vector for t in texts_clean])
    W = np.array([pipeline(t.decode("utf-8")).vector for t in data["title"].astype(str)])
    X = np.array([pipeline(t.decode("utf-8")).vector for t in data["text"]])
    Y = data["label"].as_matrix()

    return D, V, W, X, Y



def get_tfidf(data, dim):
    counts = CountVectorizer(max_df=0.95, min_df=2, ngram_range=(1,2)).fit_transform(data)
    transformer = TfidfTransformer()
    bi_tfidf =transformer.fit_transform(counts)

    vectorizer = TfidfVectorizer(
        sublinear_tf=True, min_df=5, max_df=0.95)
    tfidf = vectorizer.fit_transform(data)

    nmf_count = NMF(
        n_components=dim, random_state=1, alpha=.1, l1_ratio=.5).fit_transform(counts)

    nmf_tfidf = NMF(
        n_components=dim, random_state=1, alpha=.1, l1_ratio=.5).fit_transform(tfidf)

    nmf_bi_tfidf = NMF(
        n_components=dim, random_state=1, alpha=.1, l1_ratio=.5).fit_transform(bi_tfidf)

    svd_tfidf = TruncatedSVD(n_components=dim, random_state=1).fit_transform(tfidf)

    svd_count = TruncatedSVD(n_components=dim, random_state=1).fit_transform(counts)

    svd_bi_tfidf = TruncatedSVD(n_components=dim, random_state=1).fit_transform(bi_tfidf)

    NT = nmf_tfidf
    NC = nmf_count
    NB = nmf_bi_tfidf
    ST = svd_tfidf
    SB = svd_bi_tfidf
    SC = svd_count

    return NC, NT, NB, SC, ST, SB, counts, bi_tfidf


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

def compare_models_using_kfold(model, X_dict, Y, layers, nb_epochs):
    out = pd.DataFrame(columns=["dataset", "mean_precision", "mean_loss"])

    print "starting fit"
    for dataset, X in X_dict.iteritems():
        print dataset
        input = len(X[0])
        for i, layer in enumerate(layers):
            print layer
            compiled_model = model(input, layer)
            for j, epoch in enumerate(nb_epochs):
                print epoch
                pre, loss = cross_validate_model(compiled_model, X, Y, 5, 20, epoch)

                out.append({"dataset": dataset, "mean_precision": pre, "mean_loss": loss})

    out.to_csv("model_comparison.csv", index=False)
    return out

def cross_validate_model(compiled_model, X, y, folds, batch_size, nb_epochs):
    splits = StratifiedShuffleSplit(n_splits=folds, test_size=1./folds)
    splits.get_n_splits(X, y)

    means = []
    losses = []

    for train_index, test_index in splits.split(X, y):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        compiled_model.fit( X_train, y_train, batch_size=batch_size, nb_epoch=nb_epochs, verbose=0)

        test_scores = compiled_model.evaluate(X_test, y_test, verbose=0)
        print test_scores
        means.append(test_scores[1] * 100)
        losses.append(test_scores[0])

    return np.array(means).mean(), np.array(losses).mean()


def neuralnet(X, Y):
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
    nb_epochs = 100

    init = "normal"
    optimizer = "adam"

    # baseline model
    model = Sequential()

    model.add(Dense(150, init=init, activation='relu', input_dim=300))
    model.add(BatchNormalization())
    # model.add(Dropout(0.5))
    model.add(Dense(1, init=init, activation='sigmoid'))

    model.compile(
        loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    model.fit( X_train, y_train, batch_size=batch_size, nb_epoch=nb_epochs, verbose=1)

    test_scores = model.evaluate(X_test, y_test, verbose=1)

    print ()
    print "Test Results"
    print test_scores

    return model
