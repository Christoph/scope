from scipy.cluster.hierarchy import dendrogram, linkage
import numpy as np
from scope.methods.graphs import cluster_plot as plt
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances

from scipy.cluster.hierarchy import cophenet
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import fcluster

# Generate test data
np.random.seed(4711)  # for repeatability of this tutorial
a = np.random.multivariate_normal([10, 0], [[3, 1], [1, 4]], size=[100,])
b = np.random.multivariate_normal([0, 20], [[3, 1], [1, 4]], size=[50,])
X = np.concatenate((a, b),)

c = np.random.multivariate_normal([40, 40], [[20, 1], [1, 30]], size=[200,])
d = np.random.multivariate_normal([80, 80], [[30, 1], [1, 30]], size=[200,])
e = np.random.multivariate_normal([0, 100], [[100, 1], [1, 100]], size=[200,])
X2 = np.concatenate((X, c, d, e),)


# clustering

ward =  AgglomerativeClustering(n_clusters=4, linkage='ward')
ward.fit(X2)


# Z = linkage(X, 'average', 'cosine')
Z = linkage(X, 'ward', 'euclidean')
Z2 = linkage(X2, 'ward', 'euclidean')

# compares hierachical cluster with the actual pairwise distance
# closer to 1 means the clustering preserves the original distances
c, coph_dists = cophenet(Z, pdist(X, 'euclidean'))


clusters = fcluster(Z, 10, criterion='distance')
clusters_set = fcluster(Z2, 4, criterion='maxclust')
