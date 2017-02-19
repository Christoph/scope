import os

from trainer_functions import *
from models import *
from data_functions import *

from scipy.stats import randint as sp_randint
from scipy.stats import uniform as sp_randfloat

from gensim.models import Word2Vec

# Create directory for run histories
directory = "histories"
if not os.path.exists(directory):
    os.makedirs(directory)

T, C, F, L, Y = load_data("datasets/train_small.csv")
# Load W2V model
model = Word2Vec.load_word2vec_format('datasets/GoogleNews-vectors-negative300.bin', binary=True)

# Finallize model to reduce memory usage on my notebook
model.init_sims(replace=True)

A = convert_to_index_sequence(T, 5000, 500)
B = convert_to_index_sequence(T, 10000, 500)
C = convert_to_index_sequence(T, 20000, 500)
D = convert_to_index_sequence(T, 5000, 1000)
E = convert_to_index_sequence(T, 10000, 1000)
F = convert_to_index_sequence(T, 20000, 1000)
G = convert_to_index_sequence(T, 5000, 2000)
H = convert_to_index_sequence(T, 10000, 2000)
J = convert_to_index_sequence(T, 20000, 2000)

K = convert_to_wv_sequence(T, 500, model)
L = convert_to_wv_sequence(T, 1000, model)
M = convert_to_wv_sequence(T, 2000, model)

datasets_other = {
    "tfidf_5000_500": A,
    "tfidf_10000_500": B,
    "tfidf_20000_500": C,
    "tfidf_5000_1000": D,
    "tfidf_10000_1000": E,
    "tfidf_20000_1000": F,
    "tfidf_5000_2000": G,
    "tfidf_10000_2000": H,
    "tfidf_20000_2000": J
}

datasets_wv = {
    "wv_500": K,
    "wv_1000": L,
    "wv_2000": M
}

params_three_lstm = [
    {"batch_size": 64, "layer_size": 70, "embedding_size": 100},
    {"batch_size": 64, "layer_size": 70, "embedding_size": 200},
    {"batch_size": 64, "layer_size": 70, "embedding_size": 300},
    {"batch_size": 64, "layer_size": 35, "embedding_size": 100},
    {"batch_size": 64, "layer_size": 35, "embedding_size": 200},
    {"batch_size": 64, "layer_size": 35, "embedding_size": 300},
    {"batch_size": 64, "layer_size": 140, "embedding_size": 100},
    {"batch_size": 64, "layer_size": 140, "embedding_size": 200},
    {"batch_size": 64, "layer_size": 140, "embedding_size": 300}
]

params_three_wv_lstm = [
    {"batch_size": 64, "layer_size": 70, "embedding_size": 300},
    {"batch_size": 64, "layer_size": 35, "embedding_size": 300},
    {"batch_size": 64, "layer_size": 140, "embedding_size": 300}
]

# Computations
compare_lstm_settings(
    three_lstm_model, datasets_other, Y, params_three_lstm, 3)

compare_lstm_settings(
    three_lstm_wv_model, datasets_wv, Y, params_three_wv_lstm, 3)
