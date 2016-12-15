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

wv = word_vector.Model("en")

# Generate test data
np.random.seed(4711)  # for repeatability of this tutorial
a = np.random.multivariate_normal([10, 0], [[3, 1], [1, 4]], size=[100,])
b = np.random.multivariate_normal([0, 20], [[3, 1], [1, 4]], size=[50,])
X = np.concatenate((a, b),)

c = np.random.multivariate_normal([40, 40], [[20, 1], [1, 30]], size=[200,])
d = np.random.multivariate_normal([80, 80], [[30, 1], [1, 30]], size=[200,])
e = np.random.multivariate_normal([0, 100], [[100, 1], [1, 100]], size=[200,])
X2 = np.concatenate((X, c, d, e),)

# Get data from json
with open('test/clustering/articles.json', 'r') as stream:
    data = json.load(stream)

articles = []
for obj in serializers.deserialize("json", data):
    articles.append(obj.object)

# Get semantic informations
wv.load_data(articles)
vec = wv.document_vectors()
sim = wv.similarity_matrix()

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
