from trainer_functions import *
from models import *

D, V, W, X, Y = load_data("train_small.csv")
NC, NT, NB, SC, ST, SB, counts, bi_tfidf = get_tfidf(D, 20)

datasets = {
    "ww_clean": V,
    "ww_title": W,
    "ww_text": X,
    "nmf_tfidf": NT,
    "nmf_count": NC,
    "nmf_bi_tfidf": NB,
    "svd_tfidf": ST,
    "svd_count": SC,
    "svd_bi_tfidf": SB
}

layers = [10,20,50,100,150,200]

epochs = [50, 100, 150]

out = compare_models_using_kfold(single_layer_cv, datasets, Y, layers, epochs)
