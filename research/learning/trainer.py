import os

from trainer_functions import *
from models import *
from data_functions import *

from scipy.stats import randint as sp_randint
from scipy.stats import uniform as sp_randfloat

# Create directory for run histories
directory = "histories"
if not os.path.exists(directory):
    os.makedirs(directory)

T, C, F, Y = load_data("datasets/train_small.csv")
WC, WF, WR = get_vectors(T, F, C)

# NN
datasets_wv = {
    "wv_clean": V,
    "wv_full_text": W,  # Vector averaging
    "wv_text": X
}

layers_wv = [200, 250, 300]
layers_other = [30, 60, 150, 200]

# SVM params
rand_parameters = {
       "C": sp_randint(1, 10000),
       "gamma": sp_randfloat(1e-1, 1e-5),
       "kernel": ["linear", "poly", "rbf", "sigmoid"]}

# out = compare_datasets_layers(single_layer_cv, datasets_wv, Y, layers_wv, 100)

for i, val in enumerate([50, 100, 200, 300]):
    TC = get_tfidf(D, val, 0.90)
    TR = get_tfidf(T, val, 0.90)
    TF = get_tfidf(F, val, 0.90)

    datasets_other = {
        "tfidf_raw": TR,
        "tfidf_clean": TC,
        "tfidf_full": TF,
    }

    # Computations
    out = compare_datasets_layers(single_layer_cv, datasets_other, Y, layers_other, 100)
    # out = randsearch_svm(datasets_other, Y, 20, 5, rand_parameters)
