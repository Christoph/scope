'''
NH classifier script
'''

import numpy as np
import pandas as pd
import spacy

from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split


# fix random seed for reproducibility
seed = 7
np.random.seed(seed)

# load dataset


# Hand labeled statistics
# is_tech [1]: 46
# not tech [0]: 469
# needed additional tech articles: 423

data_hand = pd.read_csv("tech_hand_labeled.csv")
data_tech = pd.read_csv("tech_er_423.csv")

data = pd.concat([data_hand, data_tech])

# Convert data to word vectors and splits columns
pipeline = spacy.load("en")

X = [pipeline(t.decode("utf-8")).vector for t in data["text"]]
Y = data["label"].as_matrix()

# baseline model
model = Sequential()
model.add(Dense(300, init='uniform', activation='relu', input_dim=300))
model.add(Dense(1, init='uniform', activation='sigmoid'))
model.compile(
    loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Split data beforehand
X_train, X_test, y_train, y_test = train_test_split(
    X, Y, test_size=0.33, random_state=seed)

X_train = np.array(X_train)
X_test = np.array(X_test)

# Fit in keras means train
# batch_size is the nuber of evaluations before the weight matrix gets updated
# epochs is the total number of training runs
history = model.fit(X_train, y_train, batch_size=10, nb_epoch=100, verbose=1)

# Evaluate the model on a new dataset. Until that, use train dataset
scores = model.evaluate(X_test, y_test, verbose=0)

print "Output"
print "Training Accuracy: %.2f%%" % (history.history["acc"][-1] * 100)
print "Test %s: %.2f%%" % (model.metrics_names[1], scores[1] * 100)

# predictions = model.predict_classes(X_test, verbose=0)
# result = np.vstack((predictions[:, 0], y_test))
# print "Comparrison"
# print result.T
