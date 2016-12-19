from sklearn.cluster import AffinityPropagation, DBSCAN

from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster.hierarchy import cophenet
from scipy.cluster.hierarchy import fcluster

from scipy.spatial.distance import pdist

import numpy as np


def affinity_propagation(sim):
    '''
        sim: similarity matrix
        preference: influences the number of clusters

        returns: labels, center_indices
    '''
    aff = AffinityPropagation(affinity="precomputed")

    aff.fit_predict(sim)

    return aff.labels_, aff.cluster_centers_indices_


def db_scan(sim, threshold, metric, algorithm):
    '''
        sim: similarity matrix
        threshold: maximum distance between two samples
        metric: http://scikit-learn.org/stable/modules/
        classes.html#module-sklearn.metrics.cluster
        algorithm: 'auto', 'ball_tree', 'kd_tree', 'brute'

        returns: labels
    '''
    db = DBSCAN(sim, threshold=threshold, algorithm=algorithm, metric=metric)

    db.fit_predict(sim)

    return db.labels_


def hierarchical_clustering(vecs, method, metric,
                            cluster_criterion, cluster_threshold):
    '''
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
