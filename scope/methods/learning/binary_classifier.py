'''
Binary classifier class.
'''

import numpy as np
from keras.models import load_model


class nh_classifier(object):
    """The tech classifier for NH."""
    def __init__(self, pipeline, customer_key):
        # Spacy pipeline
        self.pipeline = pipeline

        # Load model
        self.model = load_model(
            "curate/customers/"+customer_key+"_model.h5")

        # Load weights
        self.model.load_weights(
            "curate/customers/"+customer_key+"_weights.h5")

    def classify(self, db_articles):
        '''
        Classify articles.
        '''

        classified_articles = []

        # Classify articles
        for article in db_articles:
            data = article.body
            doc = self.pipeline(data)

            # Predict class
            cl = self.model.predict_classes(
                doc.vector.reshape(1, 300), verbose=0)

            if cl == 1:
                classified_articles.append(article)

        return classified_articles

    def classify_labels(self, db_articles):
        '''
        Classify articles and output a labels vector.
        '''

        labels = np.zeros(len(db_articles))

        docs = [self.pipeline(item.body) for item in db_articles]

        vecs = [doc.vector for doc in docs]

        labels = self.model.predict_classes(np.array(vecs))

        return labels
