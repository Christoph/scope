from keras.models import Sequential
from keras.layers import Dense, Dropout, Merge, Activation
from keras.layers import LSTM, GRU
from keras.layers import Convolution1D, MaxPooling1D
from keras.layers.embeddings import Embedding
from keras.layers.normalization import BatchNormalization
from keras.wrappers.scikit_learn import KerasClassifier

from keras import backend as K
from keras.engine.topology import Layer

import numpy as np

class Attention(Layer):
    def __init__(self, **kwargs):
        """
        Attention operation for temporal data.
        # Input shape
            3D tensor with shape: `(samples, steps, features)`.
        # Output shape
            2D tensor with shape: `(samples, features)`.
        :param kwargs:
        """
        self.supports_masking = False
        self.init = initializations.get('glorot_uniform')
        super(Attention, self).__init__(**kwargs)

    def build(self, input_shape):
        assert len(input_shape) == 3
        self.W = self.init((input_shape[-1],), name='{}_W'.format(self.name))
        self.b = K.ones((input_shape[1],), name='{}_b'.format(self.name))
        self.trainable_weights = [self.W, self.b]

        super(Attention, self).build(input_shape)

    def call(self, x, mask=None):
        eij = K.tanh(K.dot(x, self.W) + self.b)
        ai = K.exp(eij)
        weights = ai / K.sum(ai, axis=1).dimshuffle(0, 'x')
        # weights = ai / K.sum(ai, axis=1).expand_dims(x, 1)
        weighted_input = x * weights.dimshuffle(0, 1, 'x')
        return weighted_input.sum(axis=1)

    def get_output_shape_for(self, input_shape):
        return input_shape[0], input_shape[-1]

def lstm_model():
    # Embedding
    max_features = 5000
    maxlen = 1000
    embedding_size = 128

    # Convolution
    filter_length = 5
    nb_filter = 64
    pool_length = 4

    # LSTM
    lstm_output_size = 70

    model = Sequential()
    model.add(Embedding(
        max_features, embedding_size, input_length=maxlen))
    model.add(Dropout(0.25))
    model.add(Convolution1D(nb_filter=nb_filter,
                            filter_length=filter_length,
                            border_mode='valid',
                            activation='relu',
                            subsample_length=1))
    model.add(MaxPooling1D(pool_length=pool_length))
    model.add(LSTM(lstm_output_size))
    model.add(Dense(lstm_output_size, activation='relu'))
    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    return model


def lstm_embedding_model(params):
    '''
    LSTM model which takes as input an embedded sequence.

    PARAMS
    maxlen: length of the sequences
    embedding_size: embedding dimension
    '''
    # Convolution
    filter_length = 5
    nb_filter = 64
    pool_length = 4

    # LSTM
    lstm_output_size = 70

    model = Sequential()
    model.add(Convolution1D(input_shape=(params["maxlen"], params["embedding_size"]),
                            nb_filter=nb_filter,
                            filter_length=filter_length,
                            border_mode='valid',
                            activation='relu',
                            subsample_length=1))
    model.add(MaxPooling1D(pool_length=pool_length))

    model.add(LSTM(lstm_output_size, return_sequences=True))
    model.add(LSTM(lstm_output_size, return_sequences=True))
    model.add(LSTM(lstm_output_size))

    model.add(Dense(lstm_output_size, activation='relu'))
    model.add(Dropout(0.25))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    return model

def three_lstm_wv_model(params):

    # LSTM
    lstm_output_size = params["layer_size"]

    model = Sequential()
    model.add(LSTM(lstm_output_size, return_sequences=True, input_shape=(params["maxlen"], params["embedding_size"])))
    model.add(LSTM(lstm_output_size, return_sequences=True))
    model.add(LSTM(lstm_output_size))
    model.add(Dense(lstm_output_size, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    return model

def three_lstm_model(params):
    # Embedding
    max_features = params["max_features"]
    maxlen = params["maxlen"]
    embedding_size = params["embedding_size"]

    # LSTM
    lstm_output_size = params["layer_size"]

    model = Sequential()
    model.add(Embedding(max_features, embedding_size, input_length=maxlen))
    model.add(Dropout(0.25))
    model.add(LSTM(lstm_output_size, return_sequences=True))
    model.add(LSTM(lstm_output_size, return_sequences=True))
    model.add(LSTM(lstm_output_size))
    model.add(Dense(lstm_output_size, activation='relu'))
    model.add(Dropout(0.25))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    return model


def huge_lstm_model(params):
    # Other params
    # nb_epochs: 4
    # batch_size: 64

    max_features = params["max_features"]
    maxlen = params["maxlen"]
    embedding_size = params["embedding_size"]

    # Convolution 1
    filter_length_1 = 5
    nb_filter_1 = 64
    pool_length_1 = 4

    # LSTM
    lstm_output_size = params["layer_size"]



    model = Sequential()
    model.add(Embedding(
        max_features, embedding_size, input_length=maxlen))
    model.add(Dropout(0.25))

    model.add(Convolution1D(nb_filter=nb_filter_1,
                            filter_length=filter_length_1,
                            border_mode='valid',
                            activation='relu',
                            subsample_length=1))
    model.add(MaxPooling1D(pool_length=pool_length_1))

    model.add(LSTM(lstm_output_size, return_sequences=True))
    model.add(LSTM(lstm_output_size, return_sequences=True))
    model.add(LSTM(lstm_output_size))

    model.add(Dense(lstm_output_size, activation='relu'))
    model.add(Dropout(0.25))
    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    return model


def ensemble_model(optimizer):
    text_branch = Sequential()
    text_branch.add(Dense(200, input_dim=300))
    text_branch.add(Activation("relu"))

    tfidf_branch = Sequential()
    tfidf_branch.add(Dense(200, input_dim=100))
    tfidf_branch.add(Activation("relu"))

    merged = Merge([text_branch, tfidf_branch], mode='concat')

    model = Sequential()
    model.add(merged)
    model.add(Dropout(0.3))
    model.add(Dense(300))
    model.add(Activation("relu"))
    model.add(Dropout(0.3))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(
        loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    return model


def bottle_neck_model(optimizer='adam', init='normal'):
    model = Sequential()

    model.add(Dense(150, init=init, activation='relu', input_dim=input_size))
    model.add(BatchNormalization())
    model.add(Dense(20, init=init, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1, init=init, activation='sigmoid'))

    model.compile(
        loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    return model


def single_layer_model(optimizer, in_size):

    # optimizer='adam'
    init = 'normal'

    # baseline model
    model = Sequential()

    model.add(Dense(200, init=init, activation='relu', input_dim=in_size))
    # model.add(BatchNormalization())
    model.add(Dropout(0.3))
    model.add(Dense(1, init=init, activation='sigmoid'))

    model.compile(
        loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    return model


def single_layer_cv(input_size, params):
    '''
    1 layer model.

    PARAMS
    input_size: size of the input layer
    layer_size: size of the hidden layer
    dropout: dropout value
    '''

    optimizer = "adam"
    init = 'normal'
    # baseline model
    model = Sequential()

    model.add(Dense(params["layer_size"], init=init,
                    activation='relu', input_dim=params["input_size"]))
    # test.add(BatchNormalization())
    model.add(Dropout(params["dropout"]))
    model.add(Dense(1, init=init, activation='sigmoid'))

    model.compile(
        loss='binary_crossentropy', optimizer=optimizer, metrics=['binary_accuracy', 'precision', 'recall'])

    return model


def single_layer_basic_model():
    optimizer = 'adam'
    init = 'normal'
    # baseline model
    model = Sequential()

    model.add(Dense(150, init=init, activation='relu', input_dim=300))
    # test.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(1, init=init, activation='sigmoid'))

    model.compile(
        loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    return model
