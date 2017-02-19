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

params_wv = [
    {"batch_size": 20, "layer_size": 300, "dropout": 0.3},
    {"batch_size": 20, "layer_size": 250, "dropout": 0.3},
    {"batch_size": 20, "layer_size": 200, "dropout": 0.3}
]

params_other = [
    {"batch_size": 20, "layer_size": 50, "dropout": 0.3}
    {"batch_size": 20, "layer_size": 100, "dropout": 0.3}
    {"batch_size": 20, "layer_size": 200, "dropout": 0.3}
    {"batch_size": 20, "layer_size": 250, "dropout": 0.3}
    {"batch_size": 20, "layer_size": 300, "dropout": 0.3}
]

out = compare_params_settings(single_layer_cv, datasets_wv, Y, params_wv, 100)

for i, val in enumerate([50, 100, 200, 300]):
    TC = get_tfidf(C, val, 0.90)
    TT = get_tfidf(T, val, 0.90)
    TF = get_tfidf(F, val, 0.90)

    datasets_other = {
        "tfidf_raw": TT,
        "tfidf_clean": TC,
        "tfidf_full": TF,
    }

    # Computations
    out = compare_ffn_settings(
        single_layer_cv, datasets_other, Y, params_other, 100)
