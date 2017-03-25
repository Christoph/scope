import django
django.setup()

import numpy as np
import pandas as pd
from textblob import TextBlob
import re

from scope.models import Customer, Article, Source
from curate.models import Curate_Query, Article_Curate_Query
from curate.models import Curate_Customer

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.lsi as lsi
import scope.methods.semantics.word_vector as word_vector
# from scope.methods.learning import binary_classifier
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
from sklearn import metrics

from gensim.models import Word2Vec

reload(clustering_methods)

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
# wv_model = word_vector.Model(wv_language_dict[language])
# classifier = binary_classifier.binary_classifier(
#     wv_model.pipeline, customer_key)

# model = Word2Vec.load_word2vec_format('datasets/GoogleNews-vectors-negative300.bin', binary=True)

# GET DATA
print "GET DATA"
db_articles = []
labels = []


data = pd.read_csv("clustering_24.csv", encoding="utf-8")

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

filtered_articles = db_articles

# semantic analysis
print "SEMANTIC ANALYSIS"

texts = [TextBlob(a.body) for a in filtered_articles]

tags = [TextBlob(a.body).tags for a in filtered_articles]

nnp = [[t[0] for t in doc if t[1] in ["NNP", "NNPS"]] for doc in tags]

parsed = [TextBlob(a.body).parse().split(" ") for a in filtered_articles]

text_np = []
text_vp = []
text_pp = []

for doc in parsed:
    t_np = []
    t_vp = []
    t_pp = []
    for word in doc:
        if word.find("NP") >= 0:
            t_np.append(re.sub("/.*", "", word))
        if word.find("VP") >= 0:
            t_vp.append(re.sub("/.*", "", word))
        if word.find("PNP") >= 0:
            t_pp.append(re.sub("/.*", "", word))
    text_np.append(" ".join(t_np))
    text_vp.append(" ".join(t_vp))
    text_pp.append(" ".join(t_pp))

# # Replace dollar
# replaced = [re.sub("[\$][0-9]\d*(\.\d+)?(?![\d.])( \willion)", "CURRENCY", t.body) for t in filtered_articles]
#
# # Replace euro/pounds
# replaced = [re.sub("[0-9]\d*(\.\d+)?(?![\d.])( \willion)* [euros|pounds]+", "CURRENCY", t) for t in replaced]
#
# # Replace dates
# replaced = [re.sub("\s[12][0-9]{3}\\b", " DATE", t) for t in replaced]
#
# # Replace number
# replaced = [re.sub("[+-.,]?[0-9]+", "NUMBER", t) for t in replaced]

# Possible texts for futher use
text_nnp = [" ".join(t) for t in nnp]
text = [a.body for a in filtered_articles]

noun_chunks = [" ".join(a.noun_phrases) for a in texts]

# Used text for further steps
used = text_np

# test three different dim reduction methods
vectorizer = TfidfVectorizer(
    sublinear_tf=True, stop_words='english', strip_accents="unicode", max_df=0.5, binary=False)
tfidf = vectorizer.fit_transform(used)

print len(vectorizer.vocabulary_)

# similarities
svd = TruncatedSVD(n_components=20, random_state=1).fit_transform(tfidf)
sim_svd = cosine_similarity(svd)

# clustering
print "CLUSTERING"
print "test ER as validation field"

# affinity
labels_affinity, center_indices_affinity = clustering_methods.affinity_propagation(sim_svd)

selected_articles_affinity = np.array(filtered_articles)[
    center_indices_affinity]

# gauss
labels_gauss, proba_gauss = clustering_methods.gauss_search(svd, range(10, 20))

labels_gauss_classic = clustering_methods.gauss_mix(svd, components=30)
proba_gauss_classic = clustering_methods.gauss_proba(svd, components=16)

# hierachical
links_hc_ward_dist, labels_hc_ward_dist = clustering_methods.hierarchical_clustering(svd, "ward", "euclidean", "distance", 0.8)

# EVALUATION

print "For small n (> 1000) and number of clusters < 10 any measure is good."
print "If thats not satisfied - use adjusted scores."

print ""
print "Number of Clusters"
print "ground truth: " + str(len(np.unique(labels)))
print "hc distance: " + str(len(np.unique(labels_hc_ward_dist)))
print "gauss: " + str(len(np.unique(labels_gauss)))
print "gauss_classic: " + str(len(np.unique(labels_gauss_classic)))
print "affinity: " + str(len(np.unique(labels_affinity)))


# print ""
# print "silhouette_score: higher is better"
# print "Internal measure which doesnt uses ground truth labels and is higher for better defined clusters"
# print "hc distance: " + str(metrics.silhouette_score(svd, labels_hc_ward_dist))
# print "gauss: " + str(metrics.silhouette_score(svd, labels_gauss))
# print "gauss_classic: " + str(metrics.silhouette_score(svd, labels_gauss_classic))
# print "affinity: " + str(metrics.silhouette_score(svd, labels_affinity))


# print ""
# print "Adjusted Rand Score: [-1, 1] and 0 means random"
# print "adjusted Rand index is a function that measures the similarity of the two assignments, ignoring permutations and with chance normalization"
# print "hc distance: " + str(metrics.adjusted_rand_score(labels, labels_hc_ward_dist))
# print "gauss: " + str(metrics.adjusted_rand_score(labels, labels_gauss))
# print "gauss_classic: " + str(metrics.adjusted_rand_score(labels, labels_gauss_classic))
# print "affinity: " + str(metrics.adjusted_rand_score(labels, labels_affinity))


print ""
print "Nomalized MI: [0,1] and 1 is perfect match"
print "Mutual Information is a function that measures the agreement of the two assignments, ignoring permutations"
print "hc distance: " + str(metrics.normalized_mutual_info_score(labels, labels_hc_ward_dist))
print "gauss: " + str(metrics.normalized_mutual_info_score(labels, labels_gauss))
print "gauss_classic: " + str(metrics.normalized_mutual_info_score(labels, labels_gauss_classic))
print "affinity: " + str(metrics.normalized_mutual_info_score(labels, labels_affinity))


# print ""
# print "Adjusted MI to account for chance: [0,1] and 1 is perfect match"
# print "hc distance: " + str(metrics.adjusted_mutual_info_score(labels, labels_hc_ward_dist))
# print "gauss: " + str(metrics.adjusted_mutual_info_score(labels, labels_gauss))
# print "gauss_classic: " + str(metrics.adjusted_mutual_info_score(labels, labels_gauss_classic))
# print "affinity: " + str(metrics.adjusted_mutual_info_score(labels, labels_affinity))


# print ""
# print "V-Measure: [0,1] and 1 is perfect match"
# print "The V-measure is the harmonic mean between homogeneity and completeness"
# print "hc distance: " + str(metrics.v_measure_score(labels, labels_hc_ward_dist))
# print "gauss: " + str(metrics.v_measure_score(labels, labels_gauss))
# print "gauss_classic: " + str(metrics.v_measure_score(labels, labels_gauss_classic))
# print "affinity: " + str(metrics.v_measure_score(labels, labels_affinity))

print ""
print "Fowlkes-Mallows scores: [0,1] and 1 means good correlation between clusters"
print "The Fowlkes-Mallows index (FMI) is defined as the geometric mean between of the precision and recall."
print "hc distance: " + str(metrics.fowlkes_mallows_score(labels, labels_hc_ward_dist))
print "gauss: " + str(metrics.fowlkes_mallows_score(labels, labels_gauss))
print "gauss_classic: " + str(metrics.fowlkes_mallows_score(labels, labels_gauss_classic))
print "affinity: " + str(metrics.fowlkes_mallows_score(labels, labels_affinity))
