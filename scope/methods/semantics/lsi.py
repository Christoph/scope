import gensim
import nltk
import numpy as np
from sklearn import preprocessing


class Model(object):
    """docstring for Model."""
    def __init__(self):
        self.index2 = []
        self.lsi_model2 = []
        self.corp = []
        self.scaler = preprocessing.MinMaxScaler()

    def compute(self, term_vecs, n2):
        # Convert term vectors into gensim dictionary
        dict2 = gensim.corpora.Dictionary(term_vecs)

        for i in range(0, len(term_vecs)):
            self.corp.append(dict2.doc2bow(term_vecs[i]))

        #  Create TFIDF vectors based on term vectors bag-of-word corpora
        tfidf_model = gensim.models.TfidfModel(self.corp)
        corpus_tfidf = tfidf_model[self.corp]

        # Lsi Models
        self.lsi_model2 = gensim.models.LsiModel(corpus_tfidf, id2word=dict2, num_topics=n2)
        corpus_lsi2 = self.lsi_model2[corpus_tfidf]

        #  Create pairwise document similarity index
        self.index2 = gensim.similarities.SparseMatrixSimilarity(corpus_lsi2, num_features=n2)

        # Save models and data
        # gensim.corpora.MmCorpus.serialize('last24h/static/commerz/vw.mm', corp)
        # dict2.save('last24h/static/commerz/vw.dict')
        # self.lsi_model2.save('last24h/static/commerz/vw.lsi')
        # self.index2.save('last24h/static/commerz/vw.index')

    def similarity(self):
        sim = np.zeros((len(self.corp), len(self.corp)))
        for i in range(0, len(self.corp)):
            sim = np.insert(
                sim, i, self.index2[self.lsi_model2[self.corp[i]]], axis=1)

        scaled = self.scaler.fit_transform(sim)

        return scaled
