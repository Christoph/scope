''' Used Clustering Methods '''

from collections import defaultdict

from sklearn.cluster import AffinityPropagation
from sklearn.mixture import BayesianGaussianMixture

import scipy.cluster.hierarchy as hierarchical_clustering
from scipy.spatial.distance import pdist, squareform

import numpy as np


def get_clustering(articles, sim, vecs, max_clusters, min_clusters):
    '''
        Returns clusters.
    '''

    labels_affinity, center_indices_affinity = affinity_propagation(sim)
    len_aff = len(np.unique(labels_affinity))
    print("Affinity clusters: "+str(len_aff))
    linkage_matrix = hc_create_linkage(vecs)
    labels_hc = hc_cluster_by_distance(linkage_matrix, 0.6)
    len_hc = len(np.unique(labels_hc))
    print("HC clusters: "+str(len_hc))
    labels_gauss, probas_gauss = gauss(vecs, int(max_clusters*1.3))
    len_gauss = len(np.unique(labels_gauss))
    print("Gauss clusters: "+str(len_gauss))

    print("Max Clusters:", max_clusters)
    print("Min Clusters:", min_clusters)

    if len_aff <= max_clusters and len_aff >= min_clusters:
        print("Affinity Propagation is used.")
        selected_articles = np.array(articles)[
            center_indices_affinity]
        cluster_articles = get_clusters(
            articles, vecs, selected_articles, labels_affinity)
    elif len_hc <= max_clusters and len_hc >= min_clusters:
        print("HC with distance measure is used.")
        selected_articles = compute_central_articles(
            articles, vecs, labels_hc)
        cluster_articles = get_clusters(
            articles, vecs, selected_articles, labels_hc)
    elif len_gauss <= max_clusters and len_gauss >= min_clusters:
        print("Gaussian Clustering is used.")
        selected_articles = compute_central_articles(
            articles, vecs, labels_gauss)
        cluster_articles = get_clusters(
            articles, vecs, selected_articles, labels_gauss)
    else:
        print("Fallback to HC with max cluster size is used.")
        labels_hc_clust = hc_cluster_by_maxclust(linkage_matrix, max_clusters)
        selected_articles = compute_central_articles(
            articles, vecs, labels_hc_clust)
        cluster_articles = get_clusters(
            articles, vecs, selected_articles, labels_hc_clust)

    return cluster_articles


def get_central_articles(cluster_articles, n_center):
    if len(cluster_articles) <= n_center:
        return sorted(cluster_articles, key=lambda c: len(cluster_articles[c]), reverse=True)

    return sorted(cluster_articles, key=lambda c: len(cluster_articles[c]), reverse=True)[:n_center]


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
    for key in list(graph.keys()):
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


def gauss(vecs, max_components):
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
    try:
        linkage_matrix = hierarchical_clustering.linkage(vecs, "complete", "cosine")
    except ValueError:
        print("Error using complete linkage -> Fallback to ward distance.")
        linkage_matrix = hierarchical_clustering.linkage(vecs)
        # linkage_matrix = hierarchical_clustering.linkage(vecs, "average", "cosine")

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


def get_clusters(articles, vecs, center_articles, labels):
    cluster_labels = np.unique(labels)
    clusters = []

    for l in cluster_labels:
        mask = labels == l
        cluster = np.array(articles)[mask]
        center = ""

        for c in cluster:
            if c in center_articles:
                center = c

        clusters.append((center, cluster))

    # clusters.sort(key=lambda x: len(x[1]), reverse=True)

    return dict(clusters)


def compute_central_articles(articles, vecs, labels):
    '''
        Returns central articles based on the minimum cosine distance.

        articles: List of article objects.
        vecs: Embedding vectors for articles.
        labels: Computed labels for articles.

        returns center_articles
    '''

    cluster_labels = np.unique(labels)
    center_articles = []

    for l in cluster_labels:
        mask = labels == l

        cluster = np.array(articles)[mask]
        distance_vector = pdist(vecs[mask], metric='cosine')

        # convert to squareform
        distance_matrix = squareform(distance_vector)

        center_index = np.mean(distance_matrix, axis=1).argmin()

        center_articles.append(cluster[center_index])

    return center_articles
