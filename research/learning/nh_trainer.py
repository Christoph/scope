import numpy as np
import pandas as pd
import spacy

from keras.models import Sequential
from keras.layers import Dense
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split


# fix random seed for reproducibility
seed = 7
np.random.seed(seed)

# load dataset
use_data = pd.read_csv("research/use_nh.csv", header=None, encoding="utf-8")
mis_data = pd.read_csv("research/mis_nh.csv", header=None, encoding="utf-8")

# Convert data to word vectors
pipeline = spacy.load("en")

use_docs = [pipeline(item) for item in use_data[0]]
mis_docs = [pipeline(item) for item in mis_data[0]]

use_vecs = [doc.vector for doc in use_docs]
mis_vecs = [doc.vector for doc in mis_docs]

# split into input (X) and output (Y) variables
use_vecs.extend(mis_vecs)
X = np.array(use_vecs)

use_labels = np.zeros(len(use_docs)) + 1
use_labels = use_labels.astype(int)
mis_labels = np.zeros(len(mis_docs))
mis_labels = mis_labels.astype(int)

Y = np.append(use_labels, mis_labels)

# baseline model
model = Sequential()
# First hidden layer
model.add(Dense(300, init='uniform', activation='relu', input_dim=300))
# Output layer
model.add(Dense(1, init='uniform', activation='sigmoid'))
# Compile the model using TF
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Split data beforehand
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.33, random_state=seed)

# Fit in keras means train
# batch_size is the nuber of evaluations before the weight matrix gets updated
# epochs is the total number of training runs
model.fit(np.array(X_train), np.array(y_train), batch_size=10, nb_epoch=150, verbose=1)

# Evaluate the model on a new dataset. in this case the training data -> very bad!
scores = model.evaluate(X_test, y_test, verbose=0)
predictions = model.predict_classes(X_test, verbose=0)

print "Output"
print("%s: %.2f%%" % (model.metrics_names[1], scores[1] * 100))

result = np.vstack((predictions[:, 0], y_test))

print "Comparrison"
print result.T

model.save_weights("weights.h5")
print "Model saved to weights.h5"
