''' Class which converts raw text into embeddings. '''

import spacy
import numpy as np
from textblob import TextBlob

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

from scipy.sparse import csr_matrix, hstack

from scope.methods.semantics import stopwords


def HAL(docs, window_size=5):
    '''
        Creating HAL space out of the text documents.

        docs = document list
        window_size: window size

        returns: HAL embedding
    '''

    col = []
    data = []
    row = []

    vocabulary = {}

    for text in docs:
        blob = TextBlob(text)

        toks = blob.words

        for ind in range(0, len(toks)):
            row_index = vocabulary.setdefault(toks[ind], len(vocabulary))

            # looking backwards
            for i in range(-window_size + ind, ind):
                if i >= 0:
                    term = toks[i]
                    value = i - ind + window_size + 1

                    index = vocabulary.setdefault(term, len(vocabulary))

                    col.append(row_index)
                    row.append(index)
                    data.append(value)

            # looking forward
            for i in range(ind+1, ind+window_size+1):
                if i < len(toks):
                    term = toks[i]
                    value = abs(i - window_size - ind - 1)

                    index = vocabulary.setdefault(term, len(vocabulary))

                    row.append(row_index)
                    col.append(index)
                    data.append(value)

    # Create sparse matrices
    csr_forward = csr_matrix((data, (row, col)), shape=(len(vocabulary), len(vocabulary)), dtype=float)
    csr_backward = csr_forward.transpose()

    hal = hstack((csr_backward, csr_forward))

    # Divide by 2 to normalize stacking after stacking
    hal = hal.multiply(0.5)

    # Normalize to [0,1]
    max_value = 1/hal.max()
    hal = hal.multiply(max_value)

    return hal, vocabulary




class Embedding():
    """Create word embeddings."""
    def __init__(self, lang, model, articles):
        '''
            lang: Spacy language string (en, de, ...)
        '''

        self.lang = lang
        self.vecs = []
        self.sim = []

        if lang == "en":
            self.stopwords = stopwords.EN
        else:
            raise Exception("Language not known.")

        if model == "grammar_svd":
            self._create_grammer_svd_embeddings(articles)
        else:
            raise Exception("Model not known.")

    def _create_grammer_svd_embeddings(self, articles):
        '''
            Creates an SVD embedding.

            articles: List of Article objects

            return: Embedding vectors
        '''

        clean_text = self._gammar_based_preprocessing(articles)

        self._create_svd_embedding(clean_text)

    def _gammar_based_preprocessing(self, articles):
        '''
            Grammar based text extraction using spacy.

            articles: list of article objects
        '''

        nlp = spacy.load(self.lang)

        # Convert text to spacy object
        docs = [nlp(a.body) for a in articles]

        clean = []

        for doc in docs:
            temp = []

            for sent in doc.sents:
                for t in sent:
                    # This version performs also very good
                    # if t.tag_.find("NN") >= 0:
                    if t.tag_.find("NN") >= 0 or t.dep_.find("comp") >= 0:
                        temp.append(t.lemma_)

            clean.append(" ".join(temp))

        return clean

    def _create_svd_embedding(self, clean_text):
        vectorizer = TfidfVectorizer(
            sublinear_tf=True, stop_words=self.stopwords, strip_accents="unicode")
        tfidf = vectorizer.fit_transform(clean_text)

        # similarities
        self.vecs = TruncatedSVD(n_components=18).fit_transform(tfidf)
        self.sim = cosine_similarity(self.vecs)

    def get_similarity_matrix(self):
        ''' Get the similarity matrix '''
        return self.sim

    def get_embedding_vectors(self):
        ''' Get the embedding vectors. '''
        return self.vecs
