from sklearn.cluster import AffinityPropagation, DBSCAN
from sklearn.cluster import KMeans

from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster.hierarchy import cophenet
from scipy.cluster.hierarchy import fcluster

from scipy.spatial.distance import pdist

import numpy as np
from collections import defaultdict

# Subspace clustering due to curse of dimensionality?
# Maybe PCS like method before clustering?


def sim_based_threshold(sim, threshold):
    '''
        Custom clustering method.
    '''

    graph = defaultdict(list)
    edges = set()
    labels = np.zeros(len(sim))

    # Creates lower diag distance matrix
    con = np.tril(1. - sim, -1)
    con[con == 0] = 1

    # Create adjacency list
    for i, v in enumerate(con, 1):
        for j, u in enumerate(v, 1):
            if u <= threshold and frozenset([i, j]) not in edges:
                edges.add(frozenset([i, j]))
                graph[i].append(j)

    # Resolve adjacency list
    for key in graph.keys():
        group = graph[key]
        if labels[key-1] != 0:
            label = labels[key-1]
        else:
            label = key
        labels[key-1] = label
        for e in group:
            labels[e-1] = label

    # Add group for all non grouped elements
    labels[labels == 0] = np.max(labels)+1

    return labels.astype(int)

def sim_based_test(sim, params, test):
    '''
        Custom clustering method using a test method.
    '''

    best_score = 0
    out_labels = []

    for s in np.arange(params[0][0], params[0][1], params[0][2]):
        # Get labels with threshold
        labels = sim_based_threshold(sim, s)

        score_new = test(labels, params[1])

        if score_new > best_score:
            best_score = score_new
            out_labels = labels

    return out_labels

def affinity_propagation(sim):
    '''
        sim: similarity matrix
        preference: influences the number of clusters

        returns: labels, center_indices
    '''
    aff = AffinityPropagation(affinity="precomputed")

    aff.fit_predict(sim)

    return aff.labels_, aff.cluster_centers_indices_

# Distribution-based clustering


# Centroid-based clustering
# K-means makes the assumptions that all clusters are convex

def k_means(vecs, n_clusters):
    '''
        Centroid-based clustering.

        Params:
        vecs: Document vectors
        n_clusters: Number of clusters

        returns: labels, center_indices
    '''
    
    km = KMeans(n_clusters=n_clusters)

    km.fit(vecs)

    return km.labels_, km.cluster_centers_

def db_scan(sim, threshold, metric, algorithm):
    '''
        Density based clustering method.

        Params:
        sim: similarity matrix
        threshold: maximum distance between two samples
        metric: http://scikit-learn.org/stable/modules/
        classes.html#module-sklearn.metrics.cluster
        algorithm: 'auto', 'ball_tree', 'kd_tree', 'brute'

        returns: labels
    '''
    db = DBSCAN(eps=threshold, algorithm=algorithm, metric=metric)

    db.fit_predict(sim)

    return db.labels_


def hierarchical_clustering(vecs, method, metric,
                            cluster_criterion, cluster_threshold):
    '''
        Connectivity-based clustering.
        Connects node bottom-up by similarity

        sim: similarity matrix
        method: 'ward', 'single', 'complete', 'average', 'weighted'
                'centroid', 'median'
        metric: 'euclidean', 'cosine', 'minkowski', 'cityblock',
                'seuclidean', 'sqeuclidean', ...
        cluster_criterion: 'distance' or 'maxclust'
        cluster_threshold: distance -> observations in each flat cluster
                            have no greater a cophenetic distance than t
                           maxclust -> the cophenetic distance between any
                                two original observations in the same flat
                                cluster is no more than r and no more than
                                t flat clusters are formed

        returns: link_matrix, labels
    '''

    # Compute linkage
    link_matrix = linkage(vecs, method, metric)

    # cluster
    labels = fcluster(
        link_matrix, cluster_threshold, criterion=cluster_criterion)

    return link_matrix, labels
