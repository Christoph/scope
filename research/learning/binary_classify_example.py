import numpy
import pandas
from keras.models import Sequential
from keras.layers import Dense
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split


# fix random seed for reproducibility
seed = 7
numpy.random.seed(seed)

y = product(a, b)

# load dataset
dataframe = pandas.read_csv("last24h/static/commerz/sonar.csv", header=None)
dataset = dataframe.values

# split into input (X) and output (Y) variables
X = dataset[:, 0:60].astype(float)
Y = dataset[:, 60]

# encode class values as integers
encoder = LabelEncoder()
encoder.fit(Y)
encoded_Y = encoder.transform(Y)

# baseline model

model = Sequential()
# First hidden layer
model.add(Dense(100, init='uniform', activation='relu', input_dim=60))
# Output layer
model.add(Dense(1, init='uniform', activation='sigmoid'))
# Compile the model using TF
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Split data beforehand
X_train, X_test, y_train, y_test = train_test_split(X, encoded_Y, test_size=0.33, random_state=seed)

# Fit in keras means train
# batch_size is the nuber of evaluations before the weight matrix gets updated
# epochs is the total number of training runs
model.fit(X_train, y_train, batch_size=10, nb_epoch=150, verbose=0)

# Evaluate the model on a new dataset. in this case the training data -> very bad!
scores = model.evaluate(X_test, y_test, verbose=0)
predictions = model.predict_classes(X_test, verbose=0)

print "Output"
print("%s: %.2f%%" % (model.metrics_names[1], scores[1] * 100))

result = numpy.vstack((predictions[:, 0], y_test))

print "Comparrison"
print result.T
