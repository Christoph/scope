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

T, C, F, L, Y = load_data("datasets/train_small.csv")
WC = get_vectors(C)
WF = get_vectors(F)
WT = get_vectors(T)
WL = get_vectors(L)

# NN
datasets_wv = {
    "wv_clean": WC,  # Vector averaging
    "wv_full_text": WF,
    "wv_text": WT,
    "wv_lem": WL
}

layers_wv = [200, 250, 300]
layers_other = [30, 60, 150, 200]

# SVM params
rand_parameters = {
       "C": sp_randint(1, 10000),
       "gamma": sp_randfloat(1e-1, 1e-5),
       "kernel": ["linear", "poly", "rbf", "sigmoid"]}

out = randsearch_svm(datasets_wv, Y, 20, 5, rand_parameters)

for i, val in enumerate([50, 100, 200, 300]):
    TC = get_tfidf(C, val, 0.90)
    TR = get_tfidf(T, val, 0.90)
    TF = get_tfidf(F, val, 0.90)

    datasets_other = {
        "tfidf_raw": TR,
        "tfidf_clean": TC,
        "tfidf_full": TF,
    }

    out = randsearch_svm(datasets_other, Y, 20, 5, rand_parameters)
