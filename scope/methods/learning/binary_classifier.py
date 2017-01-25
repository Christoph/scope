'''
Binary classifier class.
'''

import numpy as np
from keras.models import load_model
import pandas as pd


class binary_classifier(object):
    """Creates a binary classifier by loading the model and weights."""

    def __init__(self, pipeline, customer_key):
        # Spacy pipeline
        self.pipeline = pipeline

        # Load model
        self.model = load_model(
            "curate/customers/" + customer_key + "_model.h5")

        # Load weights
        self.model.load_weights(
            "curate/customers/" + customer_key + "_weights.h5")

    def classify(self, db_articles):
        '''
        Classify articles.
        '''

        classified_articles = []
        not_articles = []

        # Classify articles
        for article in db_articles:
            data = article.body
            doc = self.pipeline(data)

            # Predict class
            cl = self.model.predict_classes(
                doc.vector.reshape(1, 300), verbose=0)

            if cl == 1:
                classified_articles.append(article)
            else:
                not_articles.append(article)

        return classified_articles

    def classify_by_count(self, db_articles, min_count):
        '''
        Classify articles and get at least min_count many
        '''

        classified_articles = []
        good = 1.0
        counter = 0

        while counter < min_count:
            good = good - 0.05

            counter = self._get_count(db_articles, good)

            print "Classified articles"
            print good
            print counter

        # Classify articles
        for article in db_articles:
            data = article.body
            doc = self.pipeline(data)

            # Predict class
            cl = self.model.predict(
                doc.vector.reshape(1, 300), verbose=0)

            if cl >= good:
                classified_articles.append(article)

        return classified_articles

    def _get_count(self, db_articles, threshold):
        counter = 0

        # Classify articles
        for article in db_articles:
            data = article.body
            doc = self.pipeline(data)

            # Predict class
            cl = self.model.predict(
                doc.vector.reshape(1, 300), verbose=0)

            if cl >= threshold:
                counter = counter + 1

        return counter

    def classify_labels(self, db_articles, save_text):
        '''
        Classify articles and output a labels vector.
        save_text saves the classification as clustering.csv
        '''

        # labels = np.zeros(len(db_articles))

        docs = [self.pipeline(item.body) for item in db_articles]

        vecs = [doc.vector for doc in docs]

        labels = self.model.predict_classes(np.array(vecs))

        if save_text:
            titles = [item.title.replace("\"", "") for item in db_articles]
            texts = [item.body.replace("\"", "").replace("\n", "")
                     for item in db_articles]
            labels_out = [item for item in labels]

            df = pd.DataFrame(
                np.transpose(
                    [labels_out,
                     titles,
                     texts]),
                columns=["label", "title", "text"])

            df.to_csv("clustering.csv", index=False)

            return df
        else:
            return labels
