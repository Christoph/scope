import numpy as np
import pandas
from keras.models import Sequential
from keras.layers import Dense
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

class nh_classifier(object):
    """The tech classifier for NH."""
    def __init__(self, pipeline):
        # Spacy pipeline
        self.pipeline = pipeline

        # Create model
        self.model = Sequential()
        # First hidden layer
        self.model.add(Dense(100, init='uniform', activation='relu', input_dim=300))
        # Output layer
        self.model.add(Dense(1, init='uniform', activation='sigmoid'))
        # Compile the model using TF
        self.model.compile(
            loss='binary_crossentropy',
            optimizer='adam',
            metrics=['accuracy'])

        # Load weights
        self.model.load_weights("weights.h5")

    def classify(self, db_articles):
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
        labels = np.zeros(len(db_articles))

        docs = [self.pipeline(item.body) for item in db_articles]

        vecs = [doc.vector for doc in docs]

        labels = self.model.predict_classes(np.array(vecs))

        return labels
