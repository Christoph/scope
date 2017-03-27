''' Used Clustering Methods '''

from collections import defaultdict

from sklearn.cluster import AffinityPropagation
from sklearn.mixture import BayesianGaussianMixture

import scipy.cluster.hierarchy as hierarchical_clustering

import numpy as np


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

    return labels.astype(int)


def affinity_propagation(sim):
    '''
        sim: similarity matrix
        preference: influences the number of clusters

        returns: labels, center_indices
    '''
    aff = AffinityPropagation()

    aff.fit_predict(sim)

    return aff.labels_, aff.cluster_centers_indices_


def gauss_mix(vecs, max_components):
    '''
        vecs: document vectors
        max_components: maximum number of components

        returns: labels, probabilities
    '''
    gmm = BayesianGaussianMixture(n_components=max_components, max_iter=500, n_init=10).fit(vecs)

    return gmm.predict(vecs), gmm.predict_proba(vecs)


def hc_create_linkage(vecs):
    '''
        Connects node bottom-up by similarity

        vecs: Document vectors

        returns: linkage_matrix
    '''

    # Compute linkage
    linkage_matrix = hierarchical_clustering.linkage(vecs, "complete", "cosine")

    return linkage_matrix


def hc_cluster_by_distance(linkage_matrix, distance):
    '''
        Distance based clustering.
        Connects node bottom-up by similarity

        linkage_matrix: linkage matrix
        distance: observations in each flat cluster
                            have no greater a cophenetic distance than t


        returns: labels
    '''

    # cluster
    labels = hierarchical_clustering.fcluster(
        linkage_matrix, distance, criterion="distance")

    return labels


def hc_cluster_by_maxclust(linkage_matrix, n_clusters):
    '''
        MaxClust based clustering.
        Connects node bottom-up by similarity

        linkage_matrix: linkage matrix
        n_clusters:  the cophenetic distance between any
                            two original observations in the same flat
                            cluster is no more than r and no more than
                            t flat clusters are formed

        returns: labels
    '''

    # cluster
    labels = hierarchical_clustering.fcluster(
        linkage_matrix, n_clusters, criterion="maxclust")

    return labels
