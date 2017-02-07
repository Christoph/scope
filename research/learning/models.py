def lstm_model(optimizer='adam', init='normal', vocab_size=1000):
    # vocab_size = np.max(X) + 1
    # baseline model
    model = Sequential()

    model.add(Embedding(vocab_size, 32, input_length=input_size))
    model.add(LSTM(100))
    model.add(Dense(1, activation='sigmoid'))

def ensemble_model():
    title_branch = Sequential()
    title_branch.add(Dense(100, input_dim=300))

    text_branch = Sequential()
    text_branch.add(Dense(100, input_dim=300))

    merged = Merge([title_branch, text_branch], mode='concat')

    model = Sequential()
    model.add(merged)
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(
        loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    return model

def three_layer_model(optimizer='adam', init='normal'):
    model = Sequential()

    model.add(Dense(150, init=init, activation='relu', input_dim=input_size))
    model.add(BatchNormalization())
    model.add(Dense(20, init=init, activation='relu', input_dim=input_size))
    model.add(Dropout(0.5))
    model.add(Dense(1, init=init, activation='sigmoid'))

    model.compile(
        loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    return model

def single_layer_model(layer_size):

    optimizer='adam'
    init='normal'

    # baseline model
    model = Sequential()

    model.add(Dense(layer_size, init=init, activation='relu', input_dim=300))
    # test.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(1, init=init, activation='sigmoid'))

    model.compile(
        loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    return model

def single_layer_cv(input_size = 300, layer_size = 150):
    optimizer='adam'
    init='normal'
    # baseline model
    model = Sequential()

    model.add(Dense(layer_size, init=init, activation='relu', input_dim=input_size))
    # test.add(BatchNormalization())
    model.add(Dropout(0.3))
    model.add(Dense(1, init=init, activation='sigmoid'))

    model.compile(
        loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    return model

def single_layer_basic_model():
    optimizer='adam'
    init='normal'
    # baseline model
    model = Sequential()

    model.add(Dense(150, init=init, activation='relu', input_dim=300))
    # test.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(1, init=init, activation='sigmoid'))

    model.compile(
        loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    return model
