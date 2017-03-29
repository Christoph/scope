import numpy as np
import pandas as pd
import spacy

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
from keras.preprocessing.sequence import pad_sequences
from gensim.models import Word2Vec
from keras.preprocessing.text import text_to_word_sequence

import sys
reload(sys)
sys.setdefaultencoding('UTF8')

pipeline = spacy.load("en")


def load_data(filename):
    '''
    Load data for the test function
    '''

    data = pd.read_csv(filename)

    # Prepare for TF-IDF
    raw = [t.decode("utf-8") for t in data["text"]]
    texts_titles = []
    for row in data.iterrows():
        texts_titles.append(row[1]["title"] + " " + row[1]["text"])

    texts = [pipeline(t) for t in raw]
    texts_titles_docs = [pipeline(t.decode("utf-8")) for t in texts_titles]

    word_vectors = []
    for doc in texts:
        word_vectors.append([tok.lemma_ for tok in doc if
                            (tok.is_alpha) and not tok.is_stop])

    word_vectors_lemma = []
    for doc in texts:
        word_vectors_lemma.append([tok.lemma_ for tok in doc if tok.is_alpha])


    texts_clean = [u" ".join(vec) for vec in word_vectors]
    texts_lemma = [u" ".join(vec) for vec in word_vectors_lemma]

    word_vectors_full = []
    for doc in texts_titles_docs:
        word_vectors_full.append([tok.text for tok in doc if tok.is_alpha])

    texts_full = [u" ".join(vec) for vec in word_vectors_full]

    T = raw  # Raw text without touching
    C = texts_clean  # Lemmatized text without stopword and numbers
    F = texts_full  # Raw text and title without numbers
    L = texts_lemma  # Lemmatized text without numbers
    Y = data["label"].as_matrix()  # Labels

    return T, C, F, L, Y


def get_vector(X):
    '''
    Load data for the test function
    '''

    # Convert data to word vectors and splits columns
    W = np.array([pipeline(t).vector for t in X])

    n = Normalizer()

    return n.fit_transform(W)


def get_tfidf(D, dim, max_df):
    '''
    Transform clean text into tfidf embedding.
    '''
    vectorizer = TfidfVectorizer(
        sublinear_tf=True, max_df=max_df, stop_words="english")

    tfidf = vectorizer.fit_transform(D)

    svd_tfidf = TruncatedSVD(
        n_components=dim, random_state=1).fit_transform(tfidf)

    return svd_tfidf


def get_bigrams(D, dim, max_df):
    '''
    Transform clean text into word embeddings.
    '''
    bi = CountVectorizer(
        max_df=max_df, ngram_range=(2, 2)).fit_transform(D)

    svd_bi = TruncatedSVD(n_components=dim).fit_transform(bi)

    return svd_bi


def convert_to_index_sequence(X, max_features, maxlen):
    '''
    Transform text into sequence datasets
    '''

    # Prepare for TF-IDF
    texts = [pipeline(t) for t in X]

    word_vectors = []
    for doc in texts:
        word_vectors.append([tok.lemma_ for tok in doc if
                             (tok.is_alpha)])
        #  (tok.is_digit or tok.is_alpha)])

    texts_clean = [u" ".join(vec) for vec in word_vectors]

    # words = CountVectorizer(stop_words="english")
    # words.fit(texts_clean)

    # Get top tfidf words
    vectorizer = TfidfVectorizer(
        sublinear_tf=True, stop_words="english", max_df=0.90)
    temp = vectorizer.fit_transform(texts_clean)
    features = vectorizer.get_feature_names()

    vocab = get_top_words(features, temp, max_features-1)

    # Replace bad words wit zeros
    tfidf_clean = []
    for vec in word_vectors:
        temp = []
        for t in vec:
            if t in vocab:
                temp.append(vocab.get(t))
            else:
                temp.append("0")
        tfidf_clean.append(temp)

    TS = pad_sequences(tfidf_clean, maxlen=maxlen, padding='post', truncating='post')

    return TS


def convert_to_wv_sequence(X, maxlen, model):
    '''
    Transform text into sequence datasets
    '''

    # Get sequences
    sequences = []

    for t in X:
        sequences.append(text_to_word_sequence(t.encode("utf-8")))

    # Create embedding matrix
    # shape: (nb_samples, sequence_length, output_dim)
    embedding_matrix = np.zeros((len(sequences), maxlen, model.layer1_size))

    not_list = set()

    for i, seq in enumerate(sequences):
        for j in range(0, min(500, len(seq))):
            try:
                embedding_matrix[i][j] = model[seq[j]]
            except KeyError:
                not_list.add(seq[j])


    print "Not known words:"
    print len(not_list)
    print not_list

    EM = embedding_matrix

    return EM


def get_top_words(features, Xtransformed, top_n, min_tfidf=0.0):
    D = Xtransformed.toarray()

    D[D < min_tfidf] = 0
    tfidf_means = np.mean(D, axis=0)

    topn_ids = np.argsort(tfidf_means)[::-1][:top_n]
    top_feats = [(features[i], tfidf_means[i]) for i in topn_ids]

    out = {}
    for i, x in enumerate(top_feats, start=1):
        out.update({x[0]: str(i)})

    return out


def analyse_top_mean_tfidf_feats(X, y, top_n, max_df, min_tfidf=0.0):
    vectorizer = TfidfVectorizer(
        sublinear_tf=True, stop_words="english", max_df=max_df)
    Xtransformed = vectorizer.fit_transform(X)
    features = vectorizer.get_feature_names()

    dfs = pd.DataFrame()
    labels = np.unique(y)
    for label in labels:
        ids = np.where(y == label)

        D = Xtransformed[ids].toarray()

        D[D < min_tfidf] = 0
        tfidf_means = np.mean(D, axis=0)

        topn_ids = np.argsort(tfidf_means)[::-1][:top_n]
        top_feats = [(features[i], tfidf_means[i]) for i in topn_ids]

        feats_df = pd.DataFrame(top_feats)
        feats_df.columns = [label, 'tfidf']

        dfs = pd.concat([dfs, feats_df], axis=1)

    return dfs
