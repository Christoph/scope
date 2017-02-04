import django
django.setup()

import numpy as np

from scope.models import Customer
from curate.models import Curate_Query, Article_Curate_Query
from curate.models import Curate_Customer

import scope.methods.semantics.preprocess as preprocess
import scope.methods.semantics.lsi as lsi
import scope.methods.semantics.word_vector as word_vector
from scope.methods.learning import binary_classifier
from scope.methods.graphs import clustering_methods
from scope.methods.graphs import selection_methods
import curate.methods.tests as tests

# PARAMS
# general
customer_key = "neuland_herzer"
language = "eng"

# classifier
classifier_type = "nn300"  # none, nn300

# nn300
min_count = 100

# semantics
semantic_model = "lsi"  # lsi, wv

# clustering
clustering_type = "affinity"  # none, custom, affinity

# custom
size_bound = [2, 18]
lsi_dim = 20
params_global = {"threshold": 0.12}
test = tests.Curate_Test("clusters").test
params_lsi = [[0.001, 0.5, 0.001], [1, 0.01, 1, 15]]
params_wv = [[0.08, 0.2,  0.0001], [1, 0.01, 1, 15]]

# affinity
# no params

# kmeans
n_clusters = 8

# initializations
db_articles = []
vecs = []
sim = []
labels = []
selection = []
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

# get data from db
print "GET DATA"
customer = Customer.objects.get(
    customer_key=customer_key)
curate_customer = Curate_Customer.objects.get(
    customer=customer)
query = Curate_Query.objects.filter(
    curate_customer=curate_customer).order_by("pk").reverse()[0]
article_query_instances = Article_Curate_Query.objects.filter(
    curate_query=query)
for i in article_query_instances:
    i.rank = 0
    i.save()

all_articles = [i.article for i in article_query_instances]

bad_sources = curate_customer.bad_source.all()

# check if duplicate titles exist and remove them
titles = [a.title for a in all_articles]
u, indices = np.unique(titles, return_index=True)
all_articles = np.array(all_articles)[indices]
all_articles = all_articles.tolist()

for a in all_articles:
    if a.source not in bad_sources:
        db_articles.append(a)

print "articles:"
print len(db_articles)

words = sum([len(i.body) for i in db_articles])

print "CLASSIFY"

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

if semantic_model == "lsi":
    pre = preprocess.PreProcessing(lsi_language_dict[language])
    lsi_model = lsi.Model()

    vecs = pre.stemm([a.body for a in filtered_articles])
    lsi_model.compute(vecs, lsi_dim)

    sim = lsi_model.similarity()
elif semantic_model == "wv":
    word_vector.Model(wv_language_dict[language])

    wv_model.load_data(filtered_articles)
    vecs = wv_model.document_vectors()
    sim = wv_model.similarity_matrix()
else:
    print "no valid semantic processing selected"

# clustering
print "CLUSTERING"

if clustering_type == "custom":
    if semantic_model == "lsi":
        selection, threshold = selection_methods.on_average_clustering_test(
            filtered_articles, size_bound, sim, params_lsi, test)

        labels = clustering_methods.sim_based_threshold(sim, threshold)

    if semantic_model == "wv":
        selection, threshold = selection_methods.on_average_clustering_test(
            filtered_articles, size_bound, sim, params_wv, test)

        labels = clustering_methods.sim_based_threshold(sim, threshold)

    selected_articles = [
        filtered_articles[i[0]] for i in selection['articles']]
elif clustering_type == "affinity":
    labels, center_indices = clustering_methods.affinity_propagation(sim)

    selected_articles = np.array(filtered_articles)[center_indices]
elif clustering_type == "kmeans":
    labels, center_indices = clustering_methods.k_means(vecs, n_clusters)

    selected_articles = np.array(filtered_articles)[center_indices]
else:
    print "no valid clustering selected"

# select articles
print "artilces count"
print len(selected_articles)

print "selected_articles"
for a in selected_articles:
    print a
