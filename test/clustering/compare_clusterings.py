import numpy as np
import json
from django.core import serializers

from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances

from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster.hierarchy import cophenet
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import fcluster

from scope.methods.graphs import clustering_methods

#  DATA FOR CUSTOM CLUSTERING
def test_labels(labels, params):
    selected = len(labels) - np.sum(labels == np.max(labels))
    if selected == 0:
        coverage = 1
    else:
        coverage = selected/len(labels)
    max_clust = np.max(np.bincount(labels.astype(int)))
    return params["coverage_weight"] * coverage + params["max_clust_weight"] * max_clust


params_simbased = [[0.001, 0.05, 0.001], {"coverage_weight": 1, "max_clust_weight": 1}]

def get_labels(sim, vecs):
    labels_sim = clustering_methods.sim_based_test(sim, params_simbased, test_labels)
    labels_aff, centers_aff = clustering_methods.affinity_propagation(sim)
    links_hc, labels_hc = clustering_methods.hierarchical_clustering(vecs, "ward", "euclidean", "maxclust", 12)
    labels_dbscan = clustering_methods.db_scan(sim, threshold=0.3, metric="euclidean", algorithm="auto")

    return {"l_sim": labels_sim, "l_aff": labels_aff, "l_hc":labels_hc, "l_db": labels_dbscan}
