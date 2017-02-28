import django
django.setup()

import numpy as np
import pandas as pd
from textblob import TextBlob

from scope.models import Customer, Article, Source
from curate.models import Curate_Query, Article_Curate_Query
from curate.models import Curate_Customer

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.lsi as lsi
import scope.methods.semantics.word_vector as word_vector
from scope.methods.learning import binary_classifier
from scope.methods.graphs import clustering_methods
from scope.methods.graphs import selection_methods
import curate.methods.tests as tests

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity, rbf_kernel

from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import to_tree
from scipy.spatial.distance import pdist, squareform

from sklearn.cluster import AgglomerativeClustering

# initializations
customer_key = "neuland_herzer"
language = "eng"

db_articles = []
threshold = 0.0
wv_language_dict = {
    'ger': 'de',
    'eng': 'en',
}
lsi_language_dict = {
    'ger': 'german',
    'eng': 'english',
}
wv_model = word_vector.Model(wv_language_dict[language])
classifier = binary_classifier.binary_classifier(
    wv_model.pipeline, customer_key)

# GET DATA
print "GET DATA"
db_articles = []
labels = []

data = pd.read_csv("clustering_small.csv", encoding="utf-8")

# rename labels
unique_labels = np.unique(data.label)
for i in range(1, len(unique_labels)+1):
    data.ix[data.label == unique_labels[i-1], "label"] = i

for a in data.iterrows():
    source = Source.objects.create(url=a[1]['url'][0:199], name=a[1]['url'][0:199])

    art = Article.objects.create(
        title=a[1]['title'],
        url=a[1]['url'],
        source=source,
        body=a[1]['body'],
        images=a[1]['image'],
        pubdate=a[1]['date'])

    db_articles.append(art)
    labels.append(a[1]["label"])

labels = np.array(labels)

print "articles:"
print len(db_articles)

# CLASSIFY
print "CLASSIFY"
min_count = 100
classifier_type = "none"  # none, nn300

if classifier_type == "nn300":
    filtered_articles = classifier.classify_by_count(
        db_articles, min_count)
else:
    print "no classifier selected"
    filtered_articles = db_articles

print "articles after classification"
print len(filtered_articles)

# semantic analysis
print "SEMANTIC ANALYSIS"
lsi_dim = 20

pre = preprocess.PreProcessing(lsi_language_dict[language])
lsi_model = lsi.Model()

vecs = pre.stemm([a.body for a in filtered_articles])
lsi_model.compute(vecs, lsi_dim)

sim = lsi_model.similarity()

# test three different dim reduction methods
vectorizer = TfidfVectorizer(
    sublinear_tf=True, stop_words='english', max_df=0.9)
tfidf = vectorizer.fit_transform([" ".join(TextBlob(a.body).noun_phrases) for a in filtered_articles])

# similarities
svd = TruncatedSVD(n_components=10, random_state=1).fit_transform(tfidf)
sim_svd = cosine_similarity(svd)

# clustering
print "CLUSTERING"
print "test ER as validation field"

# params
params_custom = [[0.001, 0.45, 0.001], [1, 0.01, 1, 15]]
params_svd = [[0.6, 0.9, 0.001], [1, 0.01, 1, 15]]

# used params
size_bound = [2, 18]
test = tests.Curate_Test("clusters").test

used_sim = sim_svd
used_params = params_svd

# custom
selection_custom, threshold = selection_methods.on_average_clustering_test(
    filtered_articles, size_bound, sim, params_custom, test)

labels_custom = clustering_methods.sim_based_threshold(used_sim, threshold)
center_indices_custom = [i[0] for i in selection_custom['articles']]

selected_articles_custom = [
    filtered_articles[i] for i in center_indices_custom]

print "custom"
print clustering_methods.internal_measure(svd, labels_custom)

# affinity
labels_affinity, center_indices_affinity = clustering_methods.affinity_propagation(used_sim)

selected_articles_affinity = np.array(filtered_articles)[
    center_indices_affinity]

print "affinity"
print clustering_methods.internal_measure(svd, labels_affinity)

# gauss
labels_gauss = clustering_methods.bayes_gauss_mix(svd, components=10)

print "gauss"
print clustering_methods.internal_measure(svd, labels_gauss)

# hierachical
links_hc_ward, labels_hc_ward = clustering_methods.hierarchical_clustering(svd, "ward", "euclidean", "maxclust", 16)

print "hc maxclust"
print clustering_methods.internal_measure(svd, labels_hc_ward)

links_hc_ward_dist, labels_hc_ward_dist = clustering_methods.hierarchical_clustering(svd, "ward", "euclidean", "distance", 0.40)

print "hc distance"
print clustering_methods.internal_measure(svd, labels_hc_ward_dist)

links_ward = linkage(svd, "ward", "euclidean")
links_cos = linkage(svd, "average", "cosine")

# hc merge function
ward_tree = to_tree(links_ward)
cos_tree = to_tree(links_cos)

# tree.pre_order() gives original indicies
# tree.dist gives distance of current index
# tree.count gives leave nodes below current point

max_clust = 12

# Subtree
sub = ward_tree.left.pre_order()

# All distances within the subtree
distance_vector = pdist(svd[sub])

# convert to squareform
distance_matrix = squareform(distance_vector)

# Get element with lowest mean distance
center = np.mean(distance_matrix, axis=1).argmin()
center_index = sub[center]
