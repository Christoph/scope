import numpy as np
import json
from django.core import serializers

from scope.methods.graphs import clustering_methods

params_simbased = [[0.001, 0.05, 0.001],
                    {"coverage_weight": 0.1, "max_clust_weight": 0.9}]

#  DATA FOR CUSTOM CLUSTERING
def test_labels(labels, params):
    selected = len(labels) - np.sum(labels != 0)

    if selected == 0:
        coverage = 1.
    else:
        coverage = float(selected)/len(labels)

    max_clust = len(np.unique(labels))

    return params["coverage_weight"] * coverage + params["max_clust_weight"] * max_clust

# Helper
def get_article_cluster(articles, labels):
    out = []
    elements = np.unique(labels)

    for element in elements:
        out.append(articles[np.where(labels == element)[0]])

    return out


def get_labels(sim, vecs):
    labels_sim = clustering_methods.sim_based_test(
        sim, params_simbased, test_labels)
    labels_aff, centers_aff = clustering_methods.affinity_propagation(sim)
    links_hc, labels_hc = clustering_methods.hierarchical_clustering(vecs, "ward", "euclidean", "maxclust", 12)
    labels_dbscan = clustering_methods.db_scan(sim, threshold=0.3, metric="euclidean", algorithm="auto")
    labels_km, centers_km = clustering_methods.k_means(vecs, 16)
    labels_gmm = clustering_methods.gauss_mix(vecs, 16)
    labels_gmmt = clustering_methods.gauss_mix_test(vecs, [10, 20, 1])
    labels_bgmm = clustering_methods.bayes_gauss_mix(vecs, 0.01)

    return {"l_sim": labels_sim, "l_aff": labels_aff,
            "l_hc": labels_hc, "l_db": labels_dbscan,
            "l_km": labels_km, "l_gmm": labels_gmm,
            "l_bgmm": labels_bgmm, "l_gmmt": labels_gmmt}
