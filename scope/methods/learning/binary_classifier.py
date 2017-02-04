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
        self.name = customer_key

        # Load model
        self.model = load_model(
            "curate/customers/" + customer_key + "/" + customer_key + "_model.h5")

        # Load weights
        self.model.load_weights(
            "curate/customers/" + customer_key + "/" + customer_key + "_weights.h5")

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

    def update_model(self, train, positive):
        '''
        Update the model with new input.
        '''

        print "update"
        print train
        print positive

        X = []
        y = []

        # Prepare data
        if len(train) <= len(positive):
            for i in range(0, len(train)):
                X.append(self.pipeline(train[i].body).vector)
                y.append(0)
                X.append(self.pipeline(positive[i]).vector)
                y.append(1)
        elif len(train) > len(positive):
            for i in range(0, len(train)):
                X.append(self.pipeline(train[i].body).vector)
                y.append(0)
            for i in range(0, len(positive)):
                X.append(self.pipeline(positive[i]).vector)
                y.append(1)

        self.model.fit(np.array(X), y, batch_size=1, verbose=0)

        # Save updated model
        self.model.save(
            "curate/customers/"+self.name+"/"+self.name+"_model.h5")
        self.model.save_weights(
            "curate/customers/"+self.name+"/"+self.name+"_weights.h5")

        print self.name + " model updated."

    def classify_by_count(self, db_articles, min_count):
        '''
        Classify articles and get at least min_count many
        '''

        classified_articles = []
        best = 0.0

        if len(db_articles) <= min_count:
            print "not enough articles"
        else:
            lo = 0.0
            hi = 1.0
            found = False
            count = 0
            count_old = 0

            while lo<=hi and not found:
                best = (lo + hi)/2

                count_old = count
                count = self._get_count(db_articles, best)

                print best
                print count

                if count == count_old or count == min_count:
	                   found = True
                else:
                    if count > min_count:
                        lo = best
                    else:
                        hi = best

        print "Used threshold"
        print best

        # Classify articles
        for article in db_articles:
            data = article.body
            doc = self.pipeline(data)

            # Predict class
            cl = self.model.predict(
                doc.vector.reshape(1, 300), verbose=0)

            if cl >= best:
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
