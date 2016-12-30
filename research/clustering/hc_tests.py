import numpy as np
import json
from django.core import serializers

from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances

from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster.hierarchy import cophenet
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import fcluster


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

'''
        Test different metrics for hierachical clustering

metric_list = ["ward", "single", "complete", "average", "centroid", "median", "weighted"]
metric_test = compare_metrics_hc(nvecs, metric_list)
metric_test_links = [t[0] for t in metric_test]

# plt.plot_compare_dendrogram(60, metric_test_links, metric_list)

        Test different distance methods for a metric

distance_list = ['euclidean', 'cosine', 'minkowski', 'cityblock',
    'seuclidean', 'sqeuclidean']
distance_test = compare_distances_hc_distance(nvecs, "weighted", distance_list, "maxclust", 10)
distance_test_links = [t[0] for t in distance_test]

# plt.plot_compare_dendrogram(20, distance_test_links, distance_list)

        Test different threshold for a metric distance pairwise_distances

threshold_list = range(6,18)
threshold_test = compare_distances_hc_clustering(nvecs, "weighted", "sqeuclidean", "maxclust", threshold_list)
threshold_test_clustering = [t[1] for t in threshold_test]

# plt.plot_compare_clustering(nvecs, threshold_test_clustering, threshold_list)
'''
