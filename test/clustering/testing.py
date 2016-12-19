import django
django.setup()

import numpy as np
import json
from django.core import serializers

from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances

from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster.hierarchy import cophenet
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import fcluster

from scope.models import Article

import scope.methods.semantics.word_vector as word_vector
from scope.methods.graphs import clustering_methods
from test.clustering import cluster_plot as plt

wv = word_vector.Model("en")

# Helper functions
def normalize_vecs(vecs):
    min_v = np.min(vecs)
    max_v = np.max(vecs)

    out = (vecs-min_v)/(max_v - min_v)

    return out

# Get data from json
with open('test/clustering/articles.json', 'r') as stream:
    data = json.load(stream)

articles = []
for obj in serializers.deserialize("json", data):
    articles.append(obj.object)

# Get semantic informations
wv.load_data(articles)
vecs = wv.document_vectors()
nvecs = normalize_vecs(vecs)
sim = wv.similarity_matrix()

def test_labels(labels, params):
    selected = len(labels) - np.sum(labels == np.max(labels))
    if selected == 0:
        coverage = 1
    else:
        coverage = selected/len(labels)
    max_clust = np.max(np.bincount(labels.astype(int)))
    return params["coverage_weight"] * coverage + params["max_clust_weight"] * max_clust


params = [[0.001, 0.05, 0.001], {"coverage_weight": 1, "max_clust_weight": 1}]

# clustering helper
def compare_metrics_hc(data, metric_list):
    out = []
    for m in metric_list:
        out.append(clustering_methods.hierarchical_clustering(data, m, "euclidean", "distance", 1))
    return out

def compare_distances_hc_distance(data, metric, distance_list, cluster_criterion, cluster_threshold):
    out = []
    for d in distance_list:
        out.append(clustering_methods.hierarchical_clustering(data, metric, d, cluster_criterion, cluster_threshold))
    return out

def compare_distances_hc_clustering(data, metric, distance, cluster_criterion, cluster_threshold_list):
    out = []
    for t in cluster_threshold_list:
        out.append(clustering_methods.hierarchical_clustering(data, metric, distance, cluster_criterion, t))
    return out


# Generate test data
metric_list = ["ward", "single", "complete", "average", "centroid", "median", "weighted"]
metric_test = compare_metrics_hc(nvecs, metric_list)
metric_test_links = [t[0] for t in metric_test]

# plt.plot_compare_dendrogram(60, metric_test_links, metric_list)

distance_list = ['euclidean', 'cosine', 'minkowski', 'cityblock',
    'seuclidean', 'sqeuclidean']
distance_test = compare_distances_hc_distance(nvecs, "weighted", distance_list, "maxclust", 10)
distance_test_links = [t[0] for t in distance_test]

# plt.plot_compare_dendrogram(20, distance_test_links, distance_list)

threshold_list = range(6,18)
threshold_test = compare_distances_hc_clustering(nvecs, "weighted", "sqeuclidean", "maxclust", threshold_list)
threshold_test_clustering = [t[1] for t in threshold_test]

# plt.plot_compare_clustering(nvecs, threshold_test_clustering, threshold_list)
