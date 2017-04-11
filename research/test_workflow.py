import django
django.setup()

import numpy as np
import pandas as pd
from textblob import TextBlob
import re

from scope.models import Customer, Article, Source
from curate.models import Curate_Query, Article_Curate_Query
from curate.models import Curate_Customer

from scope.methods.semantics import stopwords
import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.lsi as lsi
from scope.methods.graphs import selection_methods
import curate.methods.tests as tests

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.lsi as lsi
import scope.methods.semantics.word_vector as word_vector
from scope.methods.semantics import embedding
# from scope.methods.learning import binary_classifier
from research.clustering import clustering_methods
from scope.methods.graphs import selection_methods
import curate.methods.tests as tests

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity, rbf_kernel
from sklearn.preprocessing import MinMaxScaler

from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import to_tree
from scipy.spatial.distance import pdist, squareform

from sklearn.cluster import AgglomerativeClustering
from sklearn import metrics

import spacy
import nltk

nlp = spacy.load("en")

reload(clustering_methods)
reload(embedding)

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


data = pd.read_csv("clustering_16.csv", encoding="utf-8")

# rename labels
unique_labels = np.unique(data.label)
for i in range(1, len(unique_labels) + 1):
    data.ix[data.label == unique_labels[i - 1], "label"] = i

for a in data.iterrows():
    source = Source.objects.create(
        url=a[1]['url'][0:199], name=a[1]['url'][0:199])

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

lsi_dim = 20

pre = preprocess.PreProcessing(lsi_language_dict[language])
lsi_model = lsi.Model()

vecs = pre.stemm([a.body for a in filtered_articles])
lsi_model.compute(vecs, lsi_dim)

sim_old = lsi_model.similarity()

texts = [TextBlob(a.body) for a in filtered_articles]

tags = [TextBlob(a.body).tags for a in filtered_articles]

parsed = [TextBlob(a.body).parse().split(" ") for a in filtered_articles]

text_np = []

for doc in parsed:
    t_np = []

    for word in doc:
        if word.find("B-NP") >= 0 or word.find("I-NP") >= 0:
            t_np.append(re.sub("/.*", "", word))

    text_np.append(" ".join(t_np))


docs = [nlp(a.body) for a in filtered_articles]

dep_labels = ["acomp", "ccomp", "pcomp", "xcomp", "csubj",
              "csubjpass", "dobj", "nsubj", "nsubjpass", "pobj"]

used_deps = ["acomp", "ccomp", "pcomp", "xcomp", "relcl", "conj"]
used_tags = ["NN", "NNS", "NNP", "NNPS"]

text_nnvb = []
text_lemma = []
text_checked = []

for doc in docs:
    temp = []
    lemma = []
    lemma_checked = []

    for sent in doc.sents:
        for t in sent:
            # if t.tag_ in used_tags or t.dep_ in used_deps:
            # if t.tag_.find("NN") >= 0 or t.dep_.find("comp") >= 0:
            if t.tag_.find("NN") >= 0:
                temp.append(t.lemma_)

            if t.like_email:
                lemma_checked.append("-EMAIL-")
            elif t.like_num:
                lemma_checked.append("-NUMBER-")
            elif t.like_url:
                lemma_checked.append("-URL-")
            else:
                lemma_checked.append(t.lemma_)

            lemma.append(t.lemma_)

    text_nnvb.append(" ".join(temp))
    text_lemma.append(" ".join(lemma))
    text_checked.append(" ".join(lemma_checked))


# Replace dollar
replaced = [re.sub("[\$]?[0-9]\d*(\.\d+)?(?![\d.])( \willion)",
                   "-CURRENCY-", t) for t in text_lemma]

# Replace euro/pounds
replaced = [re.sub("[0-9]\d*(\.\d+)?(?![\d.])( \willion)? (euros|pounds)+",
                   "-CURRENCY-", t) for t in replaced]

# Replace dates
replaced = [re.sub("\s[12][0-9]{3}\\b", " -DATE-", t) for t in replaced]

# Replace number
replaced = [re.sub("[+-.,]?[0-9.,]{2,}", " -NUMBER-", t) for t in replaced]

# Replace url
replaced = [re.sub('http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[:/?#\[\]@+\-\._~=]|[!$&\'()*+,;=]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                   " -URL-", t) for t in replaced]

replaced = [re.sub("[a-z]*\.[a-z]{2,3}", " -URL-", t) for t in replaced]

params_custom = [[0.001, 0.45, 0.001], [1, 0.01, 1, 15]]

size_bound = [2, 18]
test = tests.Curate_Test("clusters").test

# Possible texts for futher use
text = [a.body for a in filtered_articles]

noun_chunks = [" ".join(a.noun_phrases) for a in texts]

# Used text for further steps
used = text_nnvb

# test three different dim reduction methods
vectorizer = TfidfVectorizer(
    sublinear_tf=True, stop_words=stopwords.EN, strip_accents="unicode", binary=False)
tfidf = vectorizer.fit_transform(used)

print len(vectorizer.vocabulary_)

# similarities
svd = TruncatedSVD(n_components=18, random_state=1).fit_transform(tfidf)
sim_svd = cosine_similarity(svd)

# Word2Vec
wv = []

docs = [nlp(a) for a in used]
for doc in docs:
    temp = []

    for t in doc:
        temp.append(t.vector)

    wv.append(np.array(temp).mean(axis=0))

sim_wv = cosine_similarity(wv)

used_vecs = svd
used_sim = sim_svd


contexts = ["opel"]

hal, vocab = embedding.HAL(replaced)

hal_grammar, vocab_grammar, context_grammar = embedding.HAL_context_grammar(
    [a.body for a in filtered_articles], contexts, nlp)

# SVD doesnt work with the pandas output
if hal_grammar.shape[0] > 1000:
    svd_grammar = TruncatedSVD(
        n_components=100, random_state=1).fit_transform(hal_grammar)
else:
    svd_grammar = hal_grammar

sim_grammar = cosine_similarity(svd_grammar)

# Get context row
context_row = sim_grammar[vocab_grammar[contexts[0]]].copy()

# Remove self similarity and rescale
min_max_scaler = MinMaxScaler()

context_row[context_row >= 1.] = context_row.min() - 0.001
rescaled_grammar = min_max_scaler.fit_transform(context_row.reshape(-1, 1))

# Get similarity list
grammar_similarities = pd.DataFrame(
    {'word': sorted(vocab_grammar, key=vocab_grammar.get),
     'similarity': rescaled_grammar.flatten()
     })
grammar_similarities = grammar_similarities.sort_values(
    "similarity", ascending=False)

# clustering
print "CLUSTERING"
print "test ER as validation field"

# custom
selection_custom, threshold = selection_methods.on_average_clustering_test(
    filtered_articles, size_bound, sim_old, params_custom, test)

labels_custom = clustering_methods.sim_based_threshold(sim_old, threshold)
center_indices_custom = [i[0] for i in selection_custom['articles']]

selected_articles_custom = [filtered_articles[i]
                            for i in center_indices_custom]

# affinity
'''
Very robust when changing input and embedding sizes!
Provides central articles.

Tends to create too much clusters
'''
labels_affinity, center_indices_affinity = clustering_methods.affinity_propagation(
    used_sim)

selected_articles_affinity = np.array(filtered_articles)[
    center_indices_affinity]

# gauss
'''
Gauss seems to use as much components as possible if enough iterations and so on are given. That means its hard to predict the number of clusters with gaussian mixture methods.

Bayes Gauss seems to be the best choice from the gaussianmethods.
The "grid-search" method seem to perform worse due to the fact that
a Internal measure needs to be evaluated, and that measure doenst seem to work proberly. The search methods also thend to use the maximum number of components which reduces it to bayes with a good maximum.
'''
# BEST
# text_np, emb dim 20, comp 20-30
labels_gauss = clustering_methods.bayes_gauss_mix(used_vecs, components=20)

# hierachical
'''
Provide very good aproximations and any number of custers can be extracted from the linkage matrix.
'''

# good combinations

# input:24, text_np, ndim=20, ward + euclidean, dist 0.75 = MI: 0.80, n = 25
# input:16, text_np, ndim=20, ward + euclidean, dist 0.75 = MI: 0.77, n = 24

# ndim=10, complete + cosine, dist 0.27 = MI 0.76, n=26

# BEST HIERARCHICAL
# text_np, embedding dim 20, complete + cosine, dist 0.6
# input:24, text_np, ndim=20, complete + cosine, dist 0.6 = MI 0.85, n=22
# input:16, text_np, ndim=20, complete + cosine, dist 0.6 = MI 0.92, n=21

# ndim=50, complete + cosine, dist 1 = MI 0.83, n=26

# ndim=10, complete + sqeuclidean, dist 0.05 = MI: 0.77, n=25
# input:24, text_np, ndim=20, complete + sqeuclidean, dist 0.25 = MI: 0.78, n=25
# ndim=50, complete + sqeuclidean, dist 1 = MI: 0.77, n=28

# ndim = 10, weighted + euclidean, dist 0.2 = MI: 0.75, n=21
# ndim = 20, weighted + euclidean, dist 0.4 = MI: 0.82, n=27
# ndim = 50, weighted + euclidean, dist 1 = MI: 0.73, n=24

links_hc_ward_dist, labels_hc_dist = clustering_methods.hierarchical_clustering(
    used_vecs, "complete", "cosine", "distance", 0.6)

links_hc_clust, labels_hc_clust = clustering_methods.hierarchical_clustering(
    used_vecs, "ward", "euclidean", "maxclust", 16)

# labels_dbscan = clustering_methods.db_search(used_sim, used_vecs, np.arange(0.5, 3, 0.1))

# EVALUATION

print "For small n (> 1000) and number of clusters < 10 any measure is good."
print "If thats not satisfied - use adjusted scores."

print ""
print "Number of Clusters"
print "ground truth: " + str(len(np.unique(labels)))
print "custom: " + str(len(np.unique(labels_custom)))
print "hc distance: " + str(len(np.unique(labels_hc_dist)))
print "hc clust: " + str(len(np.unique(labels_hc_clust)))
print "gauss: " + str(len(np.unique(labels_gauss)))
# print "db scan: " + str(len(np.unique(labels_dbscan)))
print "affinity: " + str(len(np.unique(labels_affinity)))


print ""
print "silhouette_score: higher is better"
print "Internal measure which doesnt uses ground truth labels and is higher for better defined clusters"
print "custom: " + str(metrics.silhouette_score(used_vecs, labels_custom))
print "hc distance: " + str(metrics.silhouette_score(used_vecs, labels_hc_dist))
print "hc clust: " + str(metrics.silhouette_score(used_vecs, labels_hc_clust))
print "gauss: " + str(metrics.silhouette_score(used_vecs, labels_gauss))
# print "db_scan: " + str(metrics.silhouette_score(used_vecs, labels_dbscan))
print "affinity: " + str(metrics.silhouette_score(used_vecs, labels_affinity))


# print ""
# print "Adjusted Rand Score: [-1, 1] and 0 means random"
# print "adjusted Rand index is a function that measures the similarity of the two assignments, ignoring permutations and with chance normalization"
# print "hc distance: " + str(metrics.adjusted_rand_score(labels, labels_hc_dist))
# print "gauss: " + str(metrics.adjusted_rand_score(labels, labels_gauss))
# print "gauss_classic: " + str(metrics.adjusted_rand_score(labels, labels_gauss_classic))
# print "affinity: " + str(metrics.adjusted_rand_score(labels,
# labels_affinity))


print ""
print "Nomalized MI: [0,1] and 1 is perfect match"
print "Mutual Information is a function that measures the agreement of the two assignments, ignoring permutations"
print "custom: " + str(metrics.normalized_mutual_info_score(labels, labels_custom))
print "hc distance: " + str(metrics.normalized_mutual_info_score(labels, labels_hc_dist))
print "hc clust: " + str(metrics.normalized_mutual_info_score(labels, labels_hc_clust))
print "gauss: " + str(metrics.normalized_mutual_info_score(labels, labels_gauss))
# print "db_scan: " + str(metrics.normalized_mutual_info_score(labels,
# labels_dbscan))
print "affinity: " + str(metrics.normalized_mutual_info_score(labels, labels_affinity))


# print ""
# print "Adjusted MI to account for chance: [0,1] and 1 is perfect match"
# print "hc distance: " + str(metrics.adjusted_mutual_info_score(labels, labels_hc_dist))
# print "gauss: " + str(metrics.adjusted_mutual_info_score(labels, labels_gauss))
# print "gauss_classic: " + str(metrics.adjusted_mutual_info_score(labels, labels_gauss_classic))
# print "affinity: " + str(metrics.adjusted_mutual_info_score(labels,
# labels_affinity))


# print ""
# print "V-Measure: [0,1] and 1 is perfect match"
# print "The V-measure is the harmonic mean between homogeneity and completeness"
# print "hc distance: " + str(metrics.v_measure_score(labels, labels_hc_dist))
# print "gauss: " + str(metrics.v_measure_score(labels, labels_gauss))
# print "gauss_classic: " + str(metrics.v_measure_score(labels, labels_gauss_classic))
# print "affinity: " + str(metrics.v_measure_score(labels, labels_affinity))

# print ""
# print "Fowlkes-Mallows scores: [0,1] and 1 means good correlation between clusters"
# print "The Fowlkes-Mallows index (FMI) is defined as the geometric mean between of the precision and recall."
# print "hc distance: " + str(metrics.fowlkes_mallows_score(labels, labels_hc_dist))
# print "gauss: " + str(metrics.fowlkes_mallows_score(labels, labels_gauss))
# print "gauss_classic: " + str(metrics.fowlkes_mallows_score(labels, labels_gauss_classic))
# print "affinity: " + str(metrics.fowlkes_mallows_score(labels,
# labels_affinity))
