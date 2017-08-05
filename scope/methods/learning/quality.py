import numpy as np
import pandas as pd
from scope.methods.semantics import document_embedding
from sklearn.ensemble import RandomForestClassifier


class QualityManager():
    """Creates a binary classifier by loading the model and weights."""

    def classify(self, articles, bad_articles, nlp):

        total_data = []
        total_data.extend(articles)
        total_data.extend(bad_articles)

        data_model = document_embedding.Embedding("de", nlp, "grammar_svd", total_data)

        X = data_model.get_embedding_vectors()
        y = np.zeros(len(X))

        y[len(bad_articles):] = 1

        clf = RandomForestClassifier(100)
        return clf.fit(X, y)

    def find_similar(self, articles, bad_articles, nlp):
        '''
        Classify articles.
        '''

        total_data = []
        total_data.extend(articles)
        total_data.extend(bad_articles)

        data_model = document_embedding.Embedding("de", nlp, "grammar_svd", total_data)

        sim = data_model.get_similarity_matrix()

        sub = sim[0:len(articles), len(articles):] > 0.99

        for i in range(0, len(articles)):
            if True in sub[i, :]:
                print(i)
