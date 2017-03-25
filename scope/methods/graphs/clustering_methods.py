from sklearn.cluster import AffinityPropagation, DBSCAN
from sklearn.cluster import KMeans

from sklearn.mixture import GaussianMixture, BayesianGaussianMixture
from sklearn.metrics import silhouette_score

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

    return labels.astype(int)

def affinity_propagation(sim, preference=None):
    '''
        sim: similarity matrix
        preference: influences the number of clusters

        returns: labels, center_indices
    '''
    aff = AffinityPropagation(preference=preference)

    aff.fit_predict(sim)

    return aff.labels_, aff.cluster_centers_indices_

# Distribution-based clustering

def gauss_mix_test(vecs, params):
    '''
        vecs: document vectors
        params: list of component values to test [from, to , step]

        returns: best clustering
    '''

    out = []
    score = 0

    for s in np.arange(params[0], params[1], params[2]):
        gmm = GaussianMixture(n_components=s).fit(vecs)
        labels = gmm.predict(vecs)

        # new_score = silhouette_score(vecs, labels)
        new_score = calinski_harabaz_score(vecs, labels)

        if new_score > score:
            out = labels
            score = new_score

    return out

def gauss_search(vecs, components):
    '''
        vecs: document vectors
        components: Array with component numbers

        returns: labels, probas
    '''
    best_score = np.Infinity
    best_gmm = []

    scores = []

    # Go over all component numbers
    for component in components:
        mean_score = np.zeros(5)
        # Compute 5 times the BIC score and take the average
        for idx in range(0, len(mean_score)):
            gmm = GaussianMixture(n_components=component).fit(vecs)

            score = gmm.bic(vecs)
            mean_score[idx] = score

        scores.append({"comp": component, "score": mean_score.mean()})

    # Select the top 5 components numbers
    scores.sort(key=lambda x: x["score"], reverse=False)
    top = scores[0:5]

    # Compute the AIC for the top 5 and select the best model
    for row in top:
        mean_score = np.zeros(5)
        # Compute 5 times the AIC score and take the average
        for idx in range(0, len(mean_score)):
            gmm = GaussianMixture(n_components=row["comp"]).fit(vecs)
            score = gmm.aic(vecs)

            mean_score[idx] = score

        if mean_score.mean() < best_score:
            best_score = score
            best_gmm = gmm

    return best_gmm.predict(vecs), best_gmm.predict_proba(vecs)

def gauss_mix(vecs, components):
    '''
        vecs: document vectors
        compnents: number of components

        returns: labels
    '''
    gmm = GaussianMixture(n_components=components).fit(vecs)

    return gmm.predict(vecs)

def gauss_proba(vecs, components):
    '''
        vecs: document vectors
        compnents: number of components

        returns: labels
    '''
    gmm = GaussianMixture(n_components=components).fit(vecs)

    return gmm.predict_proba(vecs)


def bayes_gauss_mix(vecs, components):
    '''
        vecs: document vectors
        components: number of components

        returns: labels
    '''
    gmm = BayesianGaussianMixture(n_components=components).fit(vecs)

    return gmm.predict(vecs)


def bayes_gauss_proba(vecs, components):
    '''
        vecs: document vectors
        components: number of components

        returns: labels
    '''
    gmm = BayesianGaussianMixture(n_components=components).fit(vecs)

    return gmm.predict_proba(vecs)

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
